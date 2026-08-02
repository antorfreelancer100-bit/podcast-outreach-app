import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from google import genai
from google.genai import types

# পেজ সেটআপ
st.set_page_config(page_title="Podcast Outreach Assistant", page_icon="🎙️")
st.title("🎙️ Automated Podcast Cold Email Assistant")
st.caption("লিংক এবং নাম দিয়ে ১-ক্লিকে শর্ট ও পার্সোনালাইজড ইমেইল জেনারেট করুন।")

# Streamlit Secrets বা Environment থেকে API Key অটোমেটিক নেওয়া
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key পাওয়া যায়নি! Streamlit Secrets-এ GEMINI_API_KEY সেটিং করুন।")
    st.stop()

client = genai.Client(api_key=api_key)

# সাইডবারে আপনার প্রোফাইল কনফিগারেশন
st.sidebar.header("👤 Your Profile")
sender_name = st.sidebar.text_input("Your Name", "Antor Sarkar")
sender_role = st.sidebar.text_input("Your Title", "Podcast Growth Strategist")
my_milestone = st.sidebar.text_area("Key Case Study", "Generated 35,000+ downloads in a single month for a podcast client.")

# ব্যাকএন্ডে লিংক থেকে মেটাডেটা পড়ার ফাংশন
def fetch_url_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else ""
            paragraphs = " ".join([p.text for p in soup.find_all(['p', 'h1', 'h2'], limit=5)])
            return f"Page Title: {title}\nContent Snippet: {paragraphs[:1000]}"
    except Exception:
        return "Could not scrape URL directly, rely on AI knowledge."
    return ""

# ইনপুট ফিল্ড
st.header("📋 Input Podcast Details")
podcast_link = st.text_input("Podcast Link *", placeholder="https://spotify.com/... or Apple/YouTube link")
podcast_name = st.text_input("Podcast Name *", placeholder="e.g. The Growth Show")
host_name = st.text_input("Host Name (Optional)", placeholder="e.g. Sarah (খালি রাখলে AI নিজে খোঁজার চেষ্টা করবে)")

if st.button("🚀 Research & Write Email"):
    if not podcast_link or not podcast_name:
        st.warning("অনুগ্রহ করে অন্তত পডকাস্টের লিংক এবং নাম দিন!")
    else:
        with st.spinner("ব্যাকএন্ডে পডকাস্ট রিসার্চ করে শর্ট ইমেইল তৈরি করা হচ্ছে..."):
            
            scraped_info = fetch_url_content(podcast_link)

            system_instruction = f"""
            You are an expert, human-like Podcast Growth Strategist named {sender_name} ({sender_role}).
            Your job is to write high-converting, hyper-personalized, ultra-short cold emails to podcast hosts.

            Sender Info:
            - Name: {sender_name}
            - Role: {sender_role}
            - Key Result: {my_milestone}

            Strict Rules:
            1. SHORT & CONCISE: The email must be under 3 short paragraphs. No generic marketing fluff.
            2. NATURAL HUMAN TONE: Sound like a friendly expert who actually listened to their podcast.
            3. PERSONALIZATION: Deduce the host's name if not provided. Mention a specific hook related to their channel/content.
            4. CALL TO ACTION: Offer a simple, low-friction next step (e.g., "Open to a quick 5-min chat next week?").
            5. Provide 3 high-open-rate Subject Line options.
            """

            user_prompt = f"""
            Analyze and write a short cold email based on:
            - Podcast Name: {podcast_name}
            - Host Name: {host_name if host_name else "Unknown (Deduce if possible)"}
            - Podcast Link: {podcast_link}
            - Scraped Page Snippet: {scraped_info}
            """

            try:
                response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=user_prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,
    )
)
                st.success("✅ রিসার্চ সম্পন্ন এবং ইমেইল তৈরি হয়েছে!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {e}")
