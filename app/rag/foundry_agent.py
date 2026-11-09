
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

    @staticmethod
    def get_value(obj, key, default=None):
        """Read a field from either a dictionary or an SDK object."""

        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(obj, key, default)

    def create_conversation(self):
        conversation = self.openai_client.conversations.create()
        return conversation.id

    def extract_citations(self, response):
        citations = []
        seen = set()

        output_items = self.get_value(response, "output", []) or []

        for output_item in output_items:

            if self.get_value(output_item, "type") != "message":
                continue

            content_items = self.get_value(
                output_item,
                "content",
                [],
            ) or []

            for content_item in content_items:

                annotations = self.get_value(
                    content_item,
                    "annotations",
                    [],
                ) or []

                for annotation in annotations:

                    annotation_type = self.get_value(
                        annotation,
                        "type",
                    )

                    if annotation_type != "file_citation":
                        continue

                    filename = self.get_value(
                        annotation,
                        "filename",
                    )

                    file_id = self.get_value(
                        annotation,
                        "file_id",
                    )

                    citation_index = self.get_value(
                        annotation,
                        "index",
                    )

                    citation_key = (file_id, filename)

                    if citation_key in seen:
                        continue

                    seen.add(citation_key)

                    citations.append({
                        "type": "file_citation",
                        "filename": filename or "Source document",
                        "file_id": file_id,
                        "index": citation_index,
                    })

        return citations

    def ask(self, conversation_id: str, question: str) -> dict:

        response = self.openai_client.responses.create(
            conversation=conversation_id,
            input=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
        )

        return {
            "answer": response.output_text,
            "citations": self.extract_citations(response),
        }

    def close(self):
        self.project_client.close()
        self.credential.close()
