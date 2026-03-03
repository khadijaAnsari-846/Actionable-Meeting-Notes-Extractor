import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(page_title="CRM Intelligence", layout="wide")

st.title("📞 Sales Call Intelligence Pipeline")

# --- Sidebar: Ingestion ---
st.sidebar.header("Upload New Call")
uploaded_file = st.sidebar.file_uploader("Choose an audio file", type=["mp3", "wav"])
url_input = st.sidebar.text_input("Or paste YouTube URL")

if st.sidebar.button("Process Call"):
    if uploaded_file:
        files = {"file": uploaded_file.getvalue()}
        response = requests.post("http://localhost:8000/ingest/upload", files={"file": (uploaded_file.name, uploaded_file.getvalue())})
        st.sidebar.success(f"Job ID: {response.json()['job_id']}")
    elif url_input:
        response = requests.post("http://localhost:8000/ingest/upload", data={"url": url_input})
        st.sidebar.success(f"Job ID: {response.json()['job_id']}")

# --- Main Area: Results ---
st.header("Call Analysis")
job_id = st.text_input("Enter Job ID to check status")

if st.button("Fetch Results"):
    response = requests.get(f"http://localhost:8000/jobs/{job_id}")
    job_data = response.json()
    
    st.write(f"Status: **{job_data['status']}**")
    
    if job_data['status'] == "COMPLETED":
        insights = json.loads(job_data['result'])
        
        # Visualize Insights
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Summary")
            st.write(insights['summary'])
            st.subheader("Next Steps")
            for step in insights['next_steps']:
                st.write(f"- {step}")
        
        with col2:
            st.subheader("Entities")
            st.json({
                "Competitors": insights['competitors'],
                "Budget": insights['budget'],
                "Timeline": insights['timeline'],
                "Sentiment Score": insights['sentiment_score']
            })