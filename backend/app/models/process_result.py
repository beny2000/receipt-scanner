from pydantic import BaseModel


class ProcessResult(BaseModel):
    message: str