
import streamlit as st

from app.rag.foundry_agent import FoundryAgent


st.set_page_config(
    page_title="Voice RAG Assistant",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ Voice RAG Assistant")
st.caption("Ask questions about your uploaded PDF documents.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "agent" not in st.session_state:
    st.session_state.agent = None

# Initialize agent
if st.session_state.agent is None:
    try:
        st.session_state.agent = FoundryAgent()
        st.session_state.conversation_id = (
            st.session_state.agent.create_conversation()
        )
    except Exception as error:
        st.error(f"Could not connect to Azure Foundry: {error}")
        st.stop()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
question = st.chat_input("Ask something about your documents...")

if question:
    # Display user question
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                answer = st.session_state.agent.ask(
                    st.session_state.conversation_id,
                    question,
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:
                st.error(f"Error communicating with Foundry: {error}")
