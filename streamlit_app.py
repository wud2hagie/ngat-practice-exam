import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="NGAT Practice Exam", page_icon="🎓", layout="wide")

QUESTIONS_FILE = Path(__file__).with_name("questions.json")


@st.cache_data
def load_questions():
    """Load and validate the exam bank before showing any questions."""
    with QUESTIONS_FILE.open("r", encoding="utf-8") as file:
        raw_questions = json.load(file)

    if not isinstance(raw_questions, list) or not raw_questions:
        raise ValueError("The question bank must be a non-empty JSON list.")

    validated = []
    for number, question in enumerate(raw_questions, start=1):
        if not isinstance(question, dict):
            raise ValueError(f"Question {number} must be a JSON object.")
        prompt = question.get("question")
        options = question.get("options")
        answer = question.get("answer")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"Question {number} has no valid question text.")
        if not isinstance(options, list) or len(options) < 2 or not all(
            isinstance(option, str) and option.strip() for option in options
        ):
            raise ValueError(f"Question {number} must have at least two non-empty options.")
        if isinstance(answer, bool) or not isinstance(answer, int) or not 0 <= answer < len(options):
            raise ValueError(f"Question {number} has an invalid answer index.")
        validated.append({
            "section": str(question.get("section", "General")),
            "question": prompt.strip(),
            "options": options,
            "answer": answer,
            "explanation": str(question.get("explanation", "")),
        })
    return validated


def initialize_state():
    defaults = {
        "current_q": 0,
        "user_answers": {},
        "submitted": False,
        "marked": set(),
        "attempt": 1,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()

try:
    questions = load_questions()
except (OSError, json.JSONDecodeError, ValueError) as error:
    st.error(f"Unable to load the question bank: {error}")
    st.stop()

st.title("🎓 NGAT Practice Exam")
st.caption("Practice verbal, quantitative and analytical reasoning. Your answers stay in this browser session.")

if not st.session_state.submitted:
    with st.sidebar:
        st.subheader("Question navigator")
        st.write(f"**{len(questions)} questions**")
        for index in range(len(questions)):
            if index in st.session_state.marked:
                label = f"🔵 {index + 1} · Review"
            elif index in st.session_state.user_answers:
                label = f"🟢 {index + 1} · Answered"
            else:
                label = f"⚪ {index + 1} · Unanswered"
            if st.button(label, key=f"nav_{st.session_state.attempt}_{index}", use_container_width=True):
                st.session_state.current_q = index
                st.rerun()
        st.divider()
        answered = len(st.session_state.user_answers)
        st.progress(answered / len(questions), text=f"{answered} of {len(questions)} answered")
        if st.button("Submit exam", type="primary", use_container_width=True):
            st.session_state.submitted = True
            st.rerun()

    index = st.session_state.current_q
    question = questions[index]
    st.caption(f"Section: {question['section']}")
    st.subheader(f"Question {index + 1} of {len(questions)}")
    st.progress((index + 1) / len(questions))
    st.markdown(f"### {question['question']}")

    previous_answer = st.session_state.user_answers.get(index)
    selected = st.radio(
        "Choose one answer:",
        question["options"],
        index=previous_answer,
        key=f"answer_{st.session_state.attempt}_{index}",
    )
    if selected is not None:
        st.session_state.user_answers[index] = question["options"].index(selected)

    mark_label = "Remove review mark" if index in st.session_state.marked else "Mark for review"
    if st.button(mark_label):
        if index in st.session_state.marked:
            st.session_state.marked.remove(index)
        else:
            st.session_state.marked.add(index)
        st.rerun()

    left, spacer, right = st.columns([1, 4, 1])
    with left:
        if st.button("← Previous", disabled=index == 0, use_container_width=True):
            st.session_state.current_q -= 1
            st.rerun()
    with right:
        if st.button("Next →", disabled=index == len(questions) - 1, use_container_width=True):
            st.session_state.current_q += 1
            st.rerun()
else:
    score = sum(
        st.session_state.user_answers.get(i) == question["answer"]
        for i, question in enumerate(questions)
    )
    total = len(questions)
    percentage = score / total * 100
    st.header("Your results")
    a, b, c = st.columns(3)
    a.metric("Score", f"{score} / {total}")
    b.metric("Percentage", f"{percentage:.1f}%")
    c.metric("Unanswered", total - len(st.session_state.user_answers))
    if percentage >= 50:
        st.success("Well done! You passed this practice attempt.")
    else:
        st.info("Keep practicing. Review the explanations and try again.")

    st.subheader("Answer review")
    for number, question in enumerate(questions, start=1):
        chosen = st.session_state.user_answers.get(number - 1)
        correct = question["answer"]
        with st.expander(f"Question {number}: {'Correct' if chosen == correct else 'Review needed'}"):
            st.write(question["question"])
            if chosen is not None:
                st.write(f"Your answer: {question['options'][chosen]}")
            else:
                st.write("Your answer: Not answered")
            st.success(f"Correct answer: {question['options'][correct]}")
            if question["explanation"]:
                st.write(question["explanation"])

    if st.button("Retake exam", type="primary"):
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.submitted = False
        st.session_state.marked = set()
        st.session_state.attempt += 1
        st.rerun()
