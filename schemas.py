from pydantic import BaseModel


class ChunkSummaryResponseSchema(BaseModel):
    summary: str