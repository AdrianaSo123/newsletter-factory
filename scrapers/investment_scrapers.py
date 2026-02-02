"""
Real data scrapers for AI investment news from multiple sources
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import feedparser
from scrapers.base_scraper import BaseScraper
from models import Investment, Company, FactSource
from newsletter_factory import InvestmentStage

from parsing.extractors import (
    parse_money_usd_millions,
    infer_stage,
    extract_company_name_from_title,
    extract_investor_names,
)

from validation import validate_investment


class TechCrunchScraper(BaseScraper):
    """Scrape AI investment news from TechCrunch"""
    
    BASE_URL = "https://techcrunch.com"
    RSS_FEEDS = [
        # The AI tag feed is the most on-topic but can be quiet.
        {"name": "AI", "url": "https://techcrunch.com/tag/artificial-intelligence/feed/", "require_ai": False},
        # Broaden coverage while keeping AI relevance via keyword filtering.
        {"name": "Funding", "url": "https://techcrunch.com/tag/funding/feed/", "require_ai": True},
        {"name": "Venture Capital", "url": "https://techcrunch.com/tag/venture-capital/feed/", "require_ai": True},
    ]

    FUNDING_KEYWORDS = [
        "raises",
        "raised",
        "funding",
        "investment",
        "series ",
        "seed",
        "round",
        "closes",
        "backed",
    ]

    AI_KEYWORDS = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "deep learning",
        "llm",
        "large language model",
        "generative ai",
        "genai",
        "gpt",
        "agentic",
    ]

    def _looks_funding_related(self, text: str) -> bool:
        t = (text or "").lower()
        return any(k in t for k in self.FUNDING_KEYWORDS)

    def _looks_ai_related(self, text: str) -> bool:
        t = (text or "").lower()
        return any(k in t for k in self.AI_KEYWORDS)

    def _entry_text(self, entry: Any) -> str:
        """Best-effort extract readable text from an RSS entry."""
        parts: List[str] = []
        if getattr(entry, "title", None):
            parts.append(str(entry.title))
        if getattr(entry, "summary", None):
            parts.append(str(entry.summary))

        content = getattr(entry, "content", None)
        if isinstance(content, list) and content:
            value = content[0].get("value") if isinstance(content[0], dict) else None
            if value:
                parts.append(str(value))

        raw = "\n".join(parts)
        # RSS summary/content can contain HTML.
        try:
            soup = self._parse_html(raw)
            return self.clean_text(soup.get_text("\n"))
        except Exception:
            return self.clean_text(raw)
    
    def scrape(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Scrape TechCrunch AI news
        
        Args:
            days_back: How many days of news to fetch
        
        Returns:
            List of investment data
        """
        self.logger.info("Scraping TechCrunch RSS feeds...")
        investments = []
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)

            seen_urls = set()

            for feed_info in self.RSS_FEEDS:
                try:
                    rss_xml = self._fetch_url(feed_info["url"], use_cache=True)
                    feed = feedparser.parse(rss_xml)
                except Exception as e:
                    self.logger.warning(f"Error fetching TechCrunch feed {feed_info['name']}: {e}")
                    continue

                for entry in getattr(feed, "entries", []) or []:
                    try:
                        pub_struct = getattr(entry, "published_parsed", None)
                        if not pub_struct:
                            continue

                        pub_date = datetime(*pub_struct[:6])
                        if pub_date < cutoff_date:
                            continue

                        url = getattr(entry, "link", None)
                        if not url or url in seen_urls:
                            continue

                        entry_text = self._entry_text(entry)

                        if not self._looks_funding_related(entry_text):
                            continue

                        if feed_info.get("require_ai") and not self._looks_ai_related(entry_text):
                            continue

                        # Prefer extracting from RSS content first (faster, less brittle)
                        amount = parse_money_usd_millions(entry_text)
                        title_text = self.clean_text(getattr(entry, "title", ""))

                        article_data: Optional[Dict[str, Any]] = None

                        if amount is not None:
                            article_data = {
                                "title": title_text,
                                "amount": amount,
                                "raw_text": self.clean_text(entry_text[:1000]),
                            }

                            investors = extract_investor_names(entry_text)
                            if investors:
                                article_data["lead_investor"] = investors[0]
                                article_data["investors"] = investors

                            round_match = re.search(
                                r"(seed|series [a-f]|series [a-f]\+|acquisition|ipo)",
                                entry_text,
                                re.IGNORECASE,
                            )
                            if round_match:
                                article_data["round"] = round_match.group(1)

                            # Evidence: first line mentioning money.
                            for line in entry_text.splitlines():
                                if "$" in line and any(k in line.lower() for k in ["million", "billion", "m", "b"]):
                                    article_data["evidence_quote"] = self.clean_text(line)
                                    break

                        # Fallback: fetch full article if RSS content didn't contain an amount.
                        if article_data is None:
                            article_data = self._scrape_article(url)

                        if article_data:
                            article_data["source"] = "TechCrunch"
                            article_data["url"] = url
                            article_data["date"] = pub_date
                            investments.append(article_data)
                            seen_urls.add(url)

                    except Exception as e:
                        self.logger.warning(f"Error processing TechCrunch entry: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error scraping TechCrunch: {e}")
        
        self.logger.info(f"Found {len(investments)} investment stories from TechCrunch")
        return investments
    
    def _scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape individual article for investment details"""
        try:
            html = self._fetch_url(url)
            soup = self._parse_html(html)

            # TechCrunch markup changes over time; attempt several likely containers.
            container = (
                soup.find("div", class_="article-content")
                or soup.find("div", class_="entry-content")
                or soup.find("div", class_=re.compile(r"article__content|content"))
                or soup.find("article")
            )

            if not container:
                return None

            text = container.get_text("\n")
            
            # Extract investment details using regex patterns
            data = {
                'raw_text': self.clean_text(text[:1000])  # First 1000 chars
            }
            
            # Extract company name (usually in title or first paragraph)
            title = soup.find('h1')
            if title:
                data['title'] = self.clean_text(title.get_text())
            
            # Extract funding amount (USD millions)
            amount = parse_money_usd_millions(text)
            if amount is not None:
                data['amount'] = amount
            
            # Extract funding round
            round_match = re.search(r'(seed|series [a-f]|series [a-f]\+|acquisition|ipo)', text, re.IGNORECASE)
            if round_match:
                data['round'] = round_match.group(1)
            
            # Extract investor names (conservative)
            investors = extract_investor_names(text)
            if investors:
                data['lead_investor'] = investors[0]
                data['investors'] = investors

            # Evidence quote: first line mentioning "$" (best-effort, used for grounding)
            for line in text.splitlines():
                if "$" in line and any(k in line.lower() for k in ["million", "billion", "m", "b"]):
                    data['evidence_quote'] = self.clean_text(line)
                    break
            
            return data if data.get('amount') else None
        
        except Exception as e:
            self.logger.warning(f"Error scraping article {url}: {e}")
            return None


class VentureBeatScraper(BaseScraper):
    """Scrape AI investment news from VentureBeat"""
    
    BASE_URL = "https://venturebeat.com"
    AI_NEWS_URL = "https://venturebeat.com/category/ai/"
    
    def scrape(self, days_back: int = 7, max_pages: int = 3) -> List[Dict[str, Any]]:
        """Scrape VentureBeat AI investment news"""
        self.logger.info("Scraping VentureBeat AI news...")
        investments = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.AI_NEWS_URL}page/{page}/" if page > 1 else self.AI_NEWS_URL
                
                html = self._fetch_url(url)
                soup = self._parse_html(html)
                
                # Find article links
                articles = soup.find_all('article')
                
                for article in articles:
                    try:
                        link_elem = article.find('a', href=True)
                        if not link_elem:
                            continue
                        
                        article_url = link_elem['href']
                        title = link_elem.get_text()
                        
                        # Check if funding-related
                        if any(keyword in title.lower() 
                               for keyword in ['raises', 'funding', 'investment', 'series']):
                            
                            article_data = self._scrape_article(article_url)
                            if article_data:
                                article_data['source'] = 'VentureBeat'
                                article_data['url'] = article_url
                                investments.append(article_data)
                    
                    except Exception as e:
                        self.logger.warning(f"Error processing article: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error scraping VentureBeat: {e}")
        
        self.logger.info(f"Found {len(investments)} investment stories from VentureBeat")
        return investments
    
    def _scrape_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract investment details from VentureBeat article"""
        try:
            html = self._fetch_url(url)
            soup = self._parse_html(html)
            
            article = soup.find('article')
            if not article:
                return None
            
            text = article.get_text("\n")
            
            data = {}
            
            amount = parse_money_usd_millions(text)
            if amount is not None:
                data['amount'] = amount
            
            # Extract company and round
            title = soup.find('h1')
            if title:
                data['title'] = self.clean_text(title.get_text())

            investors = extract_investor_names(text)
            if investors:
                data['lead_investor'] = investors[0]
                data['investors'] = investors

            for line in text.splitlines():
                if "$" in line and any(k in line.lower() for k in ["million", "billion", "m", "b"]):
                    data['evidence_quote'] = self.clean_text(line)
                    break
            
            # Date
            time_elem = soup.find('time')
            if time_elem and time_elem.get('datetime'):
                data['date'] = self.parse_date(time_elem['datetime'])
            
            return data if data.get('amount') else None
        
        except Exception as e:
            self.logger.warning(f"Error scraping VentureBeat article {url}: {e}")
            return None


