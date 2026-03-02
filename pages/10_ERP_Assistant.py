import streamlit as st

st.set_page_config(page_title="ERP Assistant", layout="wide", page_icon="🤖")

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDED STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(15,23,42,0.05) !important;
}
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important; margin: 2px 8px !important;
    padding: 8px 12px !important; font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stSidebarNavLink"]:hover { background: #EBF2FF !important; color: #1A56DB !important; }
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: #EBF2FF !important; color: #1A56DB !important;
    font-weight: 600 !important; border-left: 3px solid #1A56DB !important;
}
.main .block-container { padding: 1.5rem 2rem 2rem !important; max-width: 900px !important; }

/* Chat input */
.stChatInput textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    border-radius: 12px !important;
    border: 1.5px solid #E2E8F0 !important;
    background: #fff !important;
}
.stChatInput textarea:focus {
    border-color: #93C5FD !important;
    box-shadow: 0 0 0 3px rgba(147,197,253,0.3) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    margin-bottom: 0.5rem !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.05) !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #EBF2FF !important;
    border-color: #BFDBFE !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #FFFFFF !important;
}

.stButton > button {
    background: #1A56DB !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover { background: #1140A8 !important; transform: translateY(-1px) !important; }

#MainMenu { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT SETUP
# ─────────────────────────────────────────────────────────────────────────────
import anthropic

# ── PASTE YOUR FULL API KEY BETWEEN THE QUOTES BELOW ──────────────────────
ANTHROPIC_API_KEY = "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"
# ──────────────────────────────────────────────────────────────────────────

try:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    api_ready = True
except Exception:
    api_ready = False

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — customise this to describe YOUR ERP data
# ─────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Sproutlife ERP Assistant, an intelligent helper for the Sproutlife internal ERP system.

You help the operations and supply chain team with questions about:
- RM Inventory (raw material stock, SKUs, batch numbers, warehouse locations)
- GRN Data (Goods Receipt Notes, purchase orders, vendors, delivery tracking)
- FG Inventory (finished goods stock)
- Consumption (raw material usage in production)
- Forecast (demand forecasting)
- Replenishment (reorder suggestions, safety stock)
- Consumption vs Forecast (variance analysis)

You are helpful, concise, and professional. You speak like a knowledgeable operations analyst.
When you don't have live data access, you guide the user on where to find the information in the ERP 
and suggest what filters or pages to check.

Always respond in clear, structured answers. Use bullet points for lists. 
Keep responses focused and actionable.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;padding-bottom:1.2rem;border-bottom:1px solid #E2E8F0;">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
        <span style="font-size:1.8rem;line-height:1;">🤖</span>
        <h1 style="margin:0;font-family:'DM Sans',sans-serif;font-size:1.75rem;
                   font-weight:700;color:#0F172A;letter-spacing:-0.02em;">ERP Assistant</h1>
    </div>
    <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">
        Ask me anything about your inventory, GRNs, consumption or forecasts
    </p>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# API KEY WARNING
# ─────────────────────────────────────────────────────────────────────────────
if not api_ready:
    st.markdown("""
    <div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:1.5rem;display:flex;gap:0.75rem;">
        <span style="font-size:1.2rem;">⚠️</span>
        <div>
            <div style="font-weight:700;color:#DC2626;margin-bottom:0.4rem;">API Key not configured</div>
            <div style="font-size:0.875rem;color:#7F1D1D;line-height:1.6;">
                To activate the chatbot:<br>
                1. Go to <strong>Streamlit Cloud → Your App → Settings → Secrets</strong><br>
                2. Add this line: <code style="background:#FEE2E2;color:#DC2626;
                   border-radius:3px;padding:0.1rem 0.4rem;">ANTHROPIC_API_KEY = "sk-ant-..."</code><br>
                3. Get your key at <strong>console.anthropic.com</strong> (free to start)
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTED QUESTIONS
# ─────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
                text-transform:uppercase;color:#94A3B8;margin-bottom:0.75rem;">
        Suggested questions
    </div>""", unsafe_allow_html=True)

    suggestions = [
        ("📦", "Which raw materials are running low on stock?"),
        ("📥", "How many GRNs were received this month?"),
        ("⏳", "What is the total pending quantity across all vendors?"),
        ("📊", "Which items have the highest consumption vs forecast variance?"),
        ("🏭", "Which warehouse has the most raw material stock?"),
        ("🔄", "Which items need replenishment urgently?"),
    ]

    col1, col2 = st.columns(2)
    for i, (icon, question) in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"{icon}  {question}", key=f"suggestion_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────────────────────────────────────────
# CHAT INPUT + RESPONSE
# ─────────────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about inventory, GRNs, consumption, forecasts…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not api_ready:
            st.warning("Please configure your ANTHROPIC_API_KEY in Streamlit secrets to enable the chatbot.")
        else:
            with st.spinner("Thinking…"):
                try:
                    response = client.messages.create(
                        model="claude-opus-4-5",
                        max_tokens=1024,
                        system=SYSTEM_PROMPT,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    )
                    reply = response.content[0].text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error calling Claude API: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# CLEAR CHAT BUTTON
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_clear, _ = st.columns([1, 5])
    with col_clear:
        if st.button("🗑️  Clear chat"):
            st.session_state.messages = []
            st.rerun()
