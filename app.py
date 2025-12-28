import streamlit as st
import time  
import os  # Added for CSS path handling
from utils import get_keywords, get_bingo_steps, get_next_step

# --- CSS LOADING SYSTEM ---
def load_css():
    # Get the directory where app.py is located
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, "styles", "main.css")
    try:
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Silently fail or show a small warning if styles folder isn't there yet
        pass

load_css()

# --- SESSION STATE INIT ---
if 'page' not in st.session_state:
    st.session_state['page'] = 1
if 'stuck_type' not in st.session_state:
    st.session_state['stuck_type'] = ''
if 'problem_description' not in st.session_state:
    st.session_state['problem_description'] = ''
if 'current_advice' not in st.session_state:
    st.session_state['current_advice'] = ''
if 'already_tried' not in st.session_state:
    st.session_state['already_tried'] = []

# --- PAGE 1: START ---
if st.session_state['page'] == 1:
    # Wrap in your custom CSS class from the old version
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.title("Feeling stuck?")
    st.write("Help is just a click away :)")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("I'm Stuck", use_container_width=True):
            st.session_state['page'] = 2
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE 2: TYPE ---
elif st.session_state['page'] == 2:
    st.title("Pick the one that describes where you're stuck:")
    choice = st.selectbox("Choose one:", ["Academics", "Professional life", "Personal life"])
    st.session_state['stuck_type'] = choice
    if st.button("Next"):
        st.session_state['page'] = 3
        st.rerun()

# --- PAGE 3: DESCRIPTION ---
elif st.session_state['page'] == 3:
    st.title("Describe your problem")
    user_input = st.text_area("Type your problem here:")
    if st.button("Next"):
        st.session_state['problem_description'] = user_input
        st.session_state['page'] = 4
        st.rerun()

# --- PAGE 4: GENERATION ---
elif st.session_state['page'] == 4:
    st.title("Step 4: Duration")
    duration_choice = st.selectbox("How long have you been stuck?", ["Hours", "Days", "Weeks"])
    st.session_state['stuck_duration'] = duration_choice

    if st.button("Generate My Path", type="primary"):
        log_area = st.empty() 
        log_area.info("⏳ Step 1: Contacting the AI...")
        try:
            keywords = get_keywords(st.session_state['problem_description'])
            st.session_state['keywords'] = keywords
            
            log_area.info("⏳ Step 2: Building your Bingo Board...")
            st.session_state['bingo_steps'] = get_bingo_steps(st.session_state['problem_description'], keywords)
            
            log_area.success(f"✅ Ready! Themes found: {', '.join(keywords)}")
            time.sleep(1.5) 
            st.session_state['page'] = 5
            st.rerun()
        except Exception as e:
            log_area.error(f"❌ Error: {e}")

# --- PAGE 5: BINGO BOARD ---
elif st.session_state['page'] == 5:
    st.title("🧩 Stuck Bingo")
    st.write("Select the things you've already tried. (Select at least one to proceed!)")
    
    steps = st.session_state.get('bingo_steps', [])
    cols = st.columns(3)
    current_tried = []
    
    for i, step in enumerate(steps):
        with cols[i % 3]:
            if st.checkbox(step, key=f"bingo_box_{i}"):
                current_tried.append(step)
    
    st.session_state['already_tried'] = current_tried
    st.divider()

    st.subheader("🛠️ Quick Help Tools")
    col_v, col_d = st.columns(2)
    
    with col_v:
        if st.button("I just need to vent 🎈", use_container_width=True):
            st.session_state['page'] = "vent"
            st.rerun()

    with col_d:
        if st.session_state.get('stuck_type') == "Academics":
            if st.button("Fix My Code 💻", use_container_width=True):
                st.session_state['page'] = "debugger"
                st.rerun()
    
    st.divider()

    selection_made = len(st.session_state['already_tried']) > 0
    if st.button("I'm still stuck - Help me!", type="primary", disabled=not selection_made, use_container_width=True):
        st.session_state['current_advice'] = '' 
        st.session_state['page'] = 6
        st.rerun()
    
    if not selection_made:
        st.caption("⚠️ Please check at least one box above to continue.")

# --- VENT PAGE ---
elif st.session_state['page'] == "vent":
    st.title("🎈 The Venting Room")
    st.write("This is a safe space. Just let it out.")
    st.text_area("Type whatever is on your mind...", height=300)
    if st.button("I feel a bit better now"):
        st.session_state['page'] = 5
        st.rerun()

