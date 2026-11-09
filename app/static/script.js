
const API_BASE = "/api";
const STORAGE_KEY = "nasa_space_explorer_conversation";

let conversationId = localStorage.getItem(STORAGE_KEY);

const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question-input");
const chatMessages = document.getElementById("chat-messages");
const loadingIndicator = document.getElementById("loading-indicator");
const sendButton = document.getElementById("send-button");
const newChatButton = document.getElementById("new-chat-button");


function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function showError(message) {
    const element = document.createElement("div");
    element.className = "message";

    const content = document.createElement("div");
    content.className = "assistant-bubble";
    content.style.color = "#ff8888";
    content.textContent = `Error: ${message}`;

    element.appendChild(content);
    chatMessages.appendChild(element);

    scrollToBottom();
}


function addUserMessage(text) {
    const message = document.createElement("div");
    message.className = "message user";

    const bubble = document.createElement("div");
    bubble.className = "user-bubble";
    bubble.textContent = text;

    message.appendChild(bubble);
    chatMessages.appendChild(message);

    scrollToBottom();
}


function addAssistantMessage(answer, citations = [], audioBase64 = null, audioError = null) {
    const message = document.createElement("div");
    message.className = "message";

    const avatar = document.createElement("div");
    avatar.className = "assistant-avatar";
    avatar.textContent = "🪐";

    const content = document.createElement("div");
    content.className = "assistant-bubble";

    const answerText = document.createElement("p");
    answerText.textContent = answer;

    content.appendChild(answerText);

    // Render actual file citations returned by Foundry.
    if (citations && citations.length > 0) {
        const sources = document.createElement("div");
        sources.className = "sources";

        const heading = document.createElement("h4");
        heading.textContent = "📚 Sources";
        sources.appendChild(heading);

        const list = document.createElement("ul");

        citations.forEach((citation) => {
            const item = document.createElement("li");
            item.textContent = citation.filename || "Source document";
            list.appendChild(item);
        });

        sources.appendChild(list);
        content.appendChild(sources);
    }

    // Render audio when available.
    if (audioBase64) {
        const label = document.createElement("div");
        label.className = "audio-label";
        label.textContent = "🔊 Listen to the answer";

        const audio = document.createElement("audio");
        audio.className = "audio-player";
        audio.controls = true;
        audio.preload = "none";
        audio.src = `data:audio/mp3;base64,${audioBase64}`;

        content.appendChild(label);
        content.appendChild(audio);

    } else if (audioError) {
        const warning = document.createElement("p");
        warning.className = "audio-label";
        warning.textContent = "Voice generation is temporarily unavailable.";
        content.appendChild(warning);
    }

    message.appendChild(avatar);
    message.appendChild(content);

    chatMessages.appendChild(message);

    scrollToBottom();
}


async function createConversation() {
    const response = await fetch(`${API_BASE}/conversations`, {
        method: "POST"
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Could not create conversation.");
    }

    conversationId = data.conversation_id;

    localStorage.setItem(STORAGE_KEY, conversationId);

    return conversationId;
}


async function restoreConversation() {
    if (!conversationId) {
        return false;
    }

    const response = await fetch(
        `${API_BASE}/conversations/${encodeURIComponent(conversationId)}/messages`
    );

    if (response.status === 404) {
        localStorage.removeItem(STORAGE_KEY);
        conversationId = null;
        return false;
    }

    if (!response.ok) {
        throw new Error("Could not restore conversation history.");
    }

    const data = await response.json();

    chatMessages.innerHTML = "";

    data.messages.forEach((message) => {
        if (message.role === "user") {
            addUserMessage(message.content);
        } else if (message.role === "assistant") {
            addAssistantMessage(
                message.content,
                message.citations || []
            );
        }
    });

    return true;
}


async function sendQuestion(question) {
    question = question.trim();

    if (!question || sendButton.disabled) {
        return;
    }

    sendButton.disabled = true;
    questionInput.disabled = true;

    addUserMessage(question);
    questionInput.value = "";

    loadingIndicator.classList.remove("hidden");

    try {
        if (!conversationId) {
            await createConversation();
        }

        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                conversation_id: conversationId,
                question: question
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong.");
        }

        addAssistantMessage(
            data.answer,
            data.citations,
            data.audio_base64,
            data.audio_error
        );

    } catch (error) {
        showError(error.message);

    } finally {
        loadingIndicator.classList.add("hidden");
        sendButton.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}


// Question form
chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await sendQuestion(questionInput.value);
});


// Start a new conversation
newChatButton.addEventListener("click", async () => {
    if (sendButton.disabled) {
        return;
    }

    newChatButton.disabled = true;

    try {
        await createConversation();

        chatMessages.innerHTML = "";

        const welcome = document.createElement("div");
        welcome.className = "welcome-message";

        const avatar = document.createElement("div");
        avatar.className = "assistant-avatar";
        avatar.textContent = "🪐";

        const content = document.createElement("div");
        content.className = "message-content";

        const heading = document.createElement("h3");
        heading.textContent = "New exploration started!";

        const paragraph = document.createElement("p");
        paragraph.textContent =
            "What would you like to discover about NASA's missions?";

        content.appendChild(heading);
        content.appendChild(paragraph);

        welcome.appendChild(avatar);
        welcome.appendChild(content);

        chatMessages.appendChild(welcome);

        questionInput.focus();

    } catch (error) {
        showError(error.message);

    } finally {
        newChatButton.disabled = false;
    }
});


// Suggested questions
document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", async () => {
        await sendQuestion(button.textContent);
    });
});


// Application startup
async function initializeApp() {
    questionInput.disabled = true;
    sendButton.disabled = true;

    try {
        const restored = await restoreConversation();

        if (!restored) {
            await createConversation();
        }

    } catch (error) {
        showError(error.message);

    } finally {
        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.focus();
    }
}


initializeApp();
