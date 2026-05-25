import json
from app.models.schemas import QueryRequest, QueryResponse
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(request: Request, query_request: QueryRequest) -> QueryResponse:
    rag_pipeline = request.app.state.rag_pipeline
    result = rag_pipeline.query(query_request.question, query_request.source_file)
    return QueryResponse(answer=result["answer"], sources=result["sources"])

@router.post("/query/stream")
async def query_stream(request: Request, query_request: QueryRequest):
    rag_pipeline = request.app.state.rag_pipeline

    def generate():
        for item in rag_pipeline.query_stream(query_request.question, query_request.source_file):
            if item["type"] == "token":
                yield f"data: {item['data']}\n\n"
            elif item["type"] == "sources":
                yield f"event: sources\ndata: {json.dumps(item['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")