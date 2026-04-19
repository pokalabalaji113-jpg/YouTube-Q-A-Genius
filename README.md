# 🎯 YouTube Q&A Genius

> **Ask anything about any YouTube video. Get instant AI-powered answers with timestamps. Export beautiful PDF reports.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red?style=for-the-badge&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-green?style=for-the-badge)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-purple?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 📌 About The Project

**YouTube Q&A Genius** is an AI-powered web application that turns any YouTube video into an interactive knowledge base. Paste a YouTube URL, and the app extracts the transcript, builds a vector search index, and lets you have a full conversation with the video content — with accurate answers, timestamps, summaries, quizzes, and PDF export.

Built as a portfolio project to demonstrate skills in **Generative AI, RAG, LLM Integration, Vector Search, and Full-Stack Python Development.**

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Chat with Video** | Ask any question, get instant AI answers with timestamps |
| 📋 **Auto Summary** | One-click comprehensive video summary |
| 🔑 **Key Points** | Extract top 8-10 insights automatically |
| 🧪 **Quiz Generator** | Auto-generate quiz questions to test knowledge |
| 📜 **Transcript Viewer** | Search and highlight text in full transcript |
| 📄 **PDF Export** | Download your full Q&A session as a report |
| ⚡ **Quick Actions** | One-click Summarize, Main Points, Explain, Best Quote, Study Notes |
| 🌑 **Dark UI** | Beautiful dark purple theme with glassmorphism design |

---

## 🎯 How It Works

```
User pastes YouTube URL
        ↓
yt-dlp extracts transcript with timestamps
        ↓
Transcript split into overlapping chunks (1000 words, 200 overlap)
        ↓
sentence-transformers converts chunks to vector embeddings
        ↓
FAISS stores vectors locally for fast similarity search
        ↓
User asks a question
        ↓
Question converted to embedding → Top 5 similar chunks retrieved
        ↓
Groq LLaMA 3.3 generates answer with context + timestamps
        ↓
Answer displayed with source timestamps in beautiful UI
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Streamlit | Web UI framework |
| FAISS | Vector similarity search (no C++ compiler needed) |
| sentence-transformers | Text embedding generation |
| Groq LLaMA 3.3 70B | AI language model (free & fast) |
| LangChain | LLM orchestration |
| yt-dlp | YouTube transcript extraction |
| fpdf2 | PDF report generation |
| python-dotenv | API key management |

---

## 📁 Project Structure

```
youtube-qa-genius/
│
├── app.py                  ← Main Streamlit app
├── requirements.txt        ← All dependencies
├── .env.example            ← Environment variables template
├── .gitignore
├── README.md
│
├── .streamlit/
│   └── config.toml         ← Dark theme configuration
│
├── src/
│   ├── __init__.py
│   ├── transcript.py       ← YouTube transcript extractor (yt-dlp)
│   ├── embeddings.py       ← FAISS vector store handler
│   ├── qa_chain.py         ← LLM Q&A with context retrieval
│   ├── pdf_generator.py    ← PDF report generator
│   └── utils.py            ← Helper functions
│
├── assets/
│   └── style.css           ← Custom dark UI styling
│
└── vector_db/              ← Auto-created FAISS storage
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- Groq API Key — FREE at [console.groq.com](https://console.groq.com)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/pokalabalaji113-jpg/youtube-qa-genius.git
cd youtube-qa-genius
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
pip install yt-dlp
```

### Step 3 — Setup API Key
Create a `.env` file in the project folder:
```
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
```

🔑 Get your FREE Groq API key at: [console.groq.com](https://console.groq.com)

### Step 4 — Run the App
```bash
streamlit run app.py
```

Open browser at: **http://localhost:8501**

---

## 📊 How to Use

1. **Run** → `streamlit run app.py`
2. **Paste** any YouTube URL in the sidebar
3. **Click** 🚀 Load Video and wait for processing
4. **Ask** anything in the chat tab
5. **Explore** Summary, Key Points, Quiz, Transcript tabs
6. **Export** your full session as a PDF report

---

## 🌐 Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file as `app.py`
5. Add secrets in Advanced Settings:
```
GROQ_API_KEY = "your_key_here"
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.3-70b-versatile"
```
6. Click **Deploy** — your app is live! 🎉

---

## 🧠 AI & RAG Details

| Property | Value |
|---|---|
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS (Facebook AI Similarity Search) |
| Search Type | Semantic similarity search |
| Chunks Retrieved | Top 5 most relevant |
| Chunk Size | 1000 words with 200-word overlap |
| LLM | Groq LLaMA 3.3 70B Versatile |
| Context Window | Last 4 conversation exchanges |

---

## 📈 Skills Demonstrated

- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Vector Database & Semantic Search
- ✅ LLM API Integration & Prompt Engineering
- ✅ Full-Stack Python Development
- ✅ Custom UI Design with CSS
- ✅ PDF Generation
- ✅ Dependency Management & Debugging

---

## ⚠️ Notes

- Only works with YouTube videos that have **captions/subtitles enabled**
- Free Groq API has a **100,000 token/day limit** — resets daily
- Vector database is stored **locally** in `vector_db/` folder
- Previously processed videos are **cached** for faster reload

---

## 👨‍💻 Author

**Pokala Balaji**
GitHub: [@pokalabalaji113-jpg](https://github.com/pokalabalaji113-jpg)

---

## 📄 License

MIT License — free to use, modify and distribute.

---

## 🙏 Acknowledgements

Special thanks to **Manohar Chary .V** Sir and the entire training team for their guidance, feedback and encouragement throughout this project.
