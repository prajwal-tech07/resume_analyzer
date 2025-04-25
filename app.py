import streamlit as st
from backend import (
    extract_text_from_pdf,
    extract_skills,
    save_resume_to_db,
    match_jobs_with_resume
)
import pandas as pd
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .st-b7 {
        color: white;
    }
    .reportview-container {
        background: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Main app
def main():
    st.title("📄 AI-Powered Resume Analyzer")
    st.markdown("Upload your resume and discover your best job matches")
    
    with st.expander("ℹ️ How it works"):
        st.write("""
        1. Upload your resume (PDF format)
        2. Our AI extracts your skills
        3. We match you with suitable jobs
        4. See your compatibility score
        """)
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Choose your resume (PDF only)",
        type="pdf",
        accept_multiple_files=False
    )
    
    if uploaded_file:
        # Process resume
        with st.spinner("Analyzing your resume..."):
            text = extract_text_from_pdf(uploaded_file)
            skills = extract_skills(text)
            
            # Save to database
            resume_name = f"Resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            save_resume_to_db(resume_name, text, skills)
            
            # Display results
            st.success("Analysis complete!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Extracted Skills")
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.warning("No skills detected. Try a different resume format.")
                
                st.subheader("📊 Resume Text Preview")
                st.text_area("Content", value=text[:1000] + "...", height=200)
            
            with col2:
                st.subheader("🎯 Job Matches")
                if skills:
                    matches = match_jobs_with_resume(skills)
                    if not matches.empty:
                        matches_sorted = matches.sort_values('Match %', ascending=False)
                        
                        for _, row in matches_sorted.iterrows():
                            st.markdown(f"### {row['Job Title']} at {row['Company']}")
                            st.metric("Match Score", f"{row['Match %']}%")
                            st.progress(row['Match %'] / 100)
                            
                            with st.expander("Details"):
                                st.write(f"**Required Skills:** {row['Required Skills']}")
                                st.write(f"**Your Matching Skills:** {row['Your Matching Skills']}")
                    else:
                        st.warning("No job matches found. Try adding more skills to your resume.")
                else:
                    st.warning("No skills detected - cannot match jobs.")

# Run the app
if __name__ == "__main__":
    main()