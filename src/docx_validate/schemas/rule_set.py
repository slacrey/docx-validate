from typing import Any

from pydantic import BaseModel, ConfigDict


class RuleSetCreate(BaseModel):
    name: str
    version: str
    rule_json: dict[str, Any]


class RuleSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    rule_json: dict[str, Any]
    status: str
