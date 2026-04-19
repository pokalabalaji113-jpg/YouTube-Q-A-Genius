"""
app.py - YouTube Q&A Genius - Complete Fixed Version
"""
import os, sys, time, tempfile
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="YouTube Q&A Genius",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── LOAD CSS ────────────────────────────────────────────────────────────────
def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

from src.transcript import extract_video_id, get_video_metadata, get_transcript, chunk_transcript
from src.embeddings import create_vector_store, load_vector_store, delete_vector_store, list_stored_videos
from src.qa_chain import create_qa_chain, ask_question, generate_video_summary, generate_quiz, generate_key_points
from src.pdf_generator import generate_qa_pdf
from src.utils import (format_duration, is_valid_youtube_url, get_youtube_embed_url,
                       check_api_keys, get_session_stats, estimate_read_time)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "video_loaded": False, "video_id": None, "video_metadata": {},
        "transcript_data": {}, "vector_store": None, "qa_chain": None,
        "chat_history": [], "summary": None, "key_points": None,
        "quiz_content": None, "show_sources": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# ─── CHAT MESSAGE RENDERER ────────────────────────────────────────────────────
def render_chat_message(role, content, sources=None):
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <div class="msg-label" style="color:#a5b4fc;font-size:0.75rem;font-weight:700;margin-bottom:6px;">👤 YOU</div>
            <div style="color:#f1f5f9;line-height:1.7;font-size:0.97rem;">{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        chips = ""
        if sources and st.session_state.show_sources:
            chips = "".join([f'<span class="source-chip">⏱ {s["timestamp"]}</span>' for s in sources[:4]])
            if chips:
                chips = f'<div style="margin-top:10px;">{chips}</div>'
        # Convert newlines to <br> for proper rendering
        formatted = content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="assistant-message">
            <div class="msg-label" style="color:#34d399;font-size:0.75rem;font-weight:700;margin-bottom:6px;">🤖 AI ASSISTANT</div>
            <div style="color:#e2e8f0;line-height:1.8;font-size:0.97rem;">{formatted}</div>
            {chips}
        </div>""", unsafe_allow_html=True)

# ─── PROCESS VIDEO ────────────────────────────────────────────────────────────
def process_video(url):
    video_id = extract_video_id(url)
    if not video_id:
        st.error("❌ Invalid YouTube URL.")
        return False

    progress = st.progress(0, text="🚀 Starting...")

    # Check cache
    existing = load_vector_store(video_id)
    if existing and st.session_state.get("video_id") == video_id:
        st.session_state.vector_store = existing
        st.session_state.qa_chain = create_qa_chain(existing, st.session_state.video_metadata)
        progress.progress(100, text="✅ Loaded from cache!")
        time.sleep(0.5); progress.empty()
        return True

    progress.progress(15, text="📋 Fetching video info...")
    metadata = get_video_metadata(video_id)
    st.session_state.video_metadata = metadata

    progress.progress(30, text="📝 Extracting transcript...")
    transcript_data = get_transcript(video_id)

    if not transcript_data["success"]:
        st.error(f"❌ {transcript_data.get('error', 'Could not get transcript')}")
        progress.empty()
        return False

    st.session_state.transcript_data = transcript_data
    progress.progress(55, text=f"✅ {transcript_data['word_count']:,} words! Chunking...")

    chunks = chunk_transcript(transcript_data, chunk_size=800, overlap=150)
    progress.progress(70, text=f"🧩 {len(chunks)} chunks. Building embeddings...")

    vector_store = create_vector_store(chunks, video_id, metadata)
    progress.progress(90, text="🧠 Building AI chain...")

    qa_chain = create_qa_chain(vector_store, metadata)

    st.session_state.video_loaded = True
    st.session_state.video_id = video_id
    st.session_state.vector_store = vector_store
    st.session_state.qa_chain = qa_chain
    st.session_state.chat_history = []
    st.session_state.summary = None
    st.session_state.key_points = None
    st.session_state.quiz_content = None

    progress.progress(100, text="🚀 Ready!")
    time.sleep(0.8); progress.empty()
    return True

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 15px 0;">
        <div style="font-size:3rem;">🎯</div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;
                    background:linear-gradient(135deg,#6366f1,#06b6d4);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            YT Q&A Genius
        </div>
        <div style="color:#475569;font-size:0.75rem;margin-top:4px;">Powered by LangChain + FAISS + Groq</div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔗 Video URL")
    url_input = st.text_input("Paste YouTube URL", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")

    if url_input:
        if is_valid_youtube_url(url_input):
            st.success("✅ Valid YouTube URL")
        else:
            st.error("❌ Invalid URL format")

    col1, col2 = st.columns([3, 1])
    with col1:
        load_btn = st.button("🚀 Load Video", use_container_width=True, type="primary")
    with col2:
        if st.session_state.video_loaded:
            if st.button("🔄", help="Clear current video"):
                for k in ["video_loaded","video_id","video_metadata","transcript_data",
                          "vector_store","qa_chain","chat_history","summary","key_points","quiz_content"]:
                    st.session_state[k] = [] if k == "chat_history" else (False if k == "video_loaded" else None)
                st.rerun()

    st.divider()
    st.markdown("### ⚙️ AI Settings")
    api_keys = check_api_keys()
    provider = st.selectbox("LLM Provider", ["groq", "openai"], index=0 if api_keys["provider"] == "groq" else 1)
    os.environ["LLM_PROVIDER"] = provider

    if provider == "groq":
        groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY",""), placeholder="gsk_...")
        if groq_key: os.environ["GROQ_API_KEY"] = groq_key
        model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"])
        os.environ["LLM_MODEL"] = model
        st.markdown('<div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:8px 12px;font-size:0.75rem;color:#6ee7b7;margin-top:8px;">💡 FREE key at <strong>console.groq.com</strong></div>', unsafe_allow_html=True)
    else:
        openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY",""), placeholder="sk-...")
        if openai_key: os.environ["OPENAI_API_KEY"] = openai_key
        model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        os.environ["LLM_MODEL"] = model

    st.divider()
    st.markdown("### 🎛️ Preferences")
    st.session_state.show_sources = st.toggle("Show timestamps", value=True)
    show_embed = st.toggle("Show video player", value=True)

    st.divider()
    stored = list_stored_videos()
    if stored:
        st.markdown(f"### 📚 Cached ({len(stored)})")
        for v in stored[:5]:
            ca, cb = st.columns([3,1])
            with ca: st.markdown(f'<div style="font-size:0.75rem;color:#94a3b8;">{v["video_id"][:18]}...</div>', unsafe_allow_html=True)
            with cb:
                if st.button("🗑", key=f"del_{v['video_id']}"):
                    delete_vector_store(v["video_id"]); st.rerun()

    st.divider()
    st.markdown("### 💡 Example Videos")
    examples = {
        "🧠 Neural Networks": "https://www.youtube.com/watch?v=aircAruvnKk",
        "🐍 Python Course": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
        "📐 Linear Algebra": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
    }
    for label, ex_url in examples.items():
        if st.button(label, use_container_width=True):
            st.session_state["_example_url"] = ex_url; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════
if "_example_url" in st.session_state:
    url_input = st.session_state.pop("_example_url")

if load_btn and url_input:
    success = process_video(url_input)
    if success: st.rerun()

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎯 YouTube Q&A Genius</h1>
    <p>Ask anything about any YouTube video • Instant AI-powered answers • Export PDF reports</p>
    <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:6px;">
        <span class="feature-badge">⚡ Real-time Q&A</span>
        <span class="feature-badge">🧠 RAG + FAISS</span>
        <span class="feature-badge">💬 Conversational AI</span>
        <span class="feature-badge">📄 PDF Export</span>
        <span class="feature-badge">⏱ Timestamps</span>
        <span class="feature-badge">📝 Auto Summary</span>
        <span class="feature-badge">🧪 Quiz Generator</span>
        <span class="feature-badge">🔑 Key Points</span>
    </div>
</div>""", unsafe_allow_html=True)

