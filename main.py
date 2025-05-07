import streamlit as st
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import re

load_dotenv()

# --- Custom CSS to make sidebar black ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #000000;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# extract video ID from a YouTube URL
def extract_video_id(youtube_video_url):
    pattern = r"(?:v=|/v/|youtu\.be/|/embed/|watch\\?v=|watch/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, youtube_video_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL. Could not extract video ID.")

# fetch video metadata
def get_video_metadata(video_id):
    try:
        response = requests.get(f"https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v={video_id}&format=json")
        if response.status_code == 200:
            data = response.json()
            return data.get("title"), data.get("author_name")
        else:
            return "Unknown Title", "Unknown Channel"
    except Exception:
        return "Unknown Title", "Unknown Channel"

# transcript data from YouTube videos
def extract_transcript_details(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Streamlit app layout
st.title("YouTube Decoder")

# Input YouTube link
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)

        # Fetch metadata
        title, channel = get_video_metadata(video_id)

        # Sidebar content
        with st.sidebar:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=200)
            st.markdown(f"<p style='color:white;'><strong>Title:</strong> {title}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white;'><strong>Channel:</strong> {channel}</p>", unsafe_allow_html=True)

        if st.button("Generate Transcript"):
            transcript_text = extract_transcript_details(video_id)

            if "Error" in transcript_text:
                st.error(transcript_text)
            else:
                st.markdown("### Transcript")
                st.text_area("Transcript", transcript_text, height=300, disabled=True)
                st.download_button("Download Transcript", transcript_text, file_name="Transcript.txt", mime="text/plain")

    except ValueError as ve:
        st.error(str(ve))


