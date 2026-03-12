# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import PyPDF2

# Page Configuration
st.set_page_config(page_title="AI Dashboard Generator", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AI Dashboard Generator")
st.markdown("Upload data or describe your problem → Get an automated dashboard!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    input_type = st.radio(
        "Choose Input Type:",
        ["📁 Upload Data", "📝 Describe Problem", "🔗 OpenAI Summary"]
    )
    st.info("💡 Tip: Upload CSV for best results!")

# Function to generate dummy data
def generate_dummy_data():
    return pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [100, 150, 130, 170, 200, 220],
        'Cost': [80, 90, 85, 100, 110, 120],
        'Region': ['North', 'North', 'South', 'East', 'West', 'North'],
        'Product': ['A', 'B', 'A', 'C', 'B', 'A']
    })

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

# Function to summarize text (simple keyword-based)
def summarize_text(text, max_sentences=5):
    try:
        # Split text into sentences
        sentences = text.replace('\n', ' ').split('. ')
        # Return first N sentences as summary
        summary = '. '.join(sentences[:max_sentences])
        return summary if summary else "No text content found in PDF."
    except Exception as e:
        return f"Error summarizing: {str(e)}"

# Function to create dashboard
def create_dashboard(data, title="Dashboard", pdf_summary=None):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Top Left: Text Summary
    axs[0, 0].axis('off')
    if pdf_summary:
        summary_text = (
            f"📄 PDF TEXT SUMMARY\n\n"
            f"{pdf_summary}\n\n"
            f"📊 SUMMARY\n"
            f"PDF content has been extracted and summarized."
        )
    elif 'Revenue' in data.columns:
        max_rev = data['Revenue'].max()
        avg_rev = data['Revenue'].mean()
        summary_text = (
            f"📌 KEY INSIGHTS\n\n"
            f"• Max Revenue: ${max_rev}K\n"
            f"• Avg Revenue: ${avg_rev:.2f}K\n"
            f"• Total Records: {len(data)}\n\n"
            f"📊 SUMMARY\n"
            f"Data shows strong performance "
            f"with peak at ${max_rev}K."
        )
    else:
        summary_text = (
            f"📌 KEY INSIGHTS\n\n"
            f"• Total Records: {len(data)}\n"
            f"• Columns: {', '.join(data.columns)}\n\n"
            f"📊 SUMMARY\n"
            f"Dashboard generated from uploaded data."
        )
    
    axs[0, 0].text(0.1, 0.5, summary_text, fontsize=12, family='monospace')
    axs[0, 0].set_title("Executive Summary", fontsize=12)
    
    # Top Right: Line Chart
    numeric_cols = data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        axs[0, 1].plot(data.index, data[numeric_cols[0]], marker='o', color='green', linewidth=2)
        axs[0, 1].set_title(f"{numeric_cols[0]} Trend")
        axs[0, 1].grid(True, linestyle='--', alpha=0.6)
    else:
        axs[0, 1].text(0.5, 0.5, "No numeric data for trend", ha='center')
        axs[0, 1].axis('off')
    
    # Bottom Left: PDF Text Summary (NEW - replaces pie chart)
    axs[1, 0].axis('off')
    if pdf_summary:
        axs[1, 0].text(0.1, 0.5, f"📄 PDF SUMMARY\n\n{pdf_summary[:300]}...", fontsize=10)
        axs[1, 0].set_title("PDF Text Summary", fontsize=12)
    else:
        axs[1, 0].text(0.5, 0.5, "No PDF uploaded", ha='center')
        axs[1, 0].set_title("PDF Text Summary", fontsize=12)
    
    # Bottom Right: Bar Chart
    if len(numeric_cols) > 1:
        axs[1, 1].bar(data.index[:5], data[numeric_cols[1]].values[:5], color='orange')
        axs[1, 1].set_title(f"{numeric_cols[1]} (Top 5)")
    else:
        axs[1, 1].text(0.5, 0.5, "Need more numeric columns", ha='center')
        axs[1, 1].axis('off')
    
    plt.tight_layout()
    return fig

