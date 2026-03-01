import streamlit as st

st.set_page_config(page_title="Styling Guide", layout="wide", page_icon="📖")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.stApp { background: #F8FAFC !important; }

[data-testid="stSidebar"] {
    background: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(15,23,42,0.05) !important;
}
[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important; margin: 2px 8px !important;
    padding: 8px 12px !important; font-weight: 500 !important;
}
[data-testid="stSidebarNavLink"]:hover { background: #EBF2FF !important; color: #1A56DB !important; }
[data-testid="stSidebarNavLink"][aria-selected="true"] {
    background: #EBF2FF !important; color: #1A56DB !important;
    font-weight: 600 !important; border-left: 3px solid #1A56DB !important;
}
.main .block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1000px !important; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* code block styling */
code { background: #F1F5F9 !important; border-radius: 4px !important; 
       padding: 0.15rem 0.4rem !important; font-size: 0.82rem !important;
       color: #1A56DB !important; font-family: 'DM Mono', monospace !important; }
pre { background: #0F172A !important; border-radius: 10px !important;
      padding: 1.2rem 1.5rem !important; overflow-x: auto !important; }
pre code { background: transparent !important; color: #E2E8F0 !important;
           font-size: 0.82rem !important; line-height: 1.7 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.8rem;padding-bottom:1.2rem;border-bottom:1px solid #E2E8F0;">
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.3rem;">
        <span style="font-size:1.8rem;">📖</span>
        <h1 style="margin:0;font-family:'DM Sans',sans-serif;font-size:1.75rem;
                   font-weight:700;color:#0F172A;letter-spacing:-0.02em;">Styling Guide</h1>
    </div>
    <p style="margin:0;font-size:0.875rem;color:#94A3B8;padding-left:2.6rem;">
        How to apply the Sproutlife ERP design system to any page
    </p>
</div>""", unsafe_allow_html=True)

# ─── STEP CARD HELPER ────────────────────────────────────────────────────────
def step(number, title, body_html):
    st.markdown(f"""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;background:#fff;
                border:1px solid #E2E8F0;border-radius:12px;padding:1.25rem 1.5rem;
                box-shadow:0 1px 4px rgba(15,23,42,0.05);">
        <div style="flex-shrink:0;width:32px;height:32px;background:#1A56DB;border-radius:50%;
                    display:flex;align-items:center;justify-content:center;
                    color:#fff;font-weight:700;font-size:0.85rem;margin-top:2px;">{number}</div>
        <div style="flex:1;">
            <div style="font-weight:700;font-size:1rem;color:#0F172A;margin-bottom:0.5rem;">{title}</div>
            {body_html}
        </div>
    </div>""", unsafe_allow_html=True)

def badge(text, color="#1A56DB"):
    return f'<span style="background:{color}18;color:{color};border:1px solid {color}40;border-radius:4px;padding:0.1rem 0.5rem;font-size:0.75rem;font-weight:600;font-family:DM Mono,monospace;">{text}</span>'

# ─── WHY NO SEPARATE FILE ────────────────────────────────────────────────────
st.markdown("""
<div style="background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;
            padding:1rem 1.25rem;margin-bottom:1.5rem;display:flex;gap:0.75rem;align-items:flex-start;">
    <span style="font-size:1.2rem;">⚠️</span>
    <div>
        <div style="font-weight:700;color:#DC2626;margin-bottom:0.25rem;">
            Why not use a shared style.py file?
        </div>
        <div style="font-size:0.875rem;color:#7F1D1D;line-height:1.6;">
            On Streamlit Cloud, pages inside the <code style="background:#FEE2E2;color:#DC2626;
            border-radius:3px;padding:0.1rem 0.3rem;">/pages</code> folder 
            cannot import from a file in the project root using a bare 
            <code style="background:#FEE2E2;color:#DC2626;border-radius:3px;
            padding:0.1rem 0.3rem;">from style import ...</code> statement — 
            this causes a <strong>ModuleNotFoundError</strong>. 
            The solution is to <strong>embed the CSS block directly in each page</strong>.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ─── STEPS ───────────────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:1rem;">
            How to apply styling to a new page</div>""", unsafe_allow_html=True)

step("1", "Add st.set_page_config at the very top", """
<div style="font-size:0.875rem;color:#475569;margin-bottom:0.75rem;">
    This must always be the first Streamlit call in your file.
</div>
<pre><code>st.set_page_config(page_title="My Page", layout="wide", page_icon="📦")</code></pre>
""")

step("2", "Paste the embedded CSS block", f"""
<div style="font-size:0.875rem;color:#475569;margin-bottom:0.75rem;">
    Copy the entire <code>st.markdown(\"\"\"&lt;style&gt;...&lt;/style&gt;\"\"\")</code> block 
    from any existing page (e.g. 1_RM_Inventory.py or 2_GRN_Data.py) and paste it 
    right after <code>set_page_config</code>. Do not change anything inside it.
</div>
<pre><code>st.markdown(\"\"\"
&lt;style&gt;
@import url('https://fonts.googleapis.com/...');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif !important; }}
.stApp {{ background: #F8FAFC !important; }}
/* ... rest of CSS block ... */
&lt;/style&gt;
\"\"\", unsafe_allow_html=True)</code></pre>
""")

step("3", "Copy the 3 helper functions", """
<div style="font-size:0.875rem;color:#475569;margin-bottom:0.75rem;">
    Paste these 3 functions below the CSS block. They give you clean 
    headers, KPI cards, and section labels.
</div>
<pre><code>def stat_card(label, value, sub="", color="#1A56DB", icon=""):
    return f\"\"\"
    &lt;div style="background:linear-gradient(135deg,{color} 0%,{color}cc 100%);
                border-radius:14px;padding:1.4rem 1.6rem;color:#fff;..."&gt;
        ...
    &lt;/div&gt;\"\"\"

def page_header(icon, title, subtitle=""):
    st.markdown(f\"\"\"&lt;div style="..."&gt;...&lt;/div&gt;\"\"\", unsafe_allow_html=True)

def section_label(text):
    st.markdown(f\"\"\"&lt;div style="..."&gt;{text}&lt;/div&gt;\"\"\", unsafe_allow_html=True)</code></pre>
""")

step("4", "Use the helpers in your page content", f"""
<div style="font-size:0.875rem;color:#475569;margin-bottom:0.75rem;">
    Replace your existing title/header calls with the helpers:
</div>
<pre><code># Page header (replaces st.title or st.markdown heading)
page_header("📦", "RM Inventory", "Live raw material stock")

# Section labels above filter rows
section_label("Search & Filter")

# KPI cards  — pick the right colour per meaning:
#   Blue  #1A56DB → totals / neutral
#   Green #16A34A → positive / received / in-stock
#   Amber #B45309 → pending / warning
#   Red   #DC2626 → rejected / danger
st.markdown(
    stat_card("Total QTY Available", "16,300,788", "2,414 records", "#1A56DB", "📦"),
    unsafe_allow_html=True
)</code></pre>
""")

st.markdown("---")

# ─── PAGE CHECKLIST ──────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:0.68rem;font-weight:700;letter-spacing:0.08em;
            text-transform:uppercase;color:#94A3B8;margin-bottom:1rem;">
            Page-by-page status</div>""", unsafe_allow_html=True)

pages = [
    ("1_RM_Inventory.py",           "✅", "#16A34A", "Styled"),
    ("2_GRN_Data.py",               "✅", "#16A34A", "Styled"),
    ("3_FG_Inventory.py",           "⏳", "#B45309", "Paste CSS + helpers"),
    ("4_Consumption.py",            "⏳", "#B45309", "Paste CSS + helpers"),
    ("5_Forecast.py",               "⏳", "#B45309", "Paste CSS + helpers"),
    ("6_Replenishment.py",          "⏳", "#B45309", "Paste CSS + helpers"),
    ("7_Consumption_vs_Forecast.py","⏳", "#B45309", "Paste CSS + helpers"),
    ("8_Style.py",                  "✅", "#16A34A", "Styled"),
    ("9_Styling_Guide.py",          "✅", "#16A34A", "Styled"),
]

for filename, status_icon, status_color, status_text in pages:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                background:#fff;border:1px solid #E2E8F0;border-radius:8px;
                padding:0.75rem 1.25rem;margin-bottom:0.5rem;">
        <div style="font-family:'DM Mono',monospace;font-size:0.82rem;color:#0F172A;">{filename}</div>
        <div style="display:flex;align-items:center;gap:0.4rem;">
            <span>{status_icon}</span>
            <span style="font-size:0.78rem;font-weight:600;color:{status_color};">{status_text}</span>
        </div>
    </div>""", unsafe_allow_html=True)
