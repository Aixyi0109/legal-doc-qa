from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    source_file: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]    