
const chatArea = document.getElementById("chatArea");
const userInput = document.getElementById("userInput");
const sendButton = document.getElementById("sendButton");

let welcomeScreen = document.getElementById("welcomeScreen");

function hideWelcome() {
    if (welcomeScreen) {
        welcomeScreen.remove();
        welcomeScreen = null;
    }
}

function addMessage(message, sender) {
    hideWelcome();

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageDiv.classList.add(
        sender === "user" ? "user-message" : "bot-message"
    );

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = sender === "user" ? "👨‍🌾" : "🌱";

    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = message;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatArea.appendChild(messageDiv);

    chatArea.scrollTop = chatArea.scrollHeight;

    return messageDiv;
}

async function sendMessage() {

    console.log("Send button clicked!");

    const message = userInput.value.trim();

    console.log("Message:", message);

    if (!message) return;

    addMessage(message, "user");

    userInput.value = "";
    userInput.style.height = "auto";

    sendButton.disabled = true;

    const loadingMessage = addMessage(
        "AgriSathi is thinking...",
        "bot"
    );

    try {

        console.log("Sending request to Flask...");

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        console.log("Response status:", response.status);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        loadingMessage.querySelector(
            ".message-content"
        ).textContent = data.reply;

    } catch (error) {

        console.error("Chatbot error:", error);

        loadingMessage.querySelector(
            ".message-content"
        ).textContent = "Error: " + error.message;

    } finally {

        sendButton.disabled = false;
        userInput.focus();
        chatArea.scrollTop = chatArea.scrollHeight;

    }
}

function askQuestion(question) {
    userInput.value = question;
    sendMessage();
}

function handleKey(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function clearChat() {

    try {

        const response = await fetch("/clear-chat", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Unable to clear conversation.");
        }

        chatArea.innerHTML = "";

        welcomeScreen = document.createElement("div");
        welcomeScreen.id = "welcomeScreen";
        welcomeScreen.className = "welcome-screen";

        welcomeScreen.innerHTML = `
            <div class="welcome-icon">🌱</div>
            <h1>Welcome to AgriSathi</h1>
            <p>Your smart farming assistant. Ask any agriculture-related question.</p>
        `;

        chatArea.appendChild(welcomeScreen);

    } catch (error) {
        console.error(error);
        alert(error.message);
    }
}

userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
});
