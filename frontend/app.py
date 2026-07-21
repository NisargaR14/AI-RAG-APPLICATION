import streamlit as st
import requests, json, os, uuid
from datetime import datetime

API_URL = "http://127.0.0.1:8000"
CHAT_FILE = "chat_history.json"

st.set_page_config(page_title="Enterprise Document Intelligence Core", page_icon="⚡", layout="wide")

# Storage helpers
def load_chats():
    return json.load(open(CHAT_FILE)) if os.path.exists(CHAT_FILE) else {}

def save_chats(chats):
    json.dump(chats, open(CHAT_FILE, "w"), indent=2)

# CSS Styling (Restores Image 1 Look)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
    html, body, [class*="css"] { 
            font-family: 'Inter', sans-serif;
             }
    .stApp { 
            background-color: #0d0e11; 
            color: #e2e8f0; 
            }
    .hero-container {
             padding: 1rem 0 1.5rem 0; 
            border-bottom: 1px solid #1e222d; 
            margin-bottom: 1.5rem; 
            }
    .hero-title { 
            font-size: 1.8rem; 
            font-weight: 700; 
            color: #f8fafc; 
            display: flex;
            align-items: center; 
            gap: 0.5rem; 
            }
    .hero-badge {
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8; 
            font-size: 0.75rem; 
            font-weight: 600; 
            padding: 0.2rem 0.6rem; 
            border-radius: 9999px; 
            border: 1px solid rgba(129, 140, 248, 0.3); 
            }
    .source-box {
             background-color: #161922; 
            border: 1px solid #262b3a; 
            border-radius: 8px; 
            padding: 12px; 
            margin-top: 8px; 
            font-size: 0.85rem; 
            color: #cbd5e1;
             }
    section[data-testid="stSidebar"] {
             background-color: #12141a !important;
             border-right: 1px solid #1e222d;
             }
    </style>
""", unsafe_allow_html=True)

# State Management
chats = load_chats()
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
    chats[st.session_state.chat_id] = {"title": f"New Chat ({datetime.now().strftime('%H:%M')})", "messages": []}
    save_chats(chats)

curr_chat = chats.get(st.session_state.chat_id, {"title": "New Chat", "messages": []})

# Sidebar - Document Ingestion & Recent Chats
with st.sidebar:
    st.markdown("### 🗂️ Document Ingestion")
    file = st.file_uploader("Select PDF", type=["pdf"], label_visibility="collapsed")
    if file and st.button("⚡ Index Document", use_container_width=True, type="primary"):
        res = requests.post(f"{API_URL}/upload", files={"file": (file.name, file.getvalue(), "application/pdf")})
        if res.status_code == 200:
            st.toast("PDF successfully vectorized!", icon="✨")
        else:
            st.error("Upload failed.")

    st.markdown("---")
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        chats[new_id] = {"title": f"New Chat ({datetime.now().strftime('%H:%M')})", "messages": []}
        save_chats(chats)
        st.session_state.chat_id = new_id
        st.rerun()

    st.markdown("### 💬 Recent Chats")
    for cid, data in reversed(list(chats.items())):
        is_active = (cid == st.session_state.chat_id)
        col1, col2 = st.columns([5, 1])
        if col1.button(f"{'👉 ' if is_active else '📄 '} {data.get('title', 'Chat')[:18]}", key=f"s_{cid}", use_container_width=True):
            st.session_state.chat_id = cid
            st.rerun()
        if col2.button("🗑️", key=f"d_{cid}"):
            del chats[cid]
            save_chats(chats)
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear All Chats", use_container_width=True):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        st.session_state.clear()
        st.rerun()

# Hero Header
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Enterprise Document Intelligence Core <span class="hero-badge">RAG Active</span></div>
        <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.4rem;">Autonomous vector search & real-time contextual synthesis across domain documents.</div>
    </div>
""", unsafe_allow_html=True)

# Render Messages
for msg in curr_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 Verified Context Citations"):
                for idx, src in enumerate(msg["sources"], 1):
                    st.markdown(f'<div class="source-box"><b>Chunk {idx}:</b> {src}</div>', unsafe_allow_html=True)

# User Chat Input & Query Execution
if prompt := st.chat_input("Ask a question about your uploaded document..."):
    curr_chat["messages"].append({"role": "user", "content": prompt})
    if len(curr_chat["messages"]) == 1:
        curr_chat["title"] = prompt[:28] + ("..." if len(prompt) > 28 else "")

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Synthesizing answer..."):
            res = requests.post(f"{API_URL}/query", params={"question": prompt})
            if res.status_code == 200:
                ans, srcs = res.json().get("answer", ""), res.json().get("sources", [])
                st.markdown(ans)
                if srcs:
                    with st.expander("🔍 Verified Context Citations"):
                        for idx, src in enumerate(srcs, 1):
                            st.markdown(f'<div class="source-box"><b>Chunk {idx}:</b> {src}</div>', unsafe_allow_html=True)
                curr_chat["messages"].append({"role": "assistant", "content": ans, "sources": srcs})
                chats[st.session_state.chat_id] = curr_chat
                save_chats(chats)
            else:
                st.error("Failed to fetch response.")