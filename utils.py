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