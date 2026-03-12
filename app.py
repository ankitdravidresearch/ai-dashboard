import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import PyPDF2
import re

st.set_page_config(page_title="AI Dashboard", layout="wide")

st.title("🤖 AI Dashboard Generator")
st.markdown("Upload data or describe your problem")

with st.sidebar:
    st.header("⚙️ Settings")
    input_type = st.radio("Choose Input Type:", ["📁 Upload Data", "📝 Describe Problem", "🔗 OpenAI Summary"])

def generate_dummy_data():
    return pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [100, 150, 130, 170, 200, 220],
        'Cost': [80, 90, 85, 100, 110, 120],
        'Region': ['North', 'North', 'South', 'East', 'West', 'North'],
        'Product': ['A', 'B', 'A', 'C', 'B', 'A']
    })

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error: {str(e)}"

def deep_summarize_pdf(text):
    try:
        text = text.replace('\n', ' ').strip()
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        summary = f"📄 **PDF Deep Summary**\n\n"
        if sentences:
            summary += f"📌 **Overview:** {sentences[0]}\n\n"
            summary += f"🔑 **Key Points:**\n"
            for i, sent in enumerate(sentences[:3], 1):
                summary += f"{i}. {sent[:100]}\n"
            summary += f"\n✅ **Conclusion:** {sentences[-1]}\n\n"
            summary += f"📈 **Total Sentences:** {len(sentences)}"
        else:
            summary = "No text content found in PDF."
        return summary, sentences
    except Exception as e:
        return f"Error: {str(e)}", []

def create_dashboard(data, title="Dashboard", pdf_summary=None):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Top Left: Summary
    axs[0, 0].axis('off')
    if pdf_summary:
        axs[0, 0].text(0.05, 0.95, "📄 PDF DEEP SUMMARY", fontsize=14, fontweight='bold', color='#667eea')
        axs[0, 0].text(0.05, 0.5, pdf_summary, fontsize=10, family='monospace', color='#2c3e50', verticalalignment='top')
    elif 'Revenue' in data.columns:
        max_rev = data['Revenue'].max()
        avg_rev = data['Revenue'].mean()
        summary_text = f"📌 KEY INSIGHTS\n\n• Max Revenue: ${max_rev}K\n• Avg Revenue: ${avg_rev:.2f}K\n• Total Records: {len(data)}"
        axs[0, 0].text(0.05, 0.5, summary_text, fontsize=11, family='monospace', color='#2c3e50', verticalalignment='top')
    else:
        summary_text = f"📌 KEY INSIGHTS\n\n• Total Records: {len(data)}\n• Columns: {', '.join(data.columns)}"
        axs[0, 0].text(0.05, 0.5, summary_text, fontsize=11, family='monospace', color='#2c3e50', verticalalignment='top')
    axs[0, 0].set_title("Executive Summary", fontsize=12)
    
    # Top Right: Line Chart
    numeric_cols = data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        axs[0, 1].plot(data.index, data[numeric_cols[0]], marker='o', color='#667eea', linewidth=2.5)
        axs[0, 1].set_title(f"📈 {numeric_cols[0]} Trend", fontsize=14, fontweight='bold')
        axs[0, 1].grid(True, linestyle='--', alpha=0.5)
    else:
        axs[0, 1].text(0.5, 0.5, "No numeric data", ha='center')
        axs[0, 1].axis('off')
    
    # Bottom Left: PDF Summary
    axs[1, 0].axis('off')
    if pdf_summary:
        axs[1, 0].text(0.05, 0.5, pdf_summary, fontsize=10, family='monospace', color='#2c3e50', verticalalignment='top')
    else:
        axs[1, 0].text(0.5, 0.5, "No PDF uploaded", ha='center')
    axs[1, 0].set_title("📄 PDF Deep Summary", fontsize=14, fontweight='bold')
    
    # Bottom Right: Bar Chart
    if len(numeric_cols) > 1:
        axs[1, 1].bar(range(len(data.index[:5])), data[numeric_cols[1]].values[:5], color='#764ba2')
        axs[1, 1].set_title(f"📊 {numeric_cols[1]} (Top 5)", fontsize=14, fontweight='bold')
        axs[1, 1].grid(True, linestyle='--', alpha=0.3)
    else:
        axs[1, 1].text(0.5, 0.5, "Need more numeric columns", ha='center')
        axs[1, 1].axis('off')
    
    plt.tight_layout()
    return fig

def save_fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

# Main App Logic
if input_type == "📁 Upload Data":
    st.header("📁 Upload Your Data")
    uploaded_file = st.file_uploader("Choose CSV, Excel, or PDF file", type=['csv', 'xlsx', 'pdf'])
    
    if uploaded_file is not None:
        try:
            pdf_summary = None
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
                file_type = "CSV"
            elif uploaded_file.name.endswith('.xlsx'):
                data = pd.read_excel(uploaded_file)
                file_type = "Excel"
            elif uploaded_file.name.endswith('.pdf'):
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF text extracted successfully!")
                st.text_area("📄 PDF Content Preview", pdf_text[:1000], height=300)
                pdf_summary, _ = deep_summarize_pdf(pdf_text)
                st.success("✅ PDF text deep summarized!")
                st.text_area("📊 PDF Deep Summary", pdf_summary, height=250)
                data = generate_dummy_data()
                file_type = "PDF"
            else:
                st.error("❌ Unsupported file format")
                st.stop()
            
            st.success(f"✅ Data loaded successfully! ({file_type})")
            st.dataframe(data.head())
            
            if st.button("🎨 Generate Dashboard", use_container_width=True):
                fig = create_dashboard(data, f"Dashboard: {uploaded_file.name}", pdf_summary)
                st.pyplot(fig)
                
                img_bytes = save_fig_to_bytes(fig)
                st.download_button("📥 Download Dashboard Image", data=img_bytes, file_name="dashboard.png", mime="image/png", use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif input_type == "📝 Describe Problem":
    st.header("📝 Describe Your Problem")
    problem_desc = st.text_area("What would you like to analyze?", placeholder="e.g., Sales performance in Q4")
    
    if st.button("🎨 Generate Dashboard"):
        if problem_desc:
            data = generate_dummy_data()
            fig = create_dashboard(data, f"Dashboard: {problem_desc[:30]}")
            st.pyplot(fig)
            img_bytes = save_fig_to_bytes(fig)
            st.download_button("📥 Download Dashboard Image", data=img_bytes, file_name="dashboard.png", mime="image/png", use_container_width=True)
        else:
            st.warning("⚠️ Please describe your problem first!")

elif input_type == "🔗 OpenAI Summary":
    st.header("🔗 OpenAI Integration")
    api_key = st.text_input("Enter OpenAI API Key (Optional)", type="password")
    prompt = st.text_area("Enter your prompt for analysis", placeholder="Summarize this sales data")
    
    if st.button("🎨 Generate with AI"):
        if not api_key:
            data = generate_dummy_data()
        else:
            try:
                import openai
                openai.api_key = api_key
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                st.success("✅ AI Analysis Complete!")
                st.write(response.choices[0].message.content)
                data = generate_dummy_data()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                data = generate_dummy_data()
        
        fig = create_dashboard(data, "AI-Generated Dashboard")
        st.pyplot(fig)
        img_bytes = save_fig_to_bytes(fig)
        st.download_button("📥 Download Dashboard Image", data=img_bytes, file_name="dashboard.png", mime="image/png", use_container_width=True)

st.markdown("---")
st.markdown("🎯 **Built with Streamlit | Powered by AI**")
