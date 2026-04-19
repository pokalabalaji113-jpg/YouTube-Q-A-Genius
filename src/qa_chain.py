"""
qa_chain.py - Fully Fixed Version
"""
import os
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")


def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=LLM_MODEL or "gpt-4o", temperature=0.3)
    else:
        from langchain_groq import ChatGroq
        return ChatGroq(model=LLM_MODEL or "llama-3.3-70b-versatile", temperature=0.3)


def create_qa_chain(vector_store, video_metadata: dict):
    """Returns a simple dict with vector_store and metadata - no LangChain chain memory issues."""
    return {
        "vector_store": vector_store,
        "metadata": video_metadata,
        "history": []
    }


def ask_question(chain: dict, question: str) -> dict:
    """Direct retrieval + LLM call. No ConversationalRetrievalChain memory bugs."""
    try:
        vector_store = chain["vector_store"]
        history = chain.get("history", [])

        # Retrieve relevant docs
        docs = vector_store.similarity_search(question, k=5)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Build history string
        history_str = ""
        for h in history[-4:]:  # last 4 exchanges
            history_str += f"Human: {h['q']}\nAI: {h['a']}\n"

        # Build prompt
        prompt_text = f"""You are an expert AI assistant analyzing a YouTube video transcript.

Video: {chain['metadata'].get('title', 'Unknown')}
Channel: {chain['metadata'].get('author', 'Unknown')}

Relevant transcript context:
{context}

Recent conversation:
{history_str}

Question: {question}

Answer clearly and in detail based on the transcript. Include timestamps when relevant."""

        llm = get_llm()
        response = llm.invoke(prompt_text)
        answer = response.content if hasattr(response, 'content') else str(response)

        # Save to history
        chain["history"].append({"q": question, "a": answer})

        # Extract source timestamps
        sources = []
        seen = set()
        for doc in docs:
            ts = doc.metadata.get("timestamp", "")
            if ts and ts not in seen:
                seen.add(ts)
                sources.append({"timestamp": ts, "text_preview": doc.page_content[:120] + "..."})

        return {"success": True, "answer": answer, "sources": sources[:4]}

    except Exception as e:
        return {"success": False, "answer": f"Error: {str(e)}", "sources": []}


def generate_video_summary(chain) -> str:
    result = ask_question(chain, """Give a comprehensive summary of this video with:
1. 🎯 Main Topic & Overview (2-3 sentences)
2. 📌 Key Points (5-7 bullet points)
3. 💡 Important Concepts explained
4. ✅ Takeaways for the viewer""")
    return result["answer"]


def generate_quiz(chain, num_questions: int = 5) -> str:
    result = ask_question(chain, f"""Create {num_questions} multiple choice quiz questions based on this video.
Format each as:
Q1: [question]
A) option  B) option  C) option  D) option
✅ Answer: [correct] - [brief explanation]
---""")
    return result["answer"]


def generate_key_points(chain) -> str:
    result = ask_question(chain, """Extract the top 8-10 most important key points from this video.
Format each as:
🔑 Key Point [N]: [title]
📍 Timestamp: [approximate time]
📝 Details: [2-3 sentence explanation]
""")
    return result["answer"]
