from app.models.schemas import QueryRequest, QueryResponse
from fastapi import APIRouter,Request

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(request: Request, query_request: QueryRequest) -> QueryResponse:
    rag_pipeline = request.app.state.rag_pipeline
    result = rag_pipeline.query(query_request.question, query_request.source_file)
    return QueryResponse(answer=result["answer"], sources=result["sources"])