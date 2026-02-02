"""
Data source handlers for gathering investment information
"""

from abc import ABC, abstractmethod
from typing import List
from models import Investment, Company, FactSource
from datetime import datetime


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch_investments(self, days_back: int = 30) -> List[Investment]:
        """Fetch recent investments"""
        pass


class MockDataSource(DataSource):
    """Mock data source for testing and examples"""
    
    def fetch_investments(self, days_back: int = 30) -> List[Investment]:
        """Return sample investment data"""
        from newsletter_factory import InvestmentStage
        
        # Sample data
        return [
            Investment(
                investor=Company("Google Ventures", "Venture capital arm of Google", "VC Firm"),
                investee=Company("Anthropic", "AI safety and research company", "LLM"),
                amount=450.0,
                stage=InvestmentStage.SERIES_C,
                date=datetime(2026, 1, 15),
                details="Focus on constitutional AI and safety research",
                key_insights=[
                    "Major bet on AI safety as competitive advantage",
                    "Signals importance of responsible AI development",
                    "Opens opportunities for safety-focused AI tools"
                ],
                sources=[
                    FactSource(
                        source_name="MockDataSource",
                        url=None,
                        retrieved_at=datetime.now(),
                        evidence_quote="Sample record for development/testing.",
                    )
                ],
                confidence=0.2,
            ),
            Investment(
                investor=Company("Microsoft", "Technology corporation", "Big Tech"),
                investee=Company("OpenAI", "AI research and deployment company", "LLM"),
                amount=10000.0,
                stage=InvestmentStage.SERIES_D_PLUS,
                date=datetime(2026, 1, 20),
                details="Strategic partnership extension for Azure integration",
                key_insights=[
                    "Cloud + AI integration is the winning formula",
                    "Enterprise AI adoption accelerating",
                    "Infrastructure plays are critical for AI success"
                ],
                sources=[
                    FactSource(
                        source_name="MockDataSource",
                        url=None,
                        retrieved_at=datetime.now(),
                        evidence_quote="Sample record for development/testing.",
                    )
                ],
                confidence=0.2,
            ),
            Investment(
                investor=Company("Sequoia Capital", "Venture capital firm", "VC Firm"),
                investee=Company("Mistral AI", "Open-source AI models", "LLM"),
                amount=385.0,
                stage=InvestmentStage.SERIES_B,
                date=datetime(2026, 1, 10),
                details="European AI champion building open-source models",
                key_insights=[
                    "Open-source AI models gaining investor confidence",
                    "European AI ecosystem maturing rapidly",
                    "Developer-first approach attracting capital"
                ],
                sources=[
                    FactSource(
                        source_name="MockDataSource",
                        url=None,
                        retrieved_at=datetime.now(),
                        evidence_quote="Sample record for development/testing.",
                    )
                ],
                confidence=0.2,
            ),
            Investment(
                investor=Company("Andreessen Horowitz", "Venture capital firm", "VC Firm"),
                investee=Company("Character.AI", "AI chatbot platform", "Consumer AI"),
                amount=150.0,
                stage=InvestmentStage.SERIES_A,
                date=datetime(2026, 1, 25),
                details="Consumer AI experiences with personality",
                key_insights=[
                    "Consumer AI beyond productivity is emerging",
                    "Engagement metrics rival social media",
                    "Entertainment + AI = untapped market"
                ],
                sources=[
                    FactSource(
                        source_name="MockDataSource",
                        url=None,
                        retrieved_at=datetime.now(),
                        evidence_quote="Sample record for development/testing.",
                    )
                ],
                confidence=0.2,
            ),
            Investment(
                investor=Company("Khosla Ventures", "Venture capital firm", "VC Firm"),
                investee=Company("Replit", "AI-powered coding platform", "Developer Tools"),
                amount=97.4,
                stage=InvestmentStage.SERIES_B,
                date=datetime(2026, 1, 18),
                details="AI-native IDE with built-in code generation",
                key_insights=[
                    "AI coding assistants becoming infrastructure",
                    "Lowering barriers to software development",
                    "Education meets professional tools"
                ],
                sources=[
                    FactSource(
                        source_name="MockDataSource",
                        url=None,
                        retrieved_at=datetime.now(),
                        evidence_quote="Sample record for development/testing.",
                    )
                ],
                confidence=0.2,
            )
        ]


class APIDataSource(DataSource):
    """
    Data source that connects to external APIs
    (e.g., Crunchbase, PitchBook, etc.)
    """
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def fetch_investments(self, days_back: int = 30) -> List[Investment]:
        """Fetch from external API - implement based on your data provider"""
        # TODO: Implement actual API integration
        # This would typically make HTTP requests to investment databases
        raise NotImplementedError("Connect to your preferred data API (Crunchbase, PitchBook, etc.)")


class CSVDataSource(DataSource):
    """Data source that reads from CSV files"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def fetch_investments(self, days_back: int = 30) -> List[Investment]:
        """Read investments from CSV file"""
        import csv
        from newsletter_factory import InvestmentStage
        
        investments = []
        
        with open(self.filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                investor = Company(
                    name=row['investor_name'],
                    description=row.get('investor_description', ''),
                    sector=row.get('investor_sector', 'VC Firm')
                )
                
                investee = Company(
                    name=row['investee_name'],
                    description=row.get('investee_description', ''),
                    sector=row.get('investee_sector', 'AI')
                )
                
                investment = Investment(
                    investor=investor,
                    investee=investee,
                    amount=float(row['amount']),
                    stage=InvestmentStage[row['stage']],
                    date=datetime.fromisoformat(row['date']),
                    details=row.get('details'),
                    key_insights=row.get('insights', '').split('|') if row.get('insights') else []
                )
                
                investments.append(investment)
        
        return investments
