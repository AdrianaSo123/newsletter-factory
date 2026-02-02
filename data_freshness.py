"""
Data freshness monitoring and automated refresh system
"""

from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any
from scrapers.real_data_source import RealTimeDataSource
from scrapers.event_scrapers import EventAggregator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFreshnessMonitor:
    """
    Monitor data freshness and trigger refreshes when needed
    """
    
    METADATA_FILE = Path("cache/data_metadata.json")
    
    # Freshness thresholds (in hours)
    INVESTMENT_DATA_MAX_AGE = 6  # Refresh every 6 hours
    EVENT_DATA_MAX_AGE = 24      # Refresh every 24 hours
    
    def __init__(self):
        self.metadata_file = self.METADATA_FILE
        self.metadata_file.parent.mkdir(exist_ok=True)
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load data freshness metadata"""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save data freshness metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Error saving metadata: {e}")
    
    def _is_stale(self, data_type: str, max_age_hours: int) -> bool:
        """Check if data is stale"""
        metadata = self._load_metadata()
        
        if data_type not in metadata:
            return True  # No data exists
        
        last_update_str = metadata[data_type].get('last_update')
        if not last_update_str:
            return True
        
        try:
            last_update = datetime.fromisoformat(last_update_str)
            age = datetime.now() - last_update
            
            is_stale = age > timedelta(hours=max_age_hours)
            
            if is_stale:
                logger.info(f"{data_type} data is stale (age: {age})")
            else:
                logger.info(f"{data_type} data is fresh (age: {age})")
            
            return is_stale
        
        except Exception as e:
            logger.warning(f"Error checking staleness: {e}")
            return True
    
    def _mark_updated(self, data_type: str, item_count: int = 0):
        """Mark data as updated"""
        metadata = self._load_metadata()
        
        metadata[data_type] = {
            'last_update': datetime.now().isoformat(),
            'item_count': item_count
        }
        
        self._save_metadata(metadata)
        logger.info(f"Marked {data_type} as updated ({item_count} items)")
    
    def check_investment_data(self) -> bool:
        """Check if investment data needs refresh"""
        return self._is_stale('investments', self.INVESTMENT_DATA_MAX_AGE)
    
    def check_event_data(self) -> bool:
        """Check if event data needs refresh"""
        return self._is_stale('events', self.EVENT_DATA_MAX_AGE)
    
    def mark_investments_updated(self, count: int = 0):
        """Mark investment data as updated"""
        self._mark_updated('investments', count)
    
    def mark_events_updated(self, count: int = 0):
        """Mark event data as updated"""
        self._mark_updated('events', count)
    
    def get_data_age(self, data_type: str) -> Optional[timedelta]:
        """Get age of data"""
        metadata = self._load_metadata()
        
        if data_type not in metadata:
            return None
        
        last_update_str = metadata[data_type].get('last_update')
        if not last_update_str:
            return None
        
        try:
            last_update = datetime.fromisoformat(last_update_str)
            return datetime.now() - last_update
        except:
            return None
    
    def get_status_report(self) -> str:
        """Get human-readable status report"""
        metadata = self._load_metadata()
        
        report = ["## Data Freshness Status\n"]
        
        for data_type in ['investments', 'events']:
            if data_type in metadata:
                age = self.get_data_age(data_type)
                count = metadata[data_type].get('item_count', 'unknown')
                
                status = "✅ Fresh" if not self._is_stale(
                    data_type, 
                    self.INVESTMENT_DATA_MAX_AGE if data_type == 'investments' else self.EVENT_DATA_MAX_AGE
                ) else "⚠️ Stale"
                
                report.append(f"**{data_type.title()}:** {status}")
                report.append(f"- Last updated: {age} ago" if age else "- Never updated")
                report.append(f"- Item count: {count}")
                report.append("")
            else:
                report.append(f"**{data_type.title()}:** ❌ No data")
                report.append("")
        
        return "\n".join(report)


class AutoRefreshManager:
    """
    Automatically refresh data when it becomes stale
    """
    
    def __init__(self):
        self.monitor = DataFreshnessMonitor()
        self.investment_source = RealTimeDataSource(use_cache=True)
        self.event_aggregator = EventAggregator()
    
    def refresh_if_needed(self, force: bool = False) -> Dict[str, Any]:
        """
        Check all data sources and refresh if needed
        
        Args:
            force: Force refresh regardless of age
        
        Returns:
            Dict with refresh status
        """
        results = {
            'investments_refreshed': False,
            'events_refreshed': False,
            'errors': []
        }
        
        # Check and refresh investment data
        if force or self.monitor.check_investment_data():
            logger.info("Refreshing investment data...")
            try:
                investments = self.investment_source.fetch_investments(days_back=7)
                self.monitor.mark_investments_updated(len(investments))
                results['investments_refreshed'] = True
                logger.info(f"✅ Investment data refreshed ({len(investments)} items)")
            except Exception as e:
                error_msg = f"Failed to refresh investments: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            logger.info("Investment data is still fresh, skipping refresh")
        
        # Check and refresh event data
        if force or self.monitor.check_event_data():
            logger.info("Refreshing event data...")
            try:
                events = self.event_aggregator.fetch_upcoming_events(days_ahead=90)
                self.monitor.mark_events_updated(len(events))
                results['events_refreshed'] = True
                logger.info(f"✅ Event data refreshed ({len(events)} items)")
            except Exception as e:
                error_msg = f"Failed to refresh events: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            logger.info("Event data is still fresh, skipping refresh")
        
        return results
    
    def get_status(self) -> str:
        """Get status report"""
        return self.monitor.get_status_report()


# Standalone functions for easy use
def refresh_all_data(force: bool = False):
    """Refresh all data sources"""
    manager = AutoRefreshManager()
    return manager.refresh_if_needed(force=force)


def get_data_status():
    """Get current data freshness status"""
    monitor = DataFreshnessMonitor()
    return monitor.get_status_report()


if __name__ == "__main__":
    print("Data Freshness Manager")
    print("=" * 60)
    print()
    
    # Check current status
    print(get_data_status())
    
    # Refresh if needed
    print("\nChecking for stale data...")
    results = refresh_all_data()
    
    print("\nRefresh Results:")
    print(f"- Investments refreshed: {results['investments_refreshed']}")
    print(f"- Events refreshed: {results['events_refreshed']}")
    
    if results['errors']:
        print(f"- Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"  • {error}")
    
    print("\n" + get_data_status())
