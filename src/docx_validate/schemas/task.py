from pydantic import BaseModel, ConfigDict


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_no: str
    template_id: int
    rule_set_id: int
    input_object_key: str
    status: str
    progress: int
    error_message: str | None
