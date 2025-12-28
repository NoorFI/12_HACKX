from google import genai
import streamlit as st
import time

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Wait! I can't find your API Key in secrets.toml.")
    st.stop()

client = genai.Client(api_key=API_KEY)

def get_keywords(description):
    model_id = 'gemini-2.0-flash' 
    prompt = f"""
    The user is stuck on this: "{description}"
    Give me 3-5 core topics they are struggling with (e.g., 'logic', 'math', 'python', 'syntax').
    Return ONLY a comma-separated list of lowercase words. 
    NO periods, NO sentences.
    """
    
    try:
        response = client.models.generate_content(
            model=model_id, 
            contents=prompt
        )
        if response.text:
            # 1. CLEANING: Remove newlines, asterisks, and dots the AI might add
            raw_text = response.text.replace("\n", "").replace("*", "").replace(".", "")
            
            # 2. SPLITTING: Split by comma and remove any empty strings
            keywords = [k.strip().lower() for k in raw_text.split(',') if k.strip()]
            
            # 3. VISIBILITY: This will show the keywords in your terminal so you can verify
            print(f"SUCCESS! Keywords found: {keywords}")
            
            return keywords
        return ["general"]
    except Exception as e:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt
            )
            # Apply the same cleaning here
            raw_text = response.text.replace("\n", "").replace("*", "").replace(".", "")
            return [k.strip().lower() for k in raw_text.split(',') if k.strip()]
        except:
            print(f"DEBUG ERROR: {e}")
            return ["general"]
        
def get_bingo_steps(description, keywords):
    model_id = 'gemini-2.0-flash'
    prompt = f"""
    Create 9 extremely short actions (max 3 words each) for someone stuck on: "{description}".
    Format: Action 1 | Action 2 | Action 3 | Action 4 | Action 5 | Action 6 | Action 7 | Action 8 | Action 9
    Return ONLY the actions separated by |. No intro text.
    """
    try:
        response = client.models.generate_content(model=model_id, contents=prompt)
        steps = [s.strip() for s in response.text.split('|')]
        if len(steps) >= 9:
            return steps[:9]
        return ["Check syntax", "Drink water", "Restart IDE", "Read docs", "Ask a friend", "Deep breath", "Simplify code", "Check logic", "Google error"]
    except:
        return ["Check syntax", "Drink water", "Restart IDE", "Read docs", "Ask a friend", "Deep breath", "Simplify code", "Check logic", "Google error"]
    
def get_next_step(description, tried_items, history=""):
    model_id = 'gemini-2.0-flash'
    prompt = f"""
    Problem: {description}
    Already tried: {tried_items}
    History of advice: {history}
    
    Give ONE specific micro-step and ONE helpful online resource link (YouTube or documentation).
    Tone: Very warm, reassuring, and empathetic. 
    If mental health related, focus on validation and comfort.
    """
    try:
        response = client.models.generate_content(model=model_id, contents=prompt)
        return response.text
    except:
        return "You're doing great. Let's try taking just one tiny step: breathe and re-read the goal."

def fix_my_code(code):
    # Try the newer model first
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash']
    
    prompt = f"""
    Find and fix the bugs in this code. 
    Explain the fix briefly and provide the corrected code.
    Code:
    {code}
    """

    for model_id in models_to_try:
        try:
            response = client.models.generate_content(model=model_id, contents=prompt)
            return response.text
        except Exception as e:
            # If it's a rate limit error, try the next model
            if "429" in str(e):
                continue 
            return f"Error: {e}"
            
    return "🚨 Both AI models are currently busy. Please wait 60 seconds and try again!"