class CrunchbaseNewsScraper(BaseScraper):
    """
    Scrape Crunchbase news
    Note: Full Crunchbase API access requires paid subscription
    This scraper uses the public news feed
    """
    
    NEWS_URL = "https://news.crunchbase.com/feed/"

    AI_KEYWORDS = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "deep learning",
        "llm",
        "large language model",
        "generative ai",
        "genai",
        "gpt",
        "agent",
        "agentic",
    ]

    def _looks_ai_related(self, text: str) -> bool:
        t = (text or "").lower()
        return any(k in t for k in self.AI_KEYWORDS)
    
    def scrape(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Scrape Crunchbase news RSS feed"""
        self.logger.info("Scraping Crunchbase news...")
        investments = []
        
        try:
            feed = feedparser.parse(self.NEWS_URL)
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for entry in feed.entries:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                    
                    if pub_date < cutoff_date:
                        continue
                    
                    title = entry.title.lower()
                    summary = getattr(entry, "summary", "")
                    combined = f"{entry.title} {summary}"

                    # Only keep AI-related coverage.
                    if not self._looks_ai_related(combined):
                        continue
                    
                    if any(keyword in title 
                           for keyword in ['funding', 'raises', 'investment', 'venture']):
                        
                        data = {
                            'title': self.clean_text(entry.title),
                            'summary': self.clean_text(entry.summary),
                            'url': entry.link,
                            'date': pub_date,
                            'source': 'Crunchbase News'
                        }
                        
                        # Try to extract amount from title/summary
                        text = f"{entry.title} {entry.summary}"
                        amount = parse_money_usd_millions(text)
                        if amount is not None:
                            data['amount'] = amount
                            data['evidence_quote'] = self.clean_text(entry.title)
                            investments.append(data)
                
                except Exception as e:
                    self.logger.warning(f"Error processing Crunchbase entry: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping Crunchbase: {e}")
        
        self.logger.info(f"Found {len(investments)} investment stories from Crunchbase")
        return investments


class InvestmentDataAggregator:
    """
    Aggregates investment data from multiple sources
    and converts to standardized Investment objects
    """
    
    def __init__(self):
        self.scrapers = [
            TechCrunchScraper(),
            VentureBeatScraper(),
            CrunchbaseNewsScraper()
        ]
    
    def fetch_recent_investments(self, days_back: int = 7) -> List[Investment]:
        """
        Fetch and aggregate investment data from all sources
        
        Args:
            days_back: Days of historical data to fetch
        
        Returns:
            List of Investment objects
        """
        all_data = []
        
        for scraper in self.scrapers:
            try:
                data = scraper.scrape(days_back=days_back)
                all_data.extend(data)
            except Exception as e:
                scraper.logger.error(f"Scraper failed: {e}")
                continue
        
        # Convert to Investment objects
        investments = []
        for item in all_data:
            try:
                investment = self._convert_to_investment(item)
                if investment:
                    investments.append(investment)
            except Exception as e:
                print(f"Error converting item: {e}")
                continue
        
        # Deduplicate based on company name and amount
        investments = self._deduplicate(investments)

        # Validate: drop anything ungrounded or inconsistent
        valid_investments: List[Investment] = []
        invalid_count = 0
        for inv in investments:
            res = validate_investment(inv)
            if res.ok:
                valid_investments.append(inv)
            else:
                invalid_count += 1

        if invalid_count:
            # Keep log terse; reasons are available if needed for debugging.
            print(f"Filtered {invalid_count} ungrounded/invalid investment items")

        investments = valid_investments
        
        # Sort by date
        investments.sort(key=lambda x: x.date, reverse=True)
        
        return investments
    
    def _convert_to_investment(self, data: Dict[str, Any]) -> Optional[Investment]:
        """Convert scraped data to Investment object"""
        
        if not data.get('amount'):
            return None
        
        # Extract company name from title (conservative)
        company_name = extract_company_name_from_title(data.get('title', ''))
        if not company_name:
            return None
        
        # Create investee company
        investee = Company(
            name=company_name,
            description=data.get('summary', '')[:200],
            sector=self._infer_sector(data),
            # Keep company website unknown rather than storing an article URL here.
            website=None,
        )
        
        # Create investor (if known)
        investor_name = data.get('lead_investor', 'Undisclosed Investors')
        investor = Company(
            name=investor_name,
            description=f"Investor in {company_name}",
            sector="VC Firm"
        )
        
        # Determine investment stage
        stage = infer_stage(data.get('round', '') or data.get('title', ''))
        
        sources = [
            FactSource(
                source_name=data.get('source', 'Unknown'),
                url=data.get('url'),
                retrieved_at=datetime.now(),
                evidence_quote=data.get('evidence_quote') or data.get('summary'),
            )
        ]

        confidence = 0.5
        if data.get('url') and data.get('amount') and company_name:
            confidence = 0.7

        # Create investment
        investment = Investment(
            investor=investor,
            investee=investee,
            amount=float(data['amount']),
            stage=stage,
            date=data.get('date', datetime.now()),
            details=data.get('summary', '')[:300],
            key_insights=[
                f"Source: {data.get('source', 'Unknown')}",
                f"Article: {data.get('url', 'N/A')}"
            ],
            sources=sources,
            confidence=confidence,
        )
        
        return investment
    
    def _infer_sector(self, data: Dict[str, Any]) -> str:
        """Infer AI sector from article content"""
        text = f"{data.get('title', '')} {data.get('summary', '')}".lower()
        
        sector_keywords = {
            'LLM': ['language model', 'llm', 'gpt', 'chatbot', 'conversational ai'],
            'Computer Vision': ['computer vision', 'image recognition', 'visual ai'],
            'Robotics': ['robotics', 'autonomous', 'robot'],
            'Developer Tools': ['developer', 'api', 'sdk', 'platform'],
            'Healthcare AI': ['healthcare', 'medical', 'diagnosis', 'health'],
            'AI Infrastructure': ['infrastructure', 'cloud', 'compute', 'gpu'],
            'Enterprise AI': ['enterprise', 'b2b', 'business'],
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in text for keyword in keywords):
                return sector
        
        return 'AI'  # Default
    
    def _deduplicate(self, investments: List[Investment]) -> List[Investment]:
        """Remove duplicate investments"""
        seen = set()
        unique = []
        
        for inv in investments:
            date_key = inv.date.date().isoformat() if getattr(inv, "date", None) else "unknown"
            key = (inv.investee.name.lower(), round(float(inv.amount), 1), date_key)
            if key not in seen:
                seen.add(key)
                unique.append(inv)
        
        return unique
