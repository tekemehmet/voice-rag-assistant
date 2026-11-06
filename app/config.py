
import os
from dotenv import load_dotenv

load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME")


def validate_config():
    missing = []

    if not FOUNDRY_PROJECT_ENDPOINT:
        missing.append("FOUNDRY_PROJECT_ENDPOINT")

    if not FOUNDRY_AGENT_NAME:
        missing.append("FOUNDRY_AGENT_NAME")

    if missing:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing)}"
        )
