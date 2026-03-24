import os
import streamlit as st
from dotenv import load_dotenv
from generator import generate_test_cases
from exporter import export_to_excel

load_dotenv()

st.set_page_config(
    page_title="QA Test Case Generator",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 QA Test Case Generator")
st.caption("Paste PRD → Generate Test Case → Download Excel")

# Sidebar: API Key
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Ambil API key gratis di https://aistudio.google.com/apikey",
    )
    st.divider()
    st.markdown("**Cara pakai:**")
    st.markdown("1. Masukkan API key")
    st.markdown("2. Paste PRD di kolom kiri")
    st.markdown("3. Klik **Generate**")
    st.markdown("4. Download Excel")

# Main content
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📄 PRD")
    prd_text = st.text_area(
        label="Paste PRD di sini",
        height=500,
        placeholder="Paste PRD dari Notion di sini...\n\nContoh:\nFitur: Download Kartu Massal\nDeskripsi: Admin dapat mengunduh kartu untuk seluruh siswa atau berdasarkan filter tertentu...",
        label_visibility="collapsed",
    )

    generate_btn = st.button(
        "⚡ Generate Test Case",
        type="primary",
        use_container_width=True,
        disabled=not prd_text.strip() or not api_key.strip(),
    )

with col_output:
    st.subheader("📋 Hasil")

    if "test_cases" not in st.session_state:
        st.session_state.test_cases = []
    if "excel_bytes" not in st.session_state:
        st.session_state.excel_bytes = None

    if generate_btn:
        if not api_key.strip():
            st.error("Masukkan Gemini API Key terlebih dahulu.")
        elif not prd_text.strip():
            st.error("PRD tidak boleh kosong.")
        else:
            with st.spinner("Sedang generate test case... ⏳"):
                try:
                    test_cases = generate_test_cases(prd_text, api_key)
                    st.session_state.test_cases = test_cases
                    st.session_state.excel_bytes = export_to_excel(test_cases)
                    st.success(f"Berhasil generate **{len(test_cases)} test case**!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.test_cases = []
                    st.session_state.excel_bytes = None

    if st.session_state.test_cases:
        # Download button
        st.download_button(
            label="📥 Download Excel",
            data=st.session_state.excel_bytes,
            file_name="test_cases.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

        st.divider()

        # Preview test cases
        st.markdown(f"**Total: {len(st.session_state.test_cases)} test case**")
        for i, tc in enumerate(st.session_state.test_cases, start=1):
            with st.expander(f"{i}. {tc.get('name', '-')} — {tc.get('priority', '')} | {tc.get('type', '')}"):
                steps = tc.get("steps", [])
                for j, step in enumerate(steps, start=1):
                    st.markdown(f"**Step {j}:** {step.get('step', '')}")
                    st.markdown(f"**Expected:** {step.get('expected_result', '')}")
                    if j < len(steps):
                        st.divider()
    else:
        st.info("Hasil generate test case akan muncul di sini.")