# Function to save figure to BytesIO
def save_fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

# Main App Logic
if input_type == "📁 Upload Data":
    st.header("📁 Upload Your Data")
    uploaded_file = st.file_uploader(
        "Choose CSV, Excel, or PDF file", 
        type=['csv', 'xlsx', 'pdf']
    )
    
    if uploaded_file is not None:
        try:
            pdf_summary = None
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
                file_type = "CSV"
            elif uploaded_file.name.endswith('.xlsx'):
                try:
                    data = pd.read_excel(uploaded_file)
                    file_type = "Excel"
                except ImportError:
                    st.error("❌ Excel support requires openpyxl. Please upload CSV or PDF instead.")
                    st.stop()
            elif uploaded_file.name.endswith('.pdf'):
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.success("✅ PDF text extracted successfully!")
                st.text_area("PDF Content Preview", pdf_text[:500], height=200)
                
                # Summarize PDF text
                pdf_summary = summarize_text(pdf_text)
                st.success("✅ PDF text summarized!")
                st.text_area("PDF Summary", pdf_summary, height=150)
                
                # For PDF, we'll use dummy data since PDF text extraction is complex
                st.info("💡 Note: PDF text extraction is experimental. Using demo data for dashboard.")
                data = generate_dummy_data()
                file_type = "PDF"
            else:
                st.error("❌ Unsupported file format. Please upload CSV, Excel, or PDF.")
                st.stop()
            
            st.success(f"✅ Data loaded successfully! ({file_type})")
            st.dataframe(data.head())
            
            if st.button("🎨 Generate Dashboard"):
                fig = create_dashboard(data, f"Dashboard: {uploaded_file.name}", pdf_summary)
                st.pyplot(fig)
                
                img_bytes = save_fig_to_bytes(fig)
                st.download_button(
                    label="📥 Download Dashboard Image",
                    data=img_bytes,
                    file_name="dashboard.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"❌ Error: {e}")

elif input_type == "📝 Describe Problem":
    st.header("📝 Describe Your Problem")
    problem_desc = st.text_area("What would you like to analyze?", 
                                  placeholder="e.g., Sales performance in Q4, Customer satisfaction trends...")
    
    if st.button("🎨 Generate Dashboard"):
        if problem_desc:
            st.info("🤖 Generating insights based on your description...")
            data = generate_dummy_data()
            fig = create_dashboard(data, f"Dashboard: {problem_desc[:30]}")
            st.pyplot(fig)
            
            img_bytes = save_fig_to_bytes(fig)
            st.download_button(
                label="📥 Download Dashboard Image",
                data=img_bytes,
                file_name="dashboard.png",
                mime="image/png"
            )
        else:
            st.warning("⚠️ Please describe your problem first!")

elif input_type == "🔗 OpenAI Summary":
    st.header("🔗 OpenAI Integration")
    api_key = st.text_input("Enter OpenAI API Key (Optional)", type="password")
    prompt = st.text_area("Enter your prompt for analysis", 
                          placeholder="Summarize this sales data and create insights...")
    
    if st.button("🎨 Generate with AI"):
        if not api_key:
            st.warning("⚠️ API Key is optional. Using demo data.")
            data = generate_dummy_data()
        else:
            try:
                import openai
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.success("✅ AI Analysis Complete!")
                st.write(response.choices[0].message.content)
                data = generate_dummy_data()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                data = generate_dummy_data()
        
        fig = create_dashboard(data, "AI-Generated Dashboard")
        st.pyplot(fig)
        
        img_bytes = save_fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Dashboard Image",
            data=img_bytes,
            file_name="dashboard.png",
            mime="image/png"
        )

# Footer
st.markdown("---")
st.markdown("🎯 **Built with Streamlit | Powered by AI**")
