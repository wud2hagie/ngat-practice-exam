# NGAT Practice Exam

A Streamlit-based multiple-choice practice exam with question navigation, answer tracking, review flags, scoring and answer explanations.

## Requirements

- Python 3.14 or newer
- `uv`

## Run locally

```bash
uv sync
uv run streamlit run streamlit_app.py
```

## Question bank

Edit `questions.json` to add questions. Each entry must contain:

- `section`: section name
- `question`: question text
- `options`: at least two answer choices
- `answer`: zero-based index of the correct option
- `explanation`: optional explanation shown after submission

The app validates the question bank at startup and reports malformed entries.

## Notes

This is a practice tool, not an authenticated examination platform. Answers and progress are stored in Streamlit session state and are not persisted to a user account or database.
