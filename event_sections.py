"""
Event-focused newsletter sections
"""

from typing import List
from newsletter_factory import NewsletterSection
from scrapers.event_scrapers import AIEvent
from datetime import datetime, timedelta


class UpcomingEventsSection(NewsletterSection):
    """Section showcasing upcoming AI events"""
    
    def __init__(self, events: List[AIEvent], max_items: int = 10):
        self.events = events[:max_items]
    
    def generate(self) -> str:
        content = ["## 📅 Upcoming AI Events", ""]
        content.append("*Mark your calendar - opportunities to learn and network*\n")
        
        if not self.events:
            content.append("No upcoming events found. Check back soon!\n")
            return "\n".join(content)
        
        # Group by time period
        this_week = []
        this_month = []
        later = []
        
        now = datetime.now()
        week_end = now + timedelta(days=7)
        month_end = now + timedelta(days=30)
        
        for event in self.events:
            if event.date <= week_end:
                this_week.append(event)
            elif event.date <= month_end:
                this_month.append(event)
            else:
                later.append(event)
        
        # This week section
        if this_week:
            content.append("### 🔥 This Week")
            for event in this_week:
                content.extend(self._format_event(event, show_days_until=True))
            content.append("")
        
        # This month section
        if this_month:
            content.append("### 📆 This Month")
            for event in this_month:
                content.extend(self._format_event(event))
            content.append("")
        
        # Later section
        if later:
            content.append("### 🗓️ Coming Soon")
            for event in later[:5]:  # Limit to 5
                content.extend(self._format_event(event))
            content.append("")
        
        return "\n".join(content)
    
    def _format_event(self, event: AIEvent, show_days_until: bool = False) -> List[str]:
        """Format a single event"""
        lines = []
        
        # Event header with emoji based on type
        emoji_map = {
            'Conference': '🎤',
            'Workshop': '🛠️',
            'Webinar': '💻',
            'Meetup': '🤝',
            'Hackathon': '⚡'
        }
        emoji = emoji_map.get(event.event_type, '📍')
        
        lines.append(f"**{emoji} {event.name}**")
        
        # Date and location
        date_str = event.date.strftime('%B %d, %Y')
        if show_days_until:
            days_until = (event.date - datetime.now()).days
            if days_until == 0:
                date_str += " (Today!)"
            elif days_until == 1:
                date_str += " (Tomorrow!)"
            else:
                date_str += f" ({days_until} days)"
        
        lines.append(f"- **When:** {date_str}")
        lines.append(f"- **Where:** {event.location}")
        
        if event.event_type:
            lines.append(f"- **Type:** {event.event_type}")
        
        if event.cost:
            lines.append(f"- **Cost:** {event.cost}")
        
        if event.topics:
            lines.append(f"- **Topics:** {', '.join(event.topics)}")
        
        if event.description:
            lines.append(f"- **About:** {event.description}")
        
        if event.url:
            lines.append(f"- **Link:** {event.url}")

        sources = getattr(event, "sources", [])
        if sources:
            src = sources[0]
            if getattr(event, "confidence", None) is not None:
                lines.append(f"- **Confidence:** {event.confidence:.2f}")
            if src.evidence_quote:
                lines.append(f"- **Evidence:** \"{src.evidence_quote}\"")
            if src.url:
                lines.append(f"- **Source:** {src.source_name} — {src.url}")
            else:
                lines.append(f"- **Source:** {src.source_name}")
        
        lines.append("")
        return lines


class EventsForEntrepreneursSection(NewsletterSection):
    """Section highlighting events specifically for entrepreneurs"""
    
    def __init__(self, events: List[AIEvent]):
        self.events = events
    
    def generate(self) -> str:
        content = ["## 🚀 Events for AI Entrepreneurs", ""]
        content.append("*Networking and learning opportunities for founders*\n")
        
        if not self.events:
            content.append("No entrepreneur-focused events found this period.\n")
            return "\n".join(content)
        
        for event in self.events[:8]:  # Limit to 8 events
            content.append(f"### {event.name}")
            content.append(f"📅 {event.date.strftime('%B %d, %Y')} | 📍 {event.location}\n")
            
            if event.description:
                content.append(event.description)
                content.append("")
            
            content.append("**Why attend:**")
            
            # Generate personalized reasons based on event type
            if 'Hackathon' in event.event_type:
                reasons = [
                    "Build your MVP in a focused environment",
                    "Meet potential co-founders and technical talent",
                    "Get feedback from experienced judges"
                ]
            elif 'Conference' in event.event_type:
                reasons = [
                    "Learn from successful AI founders",
                    "Network with investors and partners",
                    "Stay ahead of industry trends"
                ]
            elif 'Workshop' in event.event_type:
                reasons = [
                    "Hands-on learning with practical tools",
                    "Small group setting for deep dives",
                    "Direct access to instructors"
                ]
            else:
                reasons = [
                    "Connect with the AI startup community",
                    "Learn from peers and experts",
                    "Discover partnership opportunities"
                ]
            
            for reason in reasons:
                content.append(f"- {reason}")
            
            content.append("")
            
            if event.url:
                content.append(f"[Register Here]({event.url})")
                content.append("")
        
        return "\n".join(content)


class EventCalendarSection(NewsletterSection):
    """Compact calendar view of all events"""
    
    def __init__(self, events: List[AIEvent]):
        self.events = sorted(events, key=lambda x: x.date)
    
    def generate(self) -> str:
        content = ["## 📋 Event Calendar", ""]
        content.append("*Quick reference for all upcoming AI events*\n")
        
        if not self.events:
            return "\n".join(content + ["No events scheduled.\n"])
        
        # Create table
        content.append("| Date | Event | Type | Location | Cost |")
        content.append("|------|-------|------|----------|------|")
        
        for event in self.events:
            date = event.date.strftime('%b %d')
            name = event.name[:40] + "..." if len(event.name) > 40 else event.name
            location = event.location[:20] + "..." if len(event.location) > 20 else event.location
            
            if event.url:
                name = f"[{name}]({event.url})"
            
            content.append(
                f"| {date} | {name} | {event.event_type} | {location} | {event.cost} |"
            )
        
        content.append("")
        return "\n".join(content)
