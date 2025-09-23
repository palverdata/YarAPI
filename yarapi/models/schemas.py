from datetime import datetime, timedelta
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum


class DataSource(str, Enum):
    """Allowed data sources for the search."""

    instagram = "instagram"
    facebook = "facebook"
    twitter = "twitter"
    tiktok = "tiktok"
    youtube = "youtube"


class SearchRequest(BaseModel):
    """Model for the search request body."""

    queries: List[str] = Field(..., min_length=1, description="List of search queries.")
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    step_days: int = Field(
        1, gt=0, description="Date pagination interval in days (must be > 0)."
    )
    relative_interval: Optional[str] = Field(
        pattern=r"^\d+[hdmMyY]$",
        description="Relative time interval (e.g., '7d', '1m'). Overrides 'since' and 'until'. Does not work for Twitter.",
        default="7d",
    )
    max_results: int = Field(
        1000, le=10000, description="Maximum number of results (limit 10000)."
    )
    country: str = Field(
        "br",
        description="Country for the search (ISO 3166-1 alpha-2 format). Does not work for Twitter.",
    )
    lang: str = Field(
        "pt",
        description="Language for the search. Does not work for Twitter, pass it on the query as lang:pt.",
    )
    sort: Literal["Top", "Latest"] = Field(
        "Top", description="Sort mode (used only for Twitter)."
    )

    def set_default_until(cls, v):
        return v or datetime.utcnow()

    def set_default_since(cls, v, values):
        if "relative_interval" in values and values["relative_interval"]:
            return None  # Ignore 'since' if 'relative_interval' is provided

        until_date = values.get("until")
        if not until_date:
            until_date = datetime.utcnow()

        return v or (until_date - timedelta(days=7))


class SearchResponse(BaseModel):
    """API response model."""

    status: str = "success"
    results_count: int
    data: List[dict]
