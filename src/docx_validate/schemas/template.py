from pydantic import BaseModel, ConfigDict


class TemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    status: str
    object_key: str
    file_name: str
    file_size: int
    content_hash: str
    metadata_json: dict[str, object]
