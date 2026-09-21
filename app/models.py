from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RequestModel(BaseModel):
    # The PDF service is a tolerant consumer so older and newer Elysium payloads remain compatible.
    model_config = ConfigDict(extra="ignore")


class Affinity(RequestModel):
    tag: Optional[str] = ""
    value: Optional[int] = 0
    targetType: Optional[str] = None
    targetId: Optional[str] = None


class ReferenceData(RequestModel):
    id: str = ""
    name: str = ""
    description: Optional[str] = ""
    tags: Optional[List[str]] = Field(default_factory=list)
    affinities: Optional[List[Affinity]] = Field(default_factory=list)


class ClanData(ReferenceData):
    nickname: Optional[str] = ""
    disciplines: Optional[List[str]] = Field(default_factory=list)
    weakness: Optional[str] = ""


class TraitData(ReferenceData):
    cost: Optional[int] = 0
    rarity: Optional[int] = 3
    conflictingTraits: Optional[List[str]] = Field(default_factory=list)


class MeritData(TraitData):
    pass


class FlawData(TraitData):
    pass


# Mirrors the structure of the C# 'Character' class.
class CharacterRequest(RequestModel):
    name: str = Field(default="Unknown Kindred", description="The name of the character.")
    player: Optional[str] = Field(default="", description="The name of the player.")
    chronicle: Optional[str] = Field(default="", description="The name of the chronicle.")
    sire: Optional[str] = Field(default="", description="The name of the character's sire.")
    
    # Nested Objects
    concept: Optional[ReferenceData] = None
    clan: Optional[ClanData] = None
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
    maxTraitRating: int = 5
    
    # Dictionary Mappings
    attributes: Dict[str, int] = Field(default_factory=dict)
    abilities: Dict[str, int] = Field(default_factory=dict)
    disciplines: Dict[str, int] = Field(default_factory=dict)
    backgrounds: Dict[str, int] = Field(default_factory=dict)
    virtues: Dict[str, int] = Field(default_factory=dict)
    
    # Trackers
    humanity: int = Field(default=7, ge=0, le=10)
    willpower: int = Field(default=6, ge=0, le=10)

    # Lists (Merits/Flaws)
    # Added to prevent validation errors when C# sends these lists
    merits: Optional[List[MeritData]] = Field(default_factory=list)
    flaws: Optional[List[FlawData]] = Field(default_factory=list)
    debugLog: Optional[List[str]] = Field(default_factory=list)

    model_config = ConfigDict(
        extra="ignore",
        json_schema_extra={
            "example": {
                "name": "Theo Bell",
                "player": "Justin",
                "chronicle": "Nights of Prophecy",
                "clan": {
                    "id": "brujah",
                    "name": "Brujah",
                    "nickname": "Rabble",
                    "disciplines": ["celerity", "potence", "presence"],
                    "weakness": "Difficulties to resist frenzy are increased by two."
                },
                "nature": {"id": "rebel", "name": "Rebel"},
                "demeanor": {"id": "soldier", "name": "Soldier"},
                "generation": 9,
                "attributes": {"strength": 4, "dexterity": 3, "stamina": 3, "charisma": 4},
                "abilities": {"brawl": 4, "streetwise": 3, "intimidation": 3},
                "disciplines": {"celerity": 2, "potence": 3},
                "humanity": 7,
                "willpower": 6
            }
        },
    )
