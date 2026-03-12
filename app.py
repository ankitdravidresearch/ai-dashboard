# Install required packages
!pip install streamlit pandas matplotlib seaborn openai -q

# Import libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="AI Dashboard Generator", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; }
    .stTextArea>div>div>textarea { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🤖 AI Dashboard Generator")
st.markdown("Upload data or describe your problem → Get an automated dashboard!")

# Sidebar for options
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

# Function to create dashboard
def create_dashboard(data, title="Dashboard"):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    # Top Left: Text Summary
    axs[0, 0].axis('off')
    if 'Revenue' in data.columns:
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
    
    # Top Right: Line Chart (if numeric columns exist)
    numeric_cols = data.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        axs[0, 1].plot(data.index, data[numeric_cols[0]], marker='o', color='green', linewidth=2)
        axs[0, 1].set_title(f"{numeric_cols[0]} Trend")
        axs[0, 1].grid(True, linestyle='--', alpha=0.6)
    else:
        axs[0, 1].text(0.5, 0.5, "No numeric data for trend", ha='center')
        axs[0, 1].axis('off')
    
    # Bottom Left: Pie Chart (categorical)
    cat_cols = data.select_dtypes(include=['object']).columns
    if len(cat_cols) > 0:
        cat_data = data[cat_cols[0]].value_counts()
        axs[1, 0].pie(cat_data, labels=cat_data.index, autopct='%1.1f%%')
        axs[1, 0].set_title(f"{cat_cols[0]} Distribution")
    else:
        axs[1, 0].text(0.5, 0.5, "No categorical data", ha='center')
        axs[1, 0].axis('off')
    
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
    uploaded_file = st.file_uploader("Choose CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            st.success("✅ Data loaded successfully!")
            st.dataframe(data.head())
            
            if st.button("🎨 Generate Dashboard"):
                fig = create_dashboard(data, f"Dashboard: {uploaded_file.name}")
                st.pyplot(fig)
                
                # Fixed download button
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