import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import urlparse, parse_qs

load_dotenv()  # Load all environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for Gemini
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# Improved video ID extraction
def extract_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    elif parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    return None

# Fetch transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("Invalid YouTube link (could not extract video id).")
            return None
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id, languages=["en"])  # or omit languages if you want auto
        transcript = " ".join(
            [
                (i["text"] if isinstance(i, dict) else getattr(i, "text", str(i)))
                for i in transcript_list
            ]
        )
        return transcript
    except Exception as e:
        st.error(e)

# Generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    # Use a currently supported Gemini model name
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Streamlit App UI
st.title("🎥 YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width="stretch")
    else:
        st.error("Invalid YouTube link.")

if st.button("Get summary of the video"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        with st.spinner("generating content"):
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("📝 Detailed Notes")
            st.write(summary)
            st.success("Done ✅")
