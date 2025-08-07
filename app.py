import streamlit as st
import pandas as pd
import base64
import io
from datetime import datetime
import tempfile
import os
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
from chatbot_agent import DataSummaryChatbot

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="InsightBot",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styles ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    .user-message {
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# --- Session Setup ---
def setup_state():
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = DataSummaryChatbot()
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'current_chart' not in st.session_state:
        st.session_state.current_chart = None

# --- Display EDA Results ---
def show_eda(eda):
    st.subheader("Dataset Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Shape", f"{eda['shape'][0]} rows × {eda['shape'][1]} cols")
        st.metric("Numeric Columns", len(eda['numeric_columns']))
        st.metric("Categorical Columns", len(eda['categorical_columns']))
    
    with col2:
        for col in eda['columns']:
            dtype = eda['data_types'][col]
            nulls = eda['null_counts'][col]
            null_pct = eda['null_percentage'][col]
            st.write(f"- **{col}** ({dtype}) → Nulls: {nulls} ({null_pct:.1f}%)")

    if sum(eda['null_counts'].values()) > 0:
        st.subheader("Nulls")
        df_null = pd.DataFrame({
            'Column': list(eda['null_counts'].keys()),
            'Null Count': list(eda['null_counts'].values()),
            'Null %': list(eda['null_percentage'].values())
        })
        st.dataframe(df_null)

    st.subheader("Column Data Types")
    df_dtype = pd.DataFrame({
        'Column': list(eda['data_types'].keys()),
        'Type': list(eda['data_types'].values())
    })
    st.dataframe(df_dtype)

# --- PDF Report Generation ---
def export_pdf(chatbot, filename="report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Data Summary Report', ln=True, align='C')
    pdf.ln(10)

    if chatbot.summary_stats:
        stats = chatbot.summary_stats
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Rows × Cols: {stats['shape'][0]} × {stats['shape'][1]}", ln=True)
        pdf.cell(0, 10, f"Columns: {', '.join(stats['columns'])[:80]}...", ln=True)
        pdf.cell(0, 10, f"Numerics: {len(stats['numeric_columns'])}", ln=True)
        pdf.cell(0, 10, f"Categoricals: {len(stats['categorical_columns'])}", ln=True)

    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Conversation Log', ln=True)
    pdf.set_font('Arial', '', 10)

    for i, item in enumerate(chatbot.chat_history, 1):
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, f"Q{i}: {item['user']}", ln=True)
        pdf.set_font('Arial', '', 10)
        reply = item.get('assistant', '')
        pdf.multi_cell(0, 6, f"A{i}: {reply[:500]}{'...' if len(reply) > 500 else ''}")

        if 'chart' in item and item['chart']:
            try:
                chart_img = base64.b64decode(item['chart'])
                temp_img = f"temp_chart_{i}.png"
                with open(temp_img, "wb") as f:
                    f.write(chart_img)
                pdf.image(temp_img, w=120)
                os.remove(temp_img)
            except:
                continue
        pdf.ln(3)

    pdf.output(filename)
    return filename

# --- Main App Logic ---
def main():
    setup_state()

    st.markdown('<h1 class="main-header">InsightBot: Smart Data Chat</h1>', unsafe_allow_html=True)

    # --- Sidebar Upload ---
    with st.sidebar:
        st.header(" Upload Data")
        file = st.file_uploader("Upload a CSV, TSV, XLSX or JSON file", type=['csv', 'tsv', 'xlsx', 'json'])

        if file:
            ext = file.name.split('.')[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp:
                temp.write(file.read())
                path = temp.name

            load_result = st.session_state.chatbot.load_data(path)
            os.unlink(path)

            if load_result['success']:
                st.session_state.data_loaded = True
                st.success(load_result['message'])
            else:
                st.error(load_result['message'])

        st.divider()

        st.header(" Ollama Status")
        if st.session_state.chatbot.ollama_available:
            st.success("LLM is running (gemma:2b)")
        else:
            st.warning("Ollama not detected. Using rule-based fallback.")

        if st.session_state.data_loaded and st.session_state.chatbot.chat_history:
            if st.button(" Download PDF Summary"):
                with st.spinner("Generating PDF..."):
                    pdf_file = export_pdf(st.session_state.chatbot)
                    with open(pdf_file, "rb") as f:
                        st.download_button("Download Report", f, file_name=pdf_file, mime="application/pdf")
                    os.unlink(pdf_file)

        if st.button(" Reset Chat"):
            st.session_state.chatbot.reset()
            st.session_state.data_loaded = False
            st.session_state.current_chart = None
            st.rerun()

    # --- Main Area ---
    if st.session_state.data_loaded:
        show_eda(st.session_state.chatbot.summary_stats)
        st.divider()

        st.subheader(" Ask About Your Data")
        prompt = st.chat_input("Ask a question... (e.g. average of column, pie chart of genre)")

        if prompt:
            with st.spinner("Thinking..."):
                reply = st.session_state.chatbot.process_user_input(prompt)

            if reply['success']:
                if 'image_base64' in reply:
                    st.image(base64.b64decode(reply['image_base64']), caption=reply['message'])
                    st.session_state.current_chart = reply['image_base64']
                else:
                    st.markdown(f'<div class="chat-message bot-message">{reply["message"]}</div>', unsafe_allow_html=True)
            else:
                st.error(reply['message'])

        if st.session_state.chatbot.chat_history:
            st.subheader("🗂 Chat Log")
            for msg in st.session_state.chatbot.chat_history:
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["user"]}</div>', unsafe_allow_html=True)
                if 'assistant' in msg:
                    st.markdown(f'<div class="chat-message bot-message"><strong>Bot:</strong> {msg["assistant"]}</div>', unsafe_allow_html=True)
                if 'chart' in msg and msg['chart']:
                    st.image(base64.b64decode(msg['chart']), caption="Chart")
                st.divider()

    else:
        st.info("Upload a data file to get started!")

if __name__ == "__main__":
    main()
