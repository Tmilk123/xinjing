from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chat import ChatMessage, ChatSession
from app.schemas.chat import ChatMessageCreateRequest, ChatMessageOut, ChatSessionOut, CreateChatSessionRequest

router = APIRouter(prefix="/chat", tags=["chat"])


DEFAULT_REPLY_MAP = {
    "压力": "听起来你最近压力比较大。可以先告诉我压力最主要来自哪一件事，我们一起拆开看。",
    "睡": "睡眠会直接影响情绪。我们可以先做一个两分钟呼吸放松，然后再看你的入睡习惯。",
    "低落": "谢谢你愿意说出来。你现在不是一个人，我会陪你把这种感受慢慢说清楚。",
    "焦虑": "焦虑通常会让大脑一直高速运转。我们先把最担心的三件事写出来，再一件件处理。",
}


def build_agent_reply(text: str) -> str:
    normalized = text.strip()
    for keyword, reply in DEFAULT_REPLY_MAP.items():
        if keyword in normalized:
            return reply
    return "我收到了你的感受。你可以再多说一点最近最困扰你的场景，我会继续陪你梳理。"


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_chat_session(payload: CreateChatSessionRequest, db: Session = Depends(get_db)) -> ChatSession:
    row = ChatSession(
        user_id=payload.user_id,
        evaluation_session_id=payload.evaluation_session_id,
        session_topic=payload.session_topic or "日常陪伴",
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_chat_sessions(
    user_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ChatSession]:
    query = db.query(ChatSession)
    if user_id is not None:
        query = query.filter(ChatSession.user_id == user_id)
    rows = query.order_by(ChatSession.created_at.desc(), ChatSession.id.desc()).limit(limit).all()
    return rows


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
def get_chat_session(session_id: int, db: Session = Depends(get_db)) -> ChatSession:
    row = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return row


@router.patch("/sessions/{session_id}/close", response_model=ChatSessionOut)
def close_chat_session(session_id: int, db: Session = Depends(get_db)) -> ChatSession:
    row = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Chat session not found")

    row.status = "ended"
    row.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


@router.post("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def add_chat_message(
    session_id: int,
    payload: ChatMessageCreateRequest,
    db: Session = Depends(get_db),
) -> list[ChatMessage]:
    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    if chat_session.status != "active":
        raise HTTPException(status_code=409, detail="Chat session is not active")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    incoming = ChatMessage(
        chat_session_id=session_id,
        sender_type=payload.sender_type or "user",
        content=content,
        message_type=payload.message_type or "text",
    )
    db.add(incoming)
    db.flush()

    if incoming.sender_type == "user":
        reply = ChatMessage(
            chat_session_id=session_id,
            sender_type="agent",
            content=build_agent_reply(content),
            message_type="text",
        )
        db.add(reply)

    db.commit()

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return rows


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def list_chat_messages(session_id: int, db: Session = Depends(get_db)) -> list[ChatMessage]:
    chat_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_session_id == session_id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return rows
