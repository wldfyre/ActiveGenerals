"""
Data models for Evony Active Generals Tracker
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json

@dataclass
class General:
    """Represents a single general's data"""

    # Core fields from main details screen
    name: str = ""
    level: Optional[int] = None
    type: str = ""  # e.g., "Ground", "Mounted", "Ranged", "Siege"
    type_image: bytes = b""  # Image of the type icon
    power: Optional[int] = None
    exp_ratio: str = ""  # e.g., "1250/2000"
    stars_image: bytes = b""

    # Concatenated data from subscreens (stored as CRLF-separated strings)
    cultivation_data: str = ""  # "Leadership: 85+15\nAttack: 92+1\nDefense: 78+7\nPolitics: 81-3"
    specialty_data: str = ""    # "'Specialty1 Icon'+' '+'Specialty1 Name'\n'Specialty2 Icon'+' '+'Specialty2 Name'\n..."
    covenant_data: str = ""     # "'Covenant1 Icon'+' '+'Covenant1 Name'\n'Covenant2 Icon'+' '+'Covenant2 Name'\n..."

    # Metadata
    confidence_scores: Optional[Dict[str, float]] = None
    is_uncertain: bool = False
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        # Convert datetime to ISO string
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'General':
        """Create from dictionary"""
        # Convert ISO string back to datetime
        if 'timestamp' in data and data['timestamp']:
            try:
                data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            except (ValueError, TypeError):
                data['timestamp'] = datetime.now()
        return cls(**data)

    def get_average_confidence(self) -> float:
        """Get average confidence score across all fields"""
        if not self.confidence_scores:
            return 0.0
        scores = [score for score in self.confidence_scores.values() if score is not None]
        return sum(scores) / len(scores) if scores else 0.0

    def __str__(self) -> str:
        return f"General(name='{self.name}', level={self.level}, power={self.power}, uncertain={self.is_uncertain})"