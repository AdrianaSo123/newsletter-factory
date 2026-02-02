"""
Newsletter Factory - Core Factory Pattern Implementation

This module provides a reusable factory for creating AI investment newsletters
that help aspiring entrepreneurs stay informed about the AI ecosystem.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class InvestmentStage(Enum):
    """Investment stages for tracking company maturity"""
    SEED = "Seed"
    SERIES_A = "Series A"
    SERIES_B = "Series B"
    SERIES_C = "Series C"
    SERIES_D_PLUS = "Series D+"
    ACQUISITION = "Acquisition"
    IPO = "IPO"


class NewsletterSection(ABC):
    """Abstract base class for newsletter sections"""
    
    @abstractmethod
    def generate(self) -> str:
        """Generate the content for this section"""
        pass


class NewsletterFactory:
    """
    Factory for creating customized AI investment newsletters.
    
    This factory pattern allows for flexible newsletter creation with
    various sections and content types.
    """
    
    def __init__(self, title: str = "AI Investment Weekly"):
        self.title = title
        self.sections: List[NewsletterSection] = []
        self.date = datetime.now()
        
    def add_section(self, section: NewsletterSection) -> 'NewsletterFactory':
        """Add a section to the newsletter (builder pattern)"""
        self.sections.append(section)
        return self
    
    def create(self) -> str:
        """Generate the complete newsletter"""
        newsletter = []
        newsletter.append(f"# {self.title}")
        newsletter.append(f"*{self.date.strftime('%B %d, %Y')}*")
        newsletter.append("\n---\n")
        
        for section in self.sections:
            newsletter.append(section.generate())
            newsletter.append("\n")
        
        return "\n".join(newsletter)
    
    def reset(self) -> 'NewsletterFactory':
        """Reset the factory to create a new newsletter"""
        self.sections = []
        self.date = datetime.now()
        return self
