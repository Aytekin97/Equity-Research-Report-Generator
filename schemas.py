from pydantic import BaseModel


class ChunkSummaryResponseSchema(BaseModel):
    summary: str

class PreProcessingResponseSchema(BaseModel):
    text: str
    tables: list[dict[str, list[list[str]]]]