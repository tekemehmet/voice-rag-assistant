
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

from app.config import (
    FOUNDRY_PROJECT_ENDPOINT,
    FOUNDRY_AGENT_NAME,
    validate_config,
)


class FoundryAgent:

    def __init__(self):
        validate_config()

        self.credential = DefaultAzureCredential()

        self.project_client = AIProjectClient(
            endpoint=FOUNDRY_PROJECT_ENDPOINT,
            credential=self.credential,
            allow_preview=True,
        )

        self.openai_client = self.project_client.get_openai_client(
            agent_name=FOUNDRY_AGENT_NAME
        )

    def create_conversation(self):
        conversation = self.openai_client.conversations.create()
        return conversation.id

    def ask(self, conversation_id: str, question: str) -> str:
        response = self.openai_client.responses.create(
            conversation=conversation_id,
            input=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
        )

        return response.output_text

    def close(self):
        self.project_client.close()
        self.credential.close()
