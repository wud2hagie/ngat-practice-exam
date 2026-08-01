import streamlit as st
import json
import os

# --- CONFIGURATION & DATA LOADING ---
QUESTIONS_FILE = "questions.json"

@st.cache_data
def load_questions():
    if not os.path.exists(QUESTIONS_FILE):
        st.error(f"Error: {QUESTIONS_FILE} not found. Please create it.")
        return []
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --- INITIALIZE SESSION STATE ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'marked' not in st.session_state:
    st.session_state.marked = set()

def go_to_question(q_index):
    st.session_state.current_q = q_index

def submit_exam():
    st.session_state.submitted = True

# --- MAIN APP ---
st.set_page_config(page_title="NGAT Practice Exam", page_icon="🎓", layout="wide")

questions = load_questions()

if questions:
    # --- SIDEBAR: QUESTION PALETTE ---
    with st.sidebar:
        st.title("NGAT Exam")
        st.write(f"**Total Questions:** {len(questions)}")
        
        if not st.session_state.submitted:
            st.subheader("Question Palette")
            # Create a grid of buttons for navigation
            cols = st.columns(5)
            for i in range(len(questions)):
                with cols[i % 5]:
                    # Button styles based on state
                    if i in st.session_state.marked:
                        btn_label = f"🔵 {i+1}"
                    elif i in st.session_state.user_answers:
                        btn_label = f"🟢 {i+1}"
                    else:
                        btn_label = f"{i+1}"
                        
                    if st.button(btn_label, key=f"nav_{i}", help=f"Go to question {i+1}"):
                        go_to_question(i)
            
            st.divider()
            if st.button("Submit Exam", type="primary", use_container_width=True):
                submit_exam()

        st.divider()
        st.write("Built for NGAT Prep")

    # --- MAIN AREA: QUESTION DISPLAY ---
    if not st.session_state.submitted:
        q_index = st.session_state.current_q
        q_data = questions[q_index]
        section = q_data.get("section", "General")
        
        st.header(f"Section: {section}")
        st.subheader(f"Question {q_index + 1} of {len(questions)}")
        
        # Progress bar
        progress = int(((q_index + 1) / len(questions)) * 100)
        st.progress(progress)
        
        st.write(f"**{q_data['question']}**")
        
        # Radio buttons for options
        options = q_data["options"]
        current_selection = st.session_state.user_answers.get(q_index, None)
        
        selected_option = st.radio(
            "Select your answer:",
            options=options,
            index=current_selection,
            key=f"q_radio_{q_index}"
        )
        
        # Save answer immediately when selected
        if selected_option is not None:
            st.session_state.user_answers[q_index] = options.index(selected_option)
            
        # Mark for review button
        if st.button("Mark for Review 🔵"):
            if q_index in st.session_state.marked:
                st.session_state.marked.remove(q_index)
            else:
                st.session_state.marked.add(q_index)
            st.rerun()

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button("⬅️ Previous", disabled=(q_index == 0)):
                st.session_state.current_q -= 1
                st.rerun()
        with col3:
            if st.button("Next ➡️", disabled=(q_index == len(questions) - 1)):
                st.session_state.current_q += 1
                st.rerun()

    # --- RESULTS & FEEDBACK SCREEN ---
    if st.session_state.submitted:
        st.title("Exam Results & Feedback")
        
        # Calculate Score
        score = 0
        for i, q in enumerate(questions):
            if st.session_state.user_answers.get(i) == q["answer"]:
                score += 1
                
        percentage = (score / len(questions)) * 100
        
        # Display Score Card
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Score", f"{score} / {len(questions)}")
        col2.metric("Percentage", f"{percentage:.1f}%")
        col3.metric("Unanswered", f"{len(questions) - len(st.session_state.user_answers)}")
        
        if percentage >= 50:
            st.success("Congratulations! You passed the practice exam.")
        else:
            st.warning("Keep practicing. Review the feedback below.")
            
        st.divider()
        st.header("Detailed Feedback")
        
        # Show every question with correct/incorrect highlighting
        for i, q in enumerate(questions):
            user_ans_idx = st.session_state.user_answers.get(i)
            correct_ans_idx = q["answer"]
            is_correct = user_ans_idx == correct_ans_idx
            
            with st.container():
                if is_correct:
                    st.success(f"**Q{i+1}. {q['question']}**")
                else:
                    st.error(f"**Q{i+1}. {q['question']}**")
                
                # Display options with color coding
                for opt_idx, opt in enumerate(q["options"]):
                    if opt_idx == correct_ans_idx:
                        st.markdown(f"✅ **{opt}** *(Correct Answer)*")
                    elif opt_idx == user_ans_idx:
                        st.markdown(f"❌ ~~{opt}~~ *(Your Answer)*")
                    else:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{opt}")
                st.write("---")
                
        if st.button("Retake Exam"):
            st.session_state.submitted = False
            st.session_state.user_answers = {}
            st.session_state.current_q = 0
            st.session_state.marked = set()
            st.rerun()