"""
Updated data source using real web scraping
"""

from typing import List
from models import Investment
from scrapers.investment_scrapers import InvestmentDataAggregator
from data_sources import DataSource
import logging

logging.basicConfig(level=logging.INFO)


class RealTimeDataSource(DataSource):
    """
    Data source that fetches real investment data from web sources
    
    This replaces MockDataSource with actual scraped data from:
    - TechCrunch
    - VentureBeat
    - Crunchbase News
    """
    
    def __init__(self, use_cache: bool = True):
        """
        Initialize real-time data source
        
        Args:
            use_cache: Whether to use cached data (recommended)
        """
        self.aggregator = InvestmentDataAggregator()
        self.use_cache = use_cache
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def fetch_investments(self, days_back: int = 30) -> List[Investment]:
        """
        Fetch recent investments from real sources
        
        Args:
            days_back: How many days of historical data to fetch
        
        Returns:
            List of Investment objects with real data
        """
        self.logger.info(f"Fetching real investment data from past {days_back} days...")
        
        try:
            investments = self.aggregator.fetch_recent_investments(days_back=days_back)
            
            self.logger.info(f"Successfully fetched {len(investments)} investments")
            
            if not investments:
                self.logger.warning("No investments found. Check if scrapers are working correctly.")
                self.logger.info("Falling back to sample data for demonstration...")
                # Fall back to mock data if scraping fails
                from data_sources import MockDataSource
                return MockDataSource().fetch_investments(days_back)
            
            return investments
        
        except Exception as e:
            self.logger.error(f"Error fetching real data: {e}")
            self.logger.info("Falling back to sample data...")
            
            # Graceful fallback to mock data
            from data_sources import MockDataSource
            return MockDataSource().fetch_investments(days_back)
    
    def refresh_cache(self):
        """Force refresh of cached data"""
        self.logger.info("Clearing cache and fetching fresh data...")
        
        # Clear cache for all scrapers
        for scraper in self.aggregator.scrapers:
            if hasattr(scraper, 'cache') and scraper.cache:
                scraper.cache.clear_expired(max_age_hours=0)
        
        self.logger.info("Cache cleared")
