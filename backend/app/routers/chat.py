from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..agent.agent import run_agent
from ..db import get_session
from ..llm.factory import get_provider
from ..schemas import ChatRequest, ChatResponse, ToolCallTrace

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    provider = get_provider()
    result = run_agent(
        provider,
        session,
        message=req.message,
        history=[turn.model_dump() for turn in req.history],
    )
    return ChatResponse(
        answer=result.answer,
        tool_calls=[
            ToolCallTrace(name=t.name, arguments=t.arguments, result_preview=t.result_preview)
            for t in result.traces
        ],
    )
