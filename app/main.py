
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.database import Database
from app.rag.foundry_agent import FoundryAgent
from app.speech.text_to_speech import TextToSpeech
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.database = Database()
    app.state.agent = None
    app.state.tts_service = None

    try:
        app.state.agent = FoundryAgent()
        app.state.tts_service = TextToSpeech()

        print("SQLite database initialized.")
        print("Azure Foundry initialized.")
        print("Azure Speech initialized.")

        yield

    finally:
        if app.state.agent is not None:
            app.state.agent.close()

        print("Application stopped.")


app = FastAPI(
    title="NASA Space Explorer API",
    description=(
        "AI-powered storytelling about abandoned NASA equipment."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")
