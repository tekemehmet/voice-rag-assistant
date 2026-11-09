
import base64

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api", tags=["API"])


class ChatRequest(BaseModel):
    conversation_id: str
    question: str = Field(min_length=1, max_length=4000)


@router.get("/health")
def health(request: Request):
    return {
        "status": "healthy",
        "foundry_ready": request.app.state.agent is not None,
        "speech_ready": request.app.state.tts_service is not None,
    }


@router.post("/conversations")
def create_conversation(request: Request):
    try:
        conversation_id = (
            request.app.state.agent.create_conversation()
        )

        request.app.state.database.create_conversation(
            conversation_id
        )

        return {
            "conversation_id": conversation_id
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not create conversation: {error}",
        )


@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str,
    request: Request,
):
    database = request.app.state.database

    if not database.conversation_exists(conversation_id):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return {
        "conversation_id": conversation_id,
        "messages": database.get_messages(conversation_id),
    }


@router.post("/chat")
def chat(payload: ChatRequest, request: Request):

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    database = request.app.state.database

    if not database.conversation_exists(payload.conversation_id):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found. Please start a new conversation.",
        )

    # Save the question before calling Foundry.
    database.add_message(
        payload.conversation_id,
        "user",
        question,
    )

    try:
        result = request.app.state.agent.ask(
            payload.conversation_id,
            question,
        )

        answer = result["answer"]
        citations = result["citations"]

        database.add_message(
            payload.conversation_id,
            "assistant",
            answer,
            citations,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Foundry request failed: {error}",
        )

    # Voice is optional. Preserve the answer if TTS fails.
    audio_base64 = None
    audio_error = None

    try:
        audio_bytes = request.app.state.tts_service.synthesize(answer)

        audio_base64 = base64.b64encode(
            audio_bytes
        ).decode("utf-8")

    except Exception as error:
        audio_error = str(error)

    return {
        "conversation_id": payload.conversation_id,
        "question": question,
        "answer": answer,
        "citations": citations,
        "audio_base64": audio_base64,
        "audio_error": audio_error,
    }
