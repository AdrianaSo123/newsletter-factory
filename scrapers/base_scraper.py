"""
Base scraper infrastructure with rate limiting, caching, and error handling
"""

import time
import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ScraperConfig:
    """Configuration for scraper behavior"""
    
    # Rate limiting
    REQUESTS_PER_MINUTE = 30
    DELAY_BETWEEN_REQUESTS = 2.0  # seconds
    
    # Caching
    CACHE_DIR = Path("cache")
    CACHE_EXPIRY_HOURS = 6  # How long cached data is valid
    
    # Retry policy
    MAX_RETRIES = 3
    RETRY_WAIT_MIN = 1  # seconds
    RETRY_WAIT_MAX = 10  # seconds
    
    # Request settings
    TIMEOUT = 30  # seconds
    VERIFY_SSL = True


class CacheManager:
    """Manages cached scraper data"""

    _GOOGLE_API_KEY_RE = re.compile(r"AIza[0-9A-Za-z_\-]{20,}")
    _SENSITIVE_KEY_RE = re.compile(r"(api[_-]?key|token|secret|bearer)", re.IGNORECASE)
    
    def __init__(self, cache_dir: Path = ScraperConfig.CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from URL and parameters"""
        cache_input = url
        if params:
            cache_input += json.dumps(params, sort_keys=True)
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path for cache file"""
        return self.cache_dir / f"{cache_key}.json"

    def _redact_secrets(self, value: Any) -> Any:
        """Best-effort redaction for secrets that can appear in scraped pages."""
        if isinstance(value, str):
            return self._GOOGLE_API_KEY_RE.sub("[REDACTED]", value)

        if isinstance(value, list):
            return [self._redact_secrets(v) for v in value]

        if isinstance(value, dict):
            redacted: Dict[Any, Any] = {}
            for k, v in value.items():
                if isinstance(k, str) and self._SENSITIVE_KEY_RE.search(k):
                    redacted[k] = "[REDACTED]"
                else:
                    redacted[k] = self._redact_secrets(v)
            return redacted

        return value
    
    def get(self, url: str, params: Optional[Dict] = None, 
            max_age_hours: int = ScraperConfig.CACHE_EXPIRY_HOURS) -> Optional[Dict]:
        """Retrieve cached data if valid"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached['timestamp'])
            age = datetime.now() - cached_time
            
            if age > timedelta(hours=max_age_hours):
                logging.info(f"Cache expired for {url}")
                return None
            
            logging.info(f"Cache hit for {url} (age: {age})")
            return cached['data']
        
        except Exception as e:
            logging.warning(f"Cache read error: {e}")
            return None
    
    def set(self, url: str, data: Any, params: Optional[Dict] = None):
        """Store data in cache"""
        cache_key = self._get_cache_key(url, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'params': params,
                'data': self._redact_secrets(data)
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            logging.info(f"Cached data for {url}")
        
        except Exception as e:
            logging.warning(f"Cache write error: {e}")
    
    def clear_expired(self, max_age_hours: int = ScraperConfig.CACHE_EXPIRY_HOURS):
        """Remove expired cache files"""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                cached_time = datetime.fromisoformat(cached['timestamp'])
                age = datetime.now() - cached_time
                
                if age > timedelta(hours=max_age_hours):
                    cache_file.unlink()
                    count += 1
            
            except Exception as e:
                logging.warning(f"Error clearing cache {cache_file}: {e}")
        
        logging.info(f"Cleared {count} expired cache files")
        return count


class RateLimiter:
    """Rate limiter for polite scraping"""
    
    def __init__(self, requests_per_minute: int = ScraperConfig.REQUESTS_PER_MINUTE):
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we need to wait
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest)
            
            if wait_time > 0:
                logging.info(f"Rate limit: waiting {wait_time:.2f}s")
                time.sleep(wait_time)
        
        self.request_times.append(now)


class BaseScraper(ABC):
    """
    Base class for all scrapers with common functionality:
    - Rate limiting
    - Caching
    - Error handling
    - Retry logic
    - User agent rotation
    """
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        self.cache = CacheManager() if use_cache else None
        self.rate_limiter = RateLimiter()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers with random user agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    @retry(
        stop=stop_after_attempt(ScraperConfig.MAX_RETRIES),
        wait=wait_exponential(
            min=ScraperConfig.RETRY_WAIT_MIN,
            max=ScraperConfig.RETRY_WAIT_MAX
        )
    )
    def _fetch_url(self, url: str, params: Optional[Dict] = None, 
                   use_cache: bool = True) -> str:
        """
        Fetch URL with caching, rate limiting, and retry logic
        
        Args:
            url: URL to fetch
            params: Query parameters
            use_cache: Whether to use cache
        
        Returns:
            HTML content
        """
        # Check cache first
        if use_cache and self.cache:
            cached_data = self.cache.get(url, params)
            if cached_data is not None:
                return cached_data
        
        # Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Make request
        self.logger.info(f"Fetching {url}")
        time.sleep(ScraperConfig.DELAY_BETWEEN_REQUESTS)
        
        response = self.session.get(
            url,
            params=params,
            headers=self._get_headers(),
            timeout=ScraperConfig.TIMEOUT,
            verify=ScraperConfig.VERIFY_SSL
        )
        
        response.raise_for_status()
        content = response.text
        
        # Cache the response
        if use_cache and self.cache:
            self.cache.set(url, content, params)
        
        return content
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method - implement in subclasses
        
        Returns:
            List of scraped data items
        """
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data - override in subclasses
        
        Args:
            data: Data item to validate
        
        Returns:
            True if valid, False otherwise
        """
        return data is not None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common artifacts
        text = text.replace('\xa0', ' ')
        text = text.replace('\u200b', '')
        
        return text.strip()
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime - override for specific formats"""
        from dateutil.parser import parse
        
        try:
            return parse(date_str)
        except Exception as e:
            self.logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
