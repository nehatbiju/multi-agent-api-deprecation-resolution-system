from pydantic import BaseModel
from datetime import date
from typing import List


class DeprecationNotice(BaseModel):
    provider: str
    old_api_name: str
    new_api_name: str
    deadline: date
    breaking_changes: List[str]


class ResearchSummary(BaseModel):
    migration_guide_url: str
    schema_changes: str
    pricing_changes: str
    performance_notes: str