# 🎯 YouTube Q&A Genius

> Ask anything about any YouTube video. Get instant AI-powered answers with timestamps. Export beautiful PDF reports.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.3%2B-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🔍 **RAG-powered Q&A** — retrieves the most relevant transcript segments
- 💬 **Conversational memory** — AI remembers context across your session
- ⏱️ **Timestamps** — every answer links back to exact video moments
- 📝 **Auto Summary** — one-click comprehensive video summary
- 🔑 **Key Points Extractor** — pull out the top insights
- 🧪 **Quiz Generator** — test your knowledge of the video
- 📜 **Transcript Viewer** — search & highlight text in the full transcript
- 📄 **PDF Export** — download your Q&A session as a beautiful report

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/youtube-qa-genius.git
cd youtube-qa-genius
```

### 2. Install dependencies

> **Windows users:** No C++ compiler needed — the requirements use pre-built wheels.

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your Groq or OpenAI API key
```

Get a **free** Groq API key at [console.groq.com](https://console.groq.com) — no credit card required.

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
youtube-qa-genius/
│
├── app.py                  # Main Streamlit app
├── requirements.txt        # All dependencies
├── .env.example            # Environment variables template
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── transcript.py       # YouTube transcript extractor
│   ├── embeddings.py       # ChromaDB + embeddings handler
│   ├── qa_chain.py         # LangChain QA + conversation chain
│   ├── pdf_generator.py    # PDF report generator
│   └── utils.py            # Helper functions
│
├── assets/
│   └── style.css           # Custom dark-mode UI
│
└── chroma_db/              # Auto-created vector DB storage
```

---

## ⚙️ Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | `groq` or `openai` | `groq` |
| `GROQ_API_KEY` | Your Groq API key | — |
| `OPENAI_API_KEY` | Your OpenAI API key | — |
| `LLM_MODEL` | Model name | `llama3-70b-8192` |
| `CHROMA_DB_DIR` | ChromaDB storage path | `./chroma_db` |

---

## 🛠️ Dependency Notes

| Package | Reason for version choice |
|---|---|
| `chromadb>=0.5.3` | Ships pre-built `hnswlib` wheels — no C++ compiler needed on Windows |
| `pytubefix>=7.0.0` | Drop-in replacement for `pytube` (abandoned/broken since 2024) |
| `langchain>=0.3.0` | Required for `chain.invoke()` API and updated import paths |
| `langchain-core` | Provides `ChatPromptTemplate` in the new location |

---

## 📸 Screenshot

> Paste a YouTube URL → AI processes the transcript → Chat with the video!

---

## 🤝 Contributing

PRs welcome! Please open an issue first to discuss major changes.

---

## 📄 License

MIT © 2024
