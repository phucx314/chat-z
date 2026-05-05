# Chat-Z (AI Assistant) 🚀

Chat-Z is a modern, highly interactive AI Chatbot project featuring a centralized FastAPI backend with dual frontends: a blazing-fast **Next.js Web App** and a sleek **PyQt6 Native Desktop Client**.

Designed to simulate a highly realistic "human-like" conversation flow, Chat-Z breaks down massive AI text walls into bite-sized, sequential chat bubbles mimicking real-world messaging apps like Messenger or iMessage.

## ✨ Key Features

- **🧠 Multi-Provider LLM Support:** Easily switch between OpenAI (GPT-4o) and Xiaomi MiMo models directly from the UI.
- **💬 Messenger-Style UI:** Dynamic message grouping, conditional avatar rendering, and contextual bubble radii.
- **⏱️ Humanized Typing Simulation:** Calculates reading and typing delays (~80-100 WPM) before rendering each message block.
- **🛑 Interrupt Mechanism (Experimental):** Send a message while the AI is still "typing" to instantly abort its current thought process and force it to respond to your new input.
- **🎨 Cross-Platform Aesthetics:** Both the Web and Native apps share the exact same modern, dark-mode, glass-morphism aesthetic.

## 🏗️ Architecture

- **Backend:** Python + FastAPI + Uvicorn
  - Manages chat history locally (`chat_history.json`)
  - Interacts with LLM Providers.
  - Aggressively normalizes and splits AI responses to force short-form conversational output.
- **Web Frontend:** Next.js + React + Tailwind CSS v4
- **Native Frontend:** Python + PyQt6

---

## 🚀 Getting Started

### 1. Backend Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn httpx pydantic openai python-dotenv

# Start the server (Runs on port 8000)
uvicorn server.main:app --reload
```

### 2. Native Desktop App

```bash
# Ensure PyQt6 is installed
pip install PyQt6

# Run the native app
python main.py
```

### 3. Web App (Next.js)

```bash
cd web-next
npm install

# Start the development server (Runs on port 3000)
npm run dev
```

## ⚙️ Configuration

Create a `.env` file in the root directory for your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
MIMO_API_KEY=your_mimo_key_here
```

Alternatively, you can input your keys directly inside the **Settings** menu of either the Web or Native app. Settings are automatically synced across clients.

## 📄 License
MIT License. Do whatever you want with it! 🎈
