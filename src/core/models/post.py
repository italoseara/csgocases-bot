from datetime import datetime
from dataclasses import dataclass, field
from typing import Literal, Optional, Any


@dataclass
class Post:
    platform: Literal["Instagram", "X", "Facebook", "Discord"]
    author: str
    text: Optional[str]
    url: str
    media_url: Optional[str]
    created_at: datetime
    raw_data: Optional[dict[str, Any]] = field(default_factory=dict, repr=False)
