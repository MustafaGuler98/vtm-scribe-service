from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

# Even though we dont need all for the PDF, we must match the JSON structure
# sent by the backend to avoid validation errors.
# If you use another source to fill the pdf, change below.
class ReferenceData(BaseModel):
    id: str = ""
    name: str = ""
    description: Optional[str] = ""

# Mirrors the structure of the C# 'Character' class.
class CharacterRequest(BaseModel):
    name: str = Field(default="Unknown Kindred", description="The name of the character.")
    player: Optional[str] = Field(default="", description="The name of the player.")
    chronicle: Optional[str] = Field(default="", description="The name of the chronicle.")
    sire: Optional[str] = Field(default="", description="The name of the character's sire.")
    
    # Nested Objects
    concept: Optional[ReferenceData] = None
    clan: Optional[ReferenceData] = None
    nature: Optional[ReferenceData] = None
    demeanor: Optional[ReferenceData] = None
    
    # Vital Statistics
    generation: int = Field(default=13, ge=4, le=13, description="Vampiric generation.")
    age: Optional[int] = 0
    ageCategory: Optional[str] = ""
    bloodPointsPerTurn: int = 1
    maximumBloodPool: int = 10
    totalExperience: int = 0
    spentExperience: int = 0
    
    # Dictionary Mappings
    attributes: Dict[str, int] = Field(default_factory=dict)
    abilities: Dict[str, int] = Field(default_factory=dict)
    disciplines: Dict[str, int] = Field(default_factory=dict)
    backgrounds: Dict[str, int] = Field(default_factory=dict)
    virtues: Dict[str, int] = Field(default_factory=dict)
    
    # Trackers
    humanity: int = Field(default=7, ge=0, le=10)
    willpower: int = Field(default=6, ge=0, le=10)

    class Config:
        # Example
        json_schema_extra = {
            "example": {
                "name": "Theo Bell",
                "player": "Justin",
                "chronicle": "Nights of Prophecy",
                "clan": {"id": "brujah", "name": "Brujah"},
                "nature": {"id": "rebel", "name": "Rebel"},
                "demeanor": {"id": "soldier", "name": "Soldier"},
                "generation": 9,
                "attributes": {"strength": 4, "dexterity": 3, "stamina": 3, "charisma": 4},
                "abilities": {"brawl": 4, "streetwise": 3, "intimidation": 3},
                "disciplines": {"celerity": 2, "potence": 3},
                "humanity": 7,
                "willpower": 6
            }
        }