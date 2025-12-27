import streamlit as st
from utils import get_keywords

if 'page' not in st.session_state:
    st.session_state['page'] = 1
if 'stuck_type' not in st.session_state:
    st.session_state['stuck_type'] = ''
if 'problem_description' not in st.session_state:
    st.session_state['problem_description'] = ''

def process_ai_step():
    with st.spinner("Thinking..."):
        desc = st.session_state['problem_description']
        keywords = get_keywords(desc)
        # We save it to session_state so it stays in memory
        st.session_state['keywords'] = keywords
        # Move to the next page
        st.session_state['page'] = 5

if st.session_state['page'] == 1:
    st.title("Feeling stuck?")
    st.write("Click the button below to get help.")

    st.empty()
    st.empty()

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("I'm Stuck"):
            st.session_state['page'] = 2

elif st.session_state['page'] == 2:
    st.title("Pick the one that describes where you're stuck:")
    
    choice = st.selectbox(
        "Choose one:",
        ["Academics", "Professional life", "Personal life"]
    )
    
    st.session_state['stuck_type'] = choice
    
    if st.button("Next"):
        st.session_state['page'] = 3

elif st.session_state['page'] == 3:
    st.title("Describe your problem")
    
    user_input = st.text_area("Type your problem here:")
    st.session_state['problem_description'] = user_input
    
    if st.button("Next"):
        st.session_state['page'] = 4

elif st.session_state['page'] == 4:
    st.title("Step 4: Duration")
    duration_choice = st.selectbox("How long have you been stuck?", ["Hours", "Days", "Weeks"])
    st.session_state['stuck_duration'] = duration_choice

    if st.button("Generate My Path"):
        # This creates a "Live Log" on your screen
        log_area = st.empty() 
        log_area.info("⏳ Step 1: Contacting the AI...")
        
        try:
            # Call your function from utils.py
            keywords = get_keywords(st.session_state['problem_description'])
            
            if keywords:
                log_area.success(f"✅ Step 2: AI responded with: {keywords}")
                st.session_state['keywords'] = keywords
                
                # Give us 2 seconds to read the success message before switching
                import time
                time.sleep(2)
                
                st.session_state['page'] = 5
                st.rerun()
            else:
                log_area.warning("⚠️ AI returned nothing. Using 'general' instead.")
                st.session_state['keywords'] = ["general"]
                st.session_state['page'] = 5
                st.rerun()
                
        except Exception as e:
            log_area.error(f"❌ Error during AI Step: {e}")

elif st.session_state['page'] == 5:
    st.title("Step 5: Your Themes")
    
    if 'keywords' in st.session_state:
        st.write("The AI found these keywords for you:")
        # Show them in a nice list
        for word in st.session_state['keywords']:
            st.button(f"🔍 {word}", disabled=True)
    else:
        st.write("No keywords found. Let's try again.")
        
    if st.button("Go Back"):
        st.session_state['page'] = 1
        st.rerun()
