from pydantic import BaseModel
from typing import List


class ChunkSummaryResponseSchema(BaseModel):
    summary: str

class TableSchema(BaseModel):
    table_name: str
    columns: List[str]
    rows: List[List[str]]

class TablesSchema(BaseModel):
    tables: List[TableSchema]

class ExtractedTextSchema(BaseModel):
    text: str

class PreProcessingResponseSchema(BaseModel):
    text: str
    tables: List[TableSchema]

class AnalysisResponseSchema(BaseModel):
    analysis: str

