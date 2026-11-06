
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main():
    load_dotenv()

    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    agent_name = os.getenv("FOUNDRY_AGENT_NAME")

    if not endpoint or not agent_name:
        raise ValueError(
            "Missing FOUNDRY_PROJECT_ENDPOINT or FOUNDRY_AGENT_NAME in .env"
        )

    user_message = """
    Please analyze the PDF document uploaded to your File Search tool.

    Tell me:
    1. What is this document about?
    2. What are its five most important points?
    3. Which parts of the document support your answer?

    Use the uploaded document as your primary source.
    Do not invent information.
    """

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
            allow_preview=True,
        ) as project_client,
    ):
        # Connect directly to our existing Foundry Agent
        with project_client.get_openai_client(
            agent_name=agent_name
        ) as openai_client:

            # Create a conversation
            conversation = openai_client.conversations.create()

            # Send the question to the Agent
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=[
                    {
                        "role": "user",
                        "content": user_message,
                    }
                ],
            )

            print("\n===== AGENT RESPONSE =====\n")
            print(response.output_text)

            print("\n===== TOOL EXECUTION =====\n")

            for item in response.output:
                if item.type == "file_search_call":
                    print(f"File Search status: {item.status}")


if __name__ == "__main__":
    main()