# ─── LANDING PAGE ─────────────────────────────────────────────────────────────
if not st.session_state.video_loaded:
    st.markdown("""
    <div style="text-align:center;padding:50px 20px;">
        <div style="font-size:5rem;margin-bottom:20px;">🎬</div>
        <h2 style="color:#f1f5f9;font-size:1.8rem;font-weight:700;margin-bottom:12px;">
            Turn Any YouTube Video Into a Knowledge Base
        </h2>
        <p style="color:#64748b;font-size:1rem;line-height:1.7;max-width:500px;margin:0 auto 30px;">
            Paste a YouTube URL → AI extracts transcript → Ask any question → Get instant answers with timestamps
        </p>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "🔍", "Smart Search", "RAG retrieval finds the most relevant parts", "#6366f1"),
        (c2, "💬", "Chat Memory", "AI remembers context across conversation", "#8b5cf6"),
        (c3, "⏱️", "Timestamps", "Every answer links back to exact moments", "#06b6d4"),
        (c4, "📄", "PDF Export", "Download full Q&A session as PDF", "#10b981"),
    ]
    for col, icon, title, desc, color in cards:
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(30,41,59,0.8),rgba(15,23,42,0.9));
                        border:1px solid {color}40;border-radius:16px;padding:24px;text-align:center;
                        height:180px;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{color};"></div>
                <div style="font-size:2rem;margin-bottom:10px;">{icon}</div>
                <div style="font-weight:700;color:#f1f5f9;font-size:0.95rem;margin-bottom:8px;">{title}</div>
                <div style="color:#64748b;font-size:0.8rem;line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("👈 **Get started:** Paste a YouTube URL in the sidebar and click 🚀 Load Video")

# ─── VIDEO LOADED ─────────────────────────────────────────────────────────────
else:
    metadata = st.session_state.video_metadata
    transcript = st.session_state.transcript_data

    # Video info bar
    ic1, ic2 = st.columns([2,1])
    with ic1:
        thumb = metadata.get("thumbnail","")
        title = metadata.get("title","Unknown")
        author = metadata.get("author","Unknown")
        img_html = f"<img src='{thumb}' style='width:130px;border-radius:10px;flex-shrink:0;'/>" if thumb else ""
        st.markdown(f"""
        <div class="video-info-card">
            <div style="display:flex;gap:16px;align-items:flex-start;">
                {img_html}
                <div style="flex:1;">
                    <div class="video-title">{title}</div>
                    <div class="video-author">📺 {author}</div>
                    <div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:6px;">
                        <span style="background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.4);color:#6ee7b7;padding:3px 10px;border-radius:20px;font-size:0.75rem;">✅ Loaded</span>
                        <span style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.4);color:#a5b4fc;padding:3px 10px;border-radius:20px;font-size:0.75rem;">📝 {transcript.get('word_count',0):,} words</span>
                        <span style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);color:#fcd34d;padding:3px 10px;border-radius:20px;font-size:0.75rem;">⏱ {transcript.get('duration_formatted','?')}</span>
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    with ic2:
        stats = get_session_stats(st.session_state.chat_history)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
            <div class="metric-card"><div class="metric-value">{stats['questions_asked']}</div><div class="metric-label">Questions</div></div>
            <div class="metric-card"><div class="metric-value">{transcript.get('word_count',0)//1000}K</div><div class="metric-label">Words</div></div>
            <div class="metric-card" style="grid-column:span 2;"><div class="metric-value" style="font-size:1.3rem;">{transcript.get('duration_formatted','?')}</div><div class="metric-label">Duration</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab_chat, tab_summary, tab_keypoints, tab_quiz, tab_transcript, tab_export = st.tabs([
        "💬 Chat", "📋 Summary", "🔑 Key Points", "🧪 Quiz", "📜 Transcript", "📄 Export PDF"
    ])

    # ══════════════════════════════
    # TAB 1: CHAT
    # ══════════════════════════════
    with tab_chat:
        st.markdown('<div style="color:#a5b4fc;font-weight:600;margin-bottom:10px;">⚡ Quick Actions:</div>', unsafe_allow_html=True)
        qc1,qc2,qc3,qc4,qc5 = st.columns(5)
        quick_map = {
            "🎯 Summarize": "Give me a brief summary of this video in bullet points",
            "💡 Main Points": "What are the 5 most important points in this video?",
            "🤔 Explain": "Explain the main concept of this video in simple terms",
            "🔥 Best Quote": "What is the most memorable or important statement in this video?",
            "📚 Study Notes": "Create detailed study notes for this video with headings and bullet points",
        }
        for col, (label, question) in zip([qc1,qc2,qc3,qc4,qc5], quick_map.items()):
            with col:
                if st.button(label, use_container_width=True, key=f"quick_{label}"):
                    st.session_state["_quick_q"] = question

        st.markdown("<br>", unsafe_allow_html=True)

        # Display chat history
        if not st.session_state.chat_history:
            st.markdown(f"""
            <div style="text-align:center;padding:40px;background:rgba(30,41,59,0.3);
                        border-radius:16px;border:1px dashed rgba(99,102,241,0.3);">
                <div style="font-size:3rem;margin-bottom:12px;">💬</div>
                <div style="color:#94a3b8;font-size:1rem;">
                    Start chatting! Ask anything about<br>
                    <strong style="color:#a5b4fc;">"{title[:60]}"</strong>
                </div>
                <div style="color:#475569;font-size:0.85rem;margin-top:8px;">
                    Try the Quick Action buttons above ☝️
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                render_chat_message(msg["role"], msg["content"], msg.get("sources"))

        st.markdown("<br>", unsafe_allow_html=True)

        # Handle quick question
        default_q = ""
        if "_quick_q" in st.session_state:
            default_q = st.session_state.pop("_quick_q")

        user_input = st.chat_input("Ask anything about the video...")
        question = default_q or user_input

        if question and st.session_state.qa_chain:
            st.session_state.chat_history.append({"role":"user","content":question,"sources":[]})
            with st.spinner("🤖 AI is thinking..."):
                result = ask_question(st.session_state.qa_chain, question)
            st.session_state.chat_history.append({
                "role":"assistant",
                "content": result["answer"],
                "sources": result.get("sources",[])
            })
            st.rerun()

        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.session_state.qa_chain = create_qa_chain(st.session_state.vector_store, st.session_state.video_metadata)
                st.rerun()

    # ══════════════════════════════
    # TAB 2: SUMMARY
    # ══════════════════════════════
    with tab_summary:
        st.markdown('<h3 style="color:#f1f5f9;">📋 AI-Generated Video Summary</h3>', unsafe_allow_html=True)
        if st.session_state.summary is None:
            if st.button("✨ Generate Summary", type="primary", use_container_width=False):
                with st.spinner("🤖 Analyzing the entire video..."):
                    st.session_state.summary = generate_video_summary(st.session_state.qa_chain)
                st.rerun()
        if st.session_state.summary:
            formatted = st.session_state.summary.replace("\n","<br>")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.08));
                        border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:28px;
                        line-height:1.9;color:#e2e8f0;font-size:0.97rem;">
                {formatted}
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Regenerate Summary"):
                st.session_state.summary = None; st.rerun()

    # ══════════════════════════════
    # TAB 3: KEY POINTS
    # ══════════════════════════════
    with tab_keypoints:
        st.markdown('<h3 style="color:#f1f5f9;">🔑 Key Points & Insights</h3>', unsafe_allow_html=True)
        if st.session_state.key_points is None:
            if st.button("✨ Extract Key Points", type="primary", use_container_width=False):
                with st.spinner("🔍 Finding the most important insights..."):
                    st.session_state.key_points = generate_key_points(st.session_state.qa_chain)
                st.rerun()
        if st.session_state.key_points:
            formatted = st.session_state.key_points.replace("\n","<br>")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(16,185,129,0.1),rgba(6,182,212,0.08));
                        border:1px solid rgba(16,185,129,0.3);border-radius:16px;padding:28px;
                        line-height:1.9;color:#e2e8f0;font-size:0.97rem;">
                {formatted}
            </div>""", unsafe_allow_html=True)
            if st.button("🔄 Regenerate Key Points"):
                st.session_state.key_points = None; st.rerun()

    # ══════════════════════════════
    # TAB 4: QUIZ
    # ══════════════════════════════
    with tab_quiz:
        st.markdown('<h3 style="color:#f1f5f9;">🧪 Test Your Knowledge</h3>', unsafe_allow_html=True)
        num_q = st.slider("Number of Questions", 3, 10, 5)
        if st.button("🎯 Generate Quiz", type="primary", use_container_width=False):
            with st.spinner("🧠 Creating quiz questions..."):
                st.session_state.quiz_content = generate_quiz(st.session_state.qa_chain, num_q)
            st.rerun()
        if st.session_state.quiz_content:
            formatted = st.session_state.quiz_content.replace("\n","<br>")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(245,158,11,0.1),rgba(239,68,68,0.06));
                        border:1px solid rgba(245,158,11,0.3);border-radius:16px;padding:28px;
                        line-height:1.9;color:#e2e8f0;font-size:0.97rem;">
                {formatted}
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════
    # TAB 5: TRANSCRIPT
    # ══════════════════════════════
    with tab_transcript:
        st.markdown('<h3 style="color:#f1f5f9;">📜 Video Transcript</h3>', unsafe_allow_html=True)
        if transcript.get("text"):
            tc1,tc2,tc3 = st.columns(3)
            with tc1: st.metric("Words", f"{transcript.get('word_count',0):,}")
            with tc2: st.metric("Duration", transcript.get("duration_formatted","?"))
            with tc3: st.metric("Segments", transcript.get("segment_count",0))
            st.markdown("<br>", unsafe_allow_html=True)
            search = st.text_input("🔍 Search transcript", placeholder="Search for a word or phrase...")
            txt = transcript.get("text","")
            if search:
                highlighted = txt.replace(search, f'<mark style="background:rgba(99,102,241,0.4);color:#f1f5f9;border-radius:3px;padding:0 2px;">{search}</mark>')
                count = txt.lower().count(search.lower())
                st.markdown(f'<div style="color:#10b981;font-size:0.85rem;margin-bottom:8px;">Found {count} occurrence(s)</div>', unsafe_allow_html=True)
                display = highlighted
            else:
                display = txt
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(99,102,241,0.2);
                        border-radius:16px;padding:24px;max-height:500px;overflow-y:auto;
                        color:#94a3b8;font-size:0.9rem;line-height:1.8;">
                {display.replace(chr(10),'<br>')}
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ Download Transcript", data=txt,
                file_name=f"transcript_{st.session_state.video_id}.txt", mime="text/plain")

    # ══════════════════════════════
    # TAB 6: EXPORT PDF
    # ══════════════════════════════
    with tab_export:
        st.markdown('<h3 style="color:#f1f5f9;">📄 Export Q&A Report as PDF</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1));
                    border:1px solid rgba(99,102,241,0.25);border-radius:16px;padding:20px;margin-bottom:20px;">
            <div style="color:#f1f5f9;font-weight:600;margin-bottom:8px;">📋 PDF includes:</div>
            <div style="color:#94a3b8;line-height:1.8;">
                🎬 Video title & channel • 📝 AI Summary • 🔑 Key Points • 💬 Full Q&A • ⏱️ Timestamps
            </div>
        </div>""", unsafe_allow_html=True)

        inc_sum = st.checkbox("Include Summary", value=True)
        inc_kp = st.checkbox("Include Key Points", value=True)
        stats = get_session_stats(st.session_state.chat_history)

        if stats['questions_asked'] == 0 and not st.session_state.summary:
            st.warning("⚠️ Ask some questions or generate a summary first!")
        else:
            if st.button("📥 Generate & Download PDF", type="primary", use_container_width=False):
                with st.spinner("🎨 Creating your PDF report..."):
                    try:
                        chat_for_pdf = [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            pdf_path = tmp.name
                        generate_qa_pdf(
                            video_metadata=st.session_state.video_metadata,
                            chat_history=chat_for_pdf,
                            summary=st.session_state.summary if inc_sum else None,
                            key_points=st.session_state.key_points if inc_kp else None,
                            output_path=pdf_path,
                        )
                        with open(pdf_path,"rb") as f: pdf_bytes = f.read()
                        os.unlink(pdf_path)
                        slug = metadata.get("title","video")[:30].replace(" ","_")
                        st.download_button("⬇️ Download PDF", data=pdf_bytes,
                            file_name=f"YTQnA_{slug}.pdf", mime="application/pdf", use_container_width=True)
                        st.success("✅ PDF ready!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ PDF error: {str(e)}")

    # Video embed
    if show_embed and st.session_state.video_id:
        st.markdown("---")
        st.markdown('<h3 style="color:#f1f5f9;">🎬 Watch the Video</h3>', unsafe_allow_html=True)
        embed_url = get_youtube_embed_url(st.session_state.video_id)
        st.markdown(f"""
        <div style="border-radius:16px;overflow:hidden;border:1px solid rgba(99,102,241,0.3);box-shadow:0 4px 30px rgba(0,0,0,0.4);">
            <iframe width="100%" height="400" src="{embed_url}" frameborder="0" allowfullscreen style="display:block;"></iframe>
        </div>""", unsafe_allow_html=True)