# --- DEBUGGER PAGE ---
elif st.session_state['page'] == "debugger":
    st.title("💻 Academic Code Debugger")
    st.write("Paste your code below, and I'll try to find the bugs for you.")
    code_input = st.text_area("Paste code here...", height=300)
    if st.button("Analyze & Fix"):
        if code_input:
            with st.spinner("Hunting for bugs..."):
                from utils import fix_my_code
                solution = fix_my_code(code_input)
                st.markdown("### 🔍 The Solution")
                st.code(solution)
        else:
            st.warning("Please paste some code first!")
    if st.button("Go Back to Bingo"):
        st.session_state['page'] = 5
        st.rerun()

# --- PAGE 6: ADVICE LOOP ---
elif st.session_state['page'] == 6:
    st.title("🌱 Your Next Small Step")
    if not st.session_state.get('current_advice'):
        st.session_state['current_advice'] = get_next_step(
            st.session_state['problem_description'], 
            st.session_state['already_tried']
        )
        st.session_state['advice_history'] = []

    st.info(st.session_state['current_advice'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("That worked! 🎉", use_container_width=True):
            st.session_state['page'] = "finished"
            st.rerun()
    with col2:
        if st.button("Still stuck... next step?", use_container_width=True):
            st.session_state['advice_history'].append(st.session_state['current_advice'])
            st.session_state['current_advice'] = get_next_step(
                st.session_state['problem_description'], 
                st.session_state['already_tried'],
                history=str(st.session_state['advice_history'])
            )
            st.rerun()

# --- FINISHED PAGE ---
elif st.session_state['page'] == "finished":
    st.balloons()
    st.title("You did it!")
    st.success("So proud of you for pushing through.")
    if st.button("Start Another Journey"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.session_state['page'] = 1 
        st.rerun()
        
# import streamlit as st
# import time  
# from utils import get_keywords, get_bingo_steps, get_next_step

# # --- SESSION STATE INIT ---
# if 'page' not in st.session_state:
#     st.session_state['page'] = 1
# if 'stuck_type' not in st.session_state:
#     st.session_state['stuck_type'] = ''
# if 'problem_description' not in st.session_state:
#     st.session_state['problem_description'] = ''
# if 'current_advice' not in st.session_state:
#     st.session_state['current_advice'] = ''
# if 'already_tried' not in st.session_state:
#     st.session_state['already_tried'] = []

# # --- PAGE 1: START ---
# if st.session_state['page'] == 1:
#     st.title("Feeling stuck?")
#     st.write("Click the button below to get help.")
#     col1, col2, col3 = st.columns([1, 3, 1])
#     with col2:
#         if st.button("I'm Stuck", use_container_width=True):
#             st.session_state['page'] = 2
#             st.rerun()

# # --- PAGE 2: TYPE ---
# elif st.session_state['page'] == 2:
#     st.title("Pick the one that describes where you're stuck:")
#     choice = st.selectbox("Choose one:", ["Academics", "Professional life", "Personal life"])
#     st.session_state['stuck_type'] = choice
#     if st.button("Next"):
#         st.session_state['page'] = 3
#         st.rerun()

# # --- PAGE 3: DESCRIPTION ---
# elif st.session_state['page'] == 3:
#     st.title("Describe your problem")
#     user_input = st.text_area("Type your problem here:")
#     if st.button("Next"):
#         st.session_state['problem_description'] = user_input
#         st.session_state['page'] = 4
#         st.rerun()

# # --- PAGE 4: GENERATION ---
# elif st.session_state['page'] == 4:
#     st.title("Step 4: Duration")
#     duration_choice = st.selectbox("How long have you been stuck?", ["Hours", "Days", "Weeks"])
#     st.session_state['stuck_duration'] = duration_choice

#     if st.button("Generate My Path", type="primary"):
#         log_area = st.empty() 
#         log_area.info("⏳ Step 1: Contacting the AI...")
#         try:
#             # Get Keywords
#             keywords = get_keywords(st.session_state['problem_description'])
#             st.session_state['keywords'] = keywords
            
#             # Get Bingo Steps
#             log_area.info("⏳ Step 2: Building your Bingo Board...")
#             st.session_state['bingo_steps'] = get_bingo_steps(st.session_state['problem_description'], keywords)
            
#             log_area.success(f"✅ Ready! Themes found: {', '.join(keywords)}")
#             time.sleep(1.5) 
#             st.session_state['page'] = 5
#             st.rerun()
#         except Exception as e:
#             log_area.error(f"❌ Error: {e}")

# # --- PAGE 5: BINGO BOARD ---
# elif st.session_state['page'] == 5:
#     st.title("🧩 Stuck Bingo")
#     st.write("Select the things you've already tried. (Select at least one to proceed!)")
    
#     steps = st.session_state.get('bingo_steps', [])
#     cols = st.columns(3)
#     current_tried = []
    
#     for i, step in enumerate(steps):
#         with cols[i % 3]:
#             if st.checkbox(step, key=f"bingo_box_{i}"):
#                 current_tried.append(step)
    
#     st.session_state['already_tried'] = current_tried
#     st.divider()

#     # --- TOOLS SECTION ---
#     st.subheader("🛠️ Quick Help Tools")
#     col_v, col_d = st.columns(2)
    
#     with col_v:
#         if st.button("I just need to vent 🎈", use_container_width=True):
#             st.session_state['page'] = "vent"
#             st.rerun()

#     with col_d:
#         if st.session_state.get('stuck_type') == "Academics":
#             if st.button("Fix My Code 💻", use_container_width=True):
#                 st.session_state['page'] = "debugger"
#                 st.rerun()
    
#     st.divider()

#     # --- PROGRESS BUTTON ---
#     selection_made = len(st.session_state['already_tried']) > 0
#     if st.button("I'm still stuck - Help me!", type="primary", disabled=not selection_made, use_container_width=True):
#         st.session_state['current_advice'] = '' 
#         st.session_state['page'] = 6
#         st.rerun()
    
#     if not selection_made:
#         st.caption("⚠️ Please check at least one box above to continue.")

# # --- VENT PAGE ---
# elif st.session_state['page'] == "vent":
#     st.title("🎈 The Venting Room")
#     st.write("This is a safe space. No advice, no judgment. Just let it out.")
#     st.text_area("Type whatever is on your mind...", height=300)
#     if st.button("I feel a bit better now"):
#         st.session_state['page'] = 5
#         st.rerun()

# # --- DEBUGGER PAGE ---
# elif st.session_state['page'] == "debugger":
#     st.title("💻 Academic Code Debugger")
#     st.write("Paste your code below, and I'll try to find the bugs for you.")
#     code_input = st.text_area("Paste code here...", height=300)
#     if st.button("Analyze & Fix"):
#         if code_input:
#             with st.spinner("Hunting for bugs..."):
#                 from utils import fix_my_code
#                 solution = fix_my_code(code_input)
#                 st.markdown("### 🔍 The Solution")
#                 st.code(solution)
#         else:
#             st.warning("Please paste some code first!")
#     if st.button("Go Back to Bingo"):
#         st.session_state['page'] = 5
#         st.rerun()

# # --- PAGE 6: ADVICE LOOP ---
# elif st.session_state['page'] == 6:
#     st.title("🌱 Your Next Small Step")
#     if not st.session_state.get('current_advice'):
#         st.session_state['current_advice'] = get_next_step(
#             st.session_state['problem_description'], 
#             st.session_state['already_tried']
#         )
#         st.session_state['advice_history'] = []

#     st.info(st.session_state['current_advice'])
    
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("That worked! 🎉", use_container_width=True):
#             st.session_state['page'] = "finished"
#             st.rerun()
#     with col2:
#         if st.button("Still stuck... next step?", use_container_width=True):
#             st.session_state['advice_history'].append(st.session_state['current_advice'])
#             st.session_state['current_advice'] = get_next_step(
#                 st.session_state['problem_description'], 
#                 st.session_state['already_tried'],
#                 history=str(st.session_state['advice_history'])
#             )
#             st.rerun()

# # --- FINISHED PAGE ---
# elif st.session_state['page'] == "finished":
#     st.balloons()
#     st.title("You did it!")
#     st.success("So proud of you for pushing through.")
#     if st.button("Start Another Journey"):
#         for key in list(st.session_state.keys()): del st.session_state[key]
#         st.session_state['page'] = 1 
#         st.rerun()  
