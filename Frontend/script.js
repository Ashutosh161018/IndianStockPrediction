const backendURL = "http://127.0.0.1:5000/ask";

const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function addMessage(text, sender, chartUrl=null) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    // Avatar
    const avatar = document.createElement("img");
    avatar.classList.add("avatar");
    avatar.src = sender === "bot" ? "assets/bot.png" : "assets/user.png";

    // Text
    const textNode = document.createElement("span");
    textNode.textContent = text;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(textNode);
    chatMessages.appendChild(msgDiv);

    // Chart
    if(chartUrl){
        const img = document.createElement("img");
        img.src = chartUrl;
        img.classList.add("chart");

        // Scroll after image loads
        img.onload = () => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        };

        chatMessages.appendChild(img);
    }

    // Scroll for text-only messages
    if(!chartUrl){
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if(!message) return;

    addMessage(message, "user");
    userInput.value = "";

    addMessage("Typing...", "bot");

    try {
        const res = await fetch(backendURL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ message })
        });
        const data = await res.json();

        // Remove "Typing..."
        const lastMsg = chatMessages.lastChild;
        if(lastMsg && lastMsg.innerText === "Typing...") lastMsg.remove();

        addMessage(data.reply, "bot", data.chart_url);
    } catch(err) {
        console.error(err);
        const lastMsg = chatMessages.lastChild;
        if(lastMsg && lastMsg.innerText === "Typing...") lastMsg.remove();
        addMessage("Error connecting to server.", "bot");
    }
}

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e)=>{
    if(e.key === "Enter") sendMessage();
});

// Welcome message on load
window.onload = () => {
    addMessage("Hello! I am StockTalk AI. Ask me about NSE stocks like Infosys, TCS, Reliance.", "bot");
}
