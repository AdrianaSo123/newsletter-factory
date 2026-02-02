"""
Scrapers for AI events, conferences, meetups, and workshops
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from scrapers.base_scraper import BaseScraper
import feedparser
import re

from models import FactSource


@dataclass
class AIEvent:
    """Represents an AI event"""
    name: str
    event_type: str  # "Conference", "Meetup", "Workshop", "Webinar", "Hackathon"
    date: datetime
    location: str  # Can be "Virtual" or physical location
    description: str
    url: Optional[str] = None
    organizer: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    target_audience: str = "All"  # "Researchers", "Engineers", "Entrepreneurs", "All"
    cost: str = "Free"  # "Free", "Paid", "$X"
    registration_url: Optional[str] = None
    sources: List[FactSource] = field(default_factory=list)
    confidence: float = 0.5
    
    def is_upcoming(self) -> bool:
        """Check if event is in the future"""
        return self.date > datetime.now()
    
    def is_within_days(self, days: int) -> bool:
        """Check if event is within next N days"""
        return datetime.now() <= self.date <= datetime.now() + timedelta(days=days)


class EventbriteScraper(BaseScraper):
    """Scrape AI events from Eventbrite"""
    
    BASE_URL = "https://www.eventbrite.com"
    SEARCH_URL = "https://www.eventbrite.com/d/online/artificial-intelligence/"

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
        "agents",
        "agentic",
    ]

    def _looks_ai_related(self, name: str, description: str) -> bool:
        text = f"{name} {description}".lower()
        return any(k in text for k in self.AI_KEYWORDS)
    
    def scrape(self, days_ahead: int = 90) -> List[AIEvent]:
        """
        Scrape upcoming AI events from Eventbrite
        
        Args:
            days_ahead: How many days ahead to look for events
        
        Returns:
            List of AIEvent objects
        """
        self.logger.info("Scraping Eventbrite for AI events...")
        events = []
        
        try:
            html = self._fetch_url(self.SEARCH_URL)
            soup = self._parse_html(html)
            
            # Find event cards (structure may vary - this is an example)
            event_cards = soup.find_all('div', class_=re.compile('discover-search-desktop-card'))
            
            for card in event_cards[:20]:  # Limit to first 20
                try:
                    event = self._parse_event_card(card)
                    if event and event.is_within_days(days_ahead):
                        events.append(event)
                except Exception as e:
                    self.logger.warning(f"Error parsing event card: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping Eventbrite: {e}")
        
        self.logger.info(f"Found {len(events)} events from Eventbrite")
        return events
    
    def _parse_event_card(self, card) -> Optional[AIEvent]:
        """Parse individual event card"""
        try:
            # Extract event name
            name_elem = card.find('h3') or card.find('h2')
            if not name_elem:
                return None
            name = self.clean_text(name_elem.get_text())
            
            # Extract URL
            link_elem = card.find('a', href=True)
            url = link_elem['href'] if link_elem else None
            
            # Extract date (this is simplified - actual parsing depends on HTML structure)
            date_elem = card.find('time') or card.find('p', class_=re.compile('date'))
            date_str = date_elem.get_text() if date_elem else None
            if not date_str:
                # Don't invent dates; if we can't parse a date reliably, drop the event.
                return None

            event_date = self.parse_date(date_str)
            if not event_date:
                return None
            
            # Extract description
            desc_elem = card.find('p', class_=re.compile('description'))
            description = self.clean_text(desc_elem.get_text()) if desc_elem else ""

            # Hard filter: Eventbrite search pages can include unrelated results.
            if not self._looks_ai_related(name, description):
                return None
            
            # Determine event type
            event_type = self._determine_event_type(name, description)

            sources = [
                FactSource(
                    source_name="Eventbrite",
                    url=url,
                    retrieved_at=datetime.now(),
                    evidence_quote=self.clean_text(f"{name} — {date_str or ''}".strip(" -")),
                )
            ]

            confidence = 0.5
            if url and date_str:
                confidence = 0.7
            
            return AIEvent(
                name=name,
                event_type=event_type,
                date=event_date,
                location="Virtual",  # Most Eventbrite AI events are virtual
                description=description,
                url=url,
                organizer="Various",
                topics=self._extract_topics(name, description),
                cost="Varies",
                sources=sources,
                confidence=confidence,
            )
        
        except Exception as e:
            self.logger.warning(f"Error parsing event card: {e}")
            return None
    
    def _determine_event_type(self, name: str, description: str) -> str:
        """Determine event type from name and description"""
        text = f"{name} {description}".lower()
        
        if 'hackathon' in text:
            return 'Hackathon'
        elif 'workshop' in text:
            return 'Workshop'
        elif 'webinar' in text:
            return 'Webinar'
        elif 'meetup' in text:
            return 'Meetup'
        elif 'conference' in text or 'summit' in text:
            return 'Conference'
        else:
            return 'Event'
    
    def _extract_topics(self, name: str, description: str) -> List[str]:
        """Extract topics from event name and description"""
        text = f"{name} {description}".lower()
        topics = []
        
        topic_keywords = {
            'Machine Learning': ['machine learning', 'ml'],
            'Deep Learning': ['deep learning', 'neural network'],
            'NLP': ['nlp', 'natural language', 'language model'],
            'Computer Vision': ['computer vision', 'image recognition'],
            'GenAI': ['generative ai', 'genai', 'gpt', 'llm'],
            'AI Safety': ['ai safety', 'alignment', 'ethics'],
            'Robotics': ['robotics', 'autonomous'],
            'Entrepreneurship': ['startup', 'entrepreneur', 'business'],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        # Do not default to ['AI']; that would falsely label unrelated events.
        return topics


class MeetupScraper(BaseScraper):
    """Scrape AI meetups (Note: Meetup.com requires authentication for full access)"""
    
    BASE_URL = "https://www.meetup.com"
    
    def scrape(self, location: str = "online", days_ahead: int = 60) -> List[AIEvent]:
        """
        Scrape AI meetups
        
        Note: This is a simplified version. Full access requires Meetup API key.
        """
        self.logger.info("Scraping Meetup for AI events...")
        events = []
        
        # For demonstration, return common AI meetup patterns
        # In production, use Meetup API with authentication
        
        self.logger.info(f"Found {len(events)} events from Meetup (API key required for full access)")
        return events


class LumaScraper(BaseScraper):
    """Scrape AI events from Lu.ma (popular for startup/tech events)"""
    
    BASE_URL = "https://lu.ma"
    DISCOVER_URL = "https://lu.ma/discover"
    
    def scrape(self, days_ahead: int = 90) -> List[AIEvent]:
        """Scrape AI events from Lu.ma"""
        self.logger.info("Scraping Lu.ma for AI events...")
        events = []
        
        try:
            # Lu.ma uses dynamic loading, might need Selenium for full scraping
            # This is a simplified version
            
            search_url = f"{self.DISCOVER_URL}?q=artificial+intelligence"
            html = self._fetch_url(search_url)
            soup = self._parse_html(html)
            
            # Parse event listings
            # Note: Actual structure depends on Lu.ma's current HTML
            
            self.logger.info(f"Found {len(events)} events from Lu.ma")
        
        except Exception as e:
            self.logger.error(f"Error scraping Lu.ma: {e}")
        
        return events


class AIConferenceTracker:
    """Track major AI conferences (manually curated + scraped)"""
    
    MAJOR_CONFERENCES = [
        {
            'name': 'NeurIPS 2026',
            'event_type': 'Conference',
            'date': datetime(2026, 12, 6),
            'location': 'Vancouver, Canada',
            'description': 'Neural Information Processing Systems - Premier ML/AI conference',
            'url': 'https://neurips.cc',
            'topics': ['Machine Learning', 'Deep Learning', 'AI Research'],
            'target_audience': 'Researchers',
            'cost': 'Paid'
        },
        {
            'name': 'ICML 2026',
            'event_type': 'Conference',
            'date': datetime(2026, 7, 12),
            'location': 'Vienna, Austria',
            'description': 'International Conference on Machine Learning',
            'url': 'https://icml.cc',
            'topics': ['Machine Learning', 'AI Research'],
            'target_audience': 'Researchers',
            'cost': 'Paid'
        },
        {
            'name': 'AI Engineer Summit 2026',
            'event_type': 'Conference',
            'date': datetime(2026, 10, 8),
            'location': 'San Francisco, CA',
            'description': 'Conference for AI engineers building production systems',
            'url': 'https://ai.engineer',
            'topics': ['GenAI', 'LLM', 'Production AI'],
            'target_audience': 'Engineers',
            'cost': 'Paid'
        },
        {
            'name': 'AGI House Events',
            'event_type': 'Meetup',
            'date': datetime(2026, 2, 15),
            'location': 'San Francisco, CA',
            'description': 'Regular AI founder and builder meetups',
            'url': 'https://agi.house',
            'topics': ['Entrepreneurship', 'GenAI', 'Startups'],
            'target_audience': 'Entrepreneurs',
            'cost': 'Free'
        }
    ]
    
    @classmethod
    def get_major_conferences(cls, days_ahead: int = 365) -> List[AIEvent]:
        """Get list of major AI conferences"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        events = []
        for conf_data in cls.MAJOR_CONFERENCES:
            if conf_data['date'] <= cutoff_date:
                sources = [
                    FactSource(
                        source_name="Curated (official site)",
                        url=conf_data.get("url"),
                        retrieved_at=datetime.now(),
                        evidence_quote=conf_data.get("description"),
                    )
                ]
                events.append(
                    AIEvent(
                        **conf_data,
                        sources=sources,
                        confidence=0.6,
                    )
                )
        
        return events


