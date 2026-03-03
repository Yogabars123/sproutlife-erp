st.markdown("""
<style>

body {
    background-color: #f4f6f9;
}

/* Desktop */
.kpi-box {
    background: linear-gradient(135deg, #1A56DB, #2563EB);
    padding: 30px;
    border-radius: 16px;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.kpi-title {
    font-size: 18px;
    font-weight: 500;
}

.kpi-value {
    font-size: 38px;
    font-weight: 700;
    margin-top: 8px;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
}

/* 📱 MOBILE OPTIMIZED */
@media (max-width: 768px) {

    .main .block-container {
        padding: 0.8rem 0.8rem;
    }

    .kpi-box {
        padding: 16px;
        border-radius: 12px;
    }

    .kpi-title {
        font-size: 12px;
    }

    .kpi-value {
        font-size: 20px;
    }

    .section-title {
        font-size: 16px;
    }

    .stTextInput input {
        font-size: 13px !important;
    }

    .stSelectbox div {
        font-size: 13px !important;
    }

    .stDataFrame {
        font-size: 12px !important;
    }
}

</style>
""", unsafe_allow_html=True)
