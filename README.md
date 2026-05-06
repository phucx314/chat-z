# Chat-Z (AI Assistant) 🚀

Chat-Z is a modern, highly interactive AI Chatbot project featuring a modular architecture with clean domain separation.

## 🏗️ Project Structure ("Rạch ròi 4 phương")

The project is strictly separated into 4 distinct domains to ensure clean architecture and scalability:

- **📂 backend/**: The core FastAPI server. Handles session persistence, configuration management, and API routing.
  - Data is stored in the `data/` directory.
- **📂 frontend/**: The modern Web interface built with Next.js, React, and Tailwind CSS.
- **📂 native/**: The sleek Desktop client built with PyQt6. Decoupled from the file system; communicates solely via HTTP with the backend.
- **📂 ai/**: The centralized AI engine. Contains LLM provider logic, system prompts, and response normalization. Both the backend and native app (optionally) can leverage this logic.

## ✨ Key Features

- **🧠 Multi-Provider LLM Support:** Switch between OpenAI and MiMo models via UI.
- **💬 Messenger-Style UI:** Dynamic message grouping and contextual bubbles.
- **⏱️ Humanized Typing:** Realistic delay simulation for a better chat feel.
- **🛑 Interrupt Mechanism:** Barge in while the AI is typing to override history.

---

## 🚀 Getting Started

### 1. Backend Setup
```bash
# Install dependencies
pip install fastapi uvicorn httpx pydantic openai python-dotenv

# Start the server (Runs on port 8000)
python backend/main.py
```

### 2. Native Desktop App
```bash
# Ensure PyQt6 is installed
pip install PyQt6

# Run the native app (Connects to backend on port 8000)
python native/main.py
```

### 3. Web App (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## ⚙️ Configuration

Create a `.env` file in the root for your API keys:
```env
OPENAI_API_KEY=sk-...
MIMO_API_KEY=mimo-...
```

## 📄 License
MIT License. 🎈