class EventAggregator:
    """Aggregate events from multiple sources"""
    
    def __init__(self):
        self.scrapers = [
            EventbriteScraper(),
            # MeetupScraper(),  # Requires API key
            # LumaScraper(),  # Might need Selenium
        ]
    
    def fetch_upcoming_events(self, days_ahead: int = 90) -> List[AIEvent]:
        """
        Fetch and aggregate events from all sources
        
        Args:
            days_ahead: How many days ahead to look
        
        Returns:
            List of AIEvent objects
        """
        all_events = []
        
        # Scrape from dynamic sources
        for scraper in self.scrapers:
            try:
                events = scraper.scrape(days_ahead=days_ahead)
                all_events.extend(events)
            except Exception as e:
                print(f"Scraper failed: {e}")
                continue
        
        # Add major conferences
        major_events = AIConferenceTracker.get_major_conferences(days_ahead)
        all_events.extend(major_events)
        
        # Deduplicate
        all_events = self._deduplicate(all_events)

        # Validate grounding + sanity (drop invalid)
        from validation import validate_event

        valid_events: List[AIEvent] = []
        invalid_count = 0
        for ev in all_events:
            res = validate_event(ev)
            if res.ok:
                valid_events.append(ev)
            else:
                invalid_count += 1

        if invalid_count:
            print(f"Filtered {invalid_count} ungrounded/invalid event items")

        all_events = valid_events
        
        # Sort by date
        all_events.sort(key=lambda x: x.date)
        
        # Filter to only upcoming events
        all_events = [e for e in all_events if e.is_upcoming()]
        
        return all_events
    
    def _deduplicate(self, events: List[AIEvent]) -> List[AIEvent]:
        """Remove duplicate events"""
        seen = set()
        unique = []
        
        for event in events:
            key = (event.name.lower(), event.date.date())
            if key not in seen:
                seen.add(key)
                unique.append(event)
        
        return unique
    
    def get_events_by_type(self, events: List[AIEvent], 
                          event_type: str) -> List[AIEvent]:
        """Filter events by type"""
        return [e for e in events if e.event_type == event_type]
    
    def get_events_for_entrepreneurs(self, events: List[AIEvent]) -> List[AIEvent]:
        """Get events most relevant for entrepreneurs"""
        entrepreneur_keywords = ['startup', 'entrepreneur', 'founder', 'business', 'venture']
        
        relevant = []
        for event in events:
            text = f"{event.name} {event.description}".lower()
            if (event.target_audience == 'Entrepreneurs' or
                any(keyword in text for keyword in entrepreneur_keywords) or
                'Entrepreneurship' in event.topics):
                relevant.append(event)
        
        return relevant
