"""
app.py
------
Main Streamlit application. Ties together recording, transcription,
summarization, database storage, and Word export into one UI.

Run with:
    streamlit run app.py
"""

import streamlit as st

from audio_recorder import AudioRecorder
from transcriber import transcribe_audio
from summarizer import generate_meeting_insights
from docx_generator import create_meeting_docx
from database import init_db, save_meeting, get_all_meetings

# --- One-time setup ---
init_db()  # make sure the meetings table exists before anything else runs

st.set_page_config(page_title="AI Meeting Assistant", layout="wide")
st.title("🎙️ AI Meeting Assistant")

# --- Session state initialization ---
# Streamlit reruns the script top-to-bottom on every interaction, so any
# data that needs to persist between reruns (like the recorder object,
# the current transcript, etc.) must live in st.session_state.
if "recorder" not in st.session_state:
    st.session_state.recorder = AudioRecorder()
if "wav_path" not in st.session_state:
    st.session_state.wav_path = None
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "insights" not in st.session_state:
    st.session_state.insights = None
if "docx_path" not in st.session_state:
    st.session_state.docx_path = None

recorder = st.session_state.recorder

tab_record, tab_history = st.tabs(["🎤 New Meeting", "📚 Meeting History"])

# ============================================================
# TAB 1: Record, transcribe, summarize a new meeting
# ============================================================
with tab_record:
    st.subheader("Step 1: Record Meeting Audio")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("● Start Recording", disabled=recorder.is_recording):
            recorder.start()
            st.success("Recording started... speak now.")

    with col2:
        if st.button("■ Stop Recording", disabled=not recorder.is_recording):
            wav_path = recorder.stop_and_save()
            st.session_state.wav_path = wav_path
            st.success(f"Recording saved: {wav_path}")

    if recorder.is_recording:
        st.info("🔴 Recording in progress... click Stop when finished.")

    # --- Step 2: Transcribe ---
    if st.session_state.wav_path:
        st.audio(st.session_state.wav_path)
        st.subheader("Step 2: Transcribe Audio")

        if st.button("Transcribe with Whisper"):
            with st.spinner("Transcribing audio... this may take a moment."):
                st.session_state.transcript = transcribe_audio(st.session_state.wav_path)
            st.success("Transcription complete!")

    # --- Step 3: Show transcript + generate insights ---
    if st.session_state.transcript:
        st.subheader("Transcript")
        st.text_area("Transcript", st.session_state.transcript, height=200, label_visibility="collapsed")

        st.subheader("Step 3: Generate AI Insights")
        if st.button("Generate Summary / MoM / Action Items"):
            with st.spinner("Contacting Groq API..."):
                st.session_state.insights = generate_meeting_insights(st.session_state.transcript)
            st.success("Insights generated!")

    # --- Step 4: Display insights + save + export ---
    if st.session_state.insights:
        insights = st.session_state.insights

        st.subheader("📄 Meeting Summary")
        st.write(insights["summary"])

        st.subheader("📝 Minutes of Meeting (MoM)")
        st.write(insights["mom"])

        st.subheader("✅ Action Items")
        if insights["action_items"]:
            for item in insights["action_items"]:
                st.markdown(f"- {item}")
        else:
            st.write("No action items identified.")

        st.subheader("📌 Key Decisions")
        if insights["key_decisions"]:
            for decision in insights["key_decisions"]:
                st.markdown(f"- {decision}")
        else:
            st.write("No key decisions identified.")

        st.divider()
        meeting_title = st.text_input("Meeting title (for saving)", value="Untitled Meeting")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Save to Database"):
                save_meeting(meeting_title, st.session_state.transcript, insights)
                st.success("Meeting saved to database!")

        with col_b:
            if st.button("📥 Generate Word Document"):
                st.session_state.docx_path = create_meeting_docx(meeting_title, insights)

        if st.session_state.docx_path:
            with open(st.session_state.docx_path, "rb") as f:
                st.download_button(
                    label="Download .docx",
                    data=f.read(),
                    file_name=st.session_state.docx_path.split("/")[-1].split("\\")[-1],
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

# ============================================================
# TAB 2: View history of past meetings
# ============================================================
with tab_history:
    st.subheader("Previous Meetings")
    meetings = get_all_meetings()

    if not meetings:
        st.info("No meetings saved yet.")
    else:
        for meeting in meetings:
            with st.expander(f"{meeting['title']}  —  {meeting['created_at']}"):
                st.markdown("**Summary**")
                st.write(meeting["summary"])

                st.markdown("**Minutes of Meeting**")
                st.write(meeting["mom"])

                st.markdown("**Action Items**")
                if meeting["action_items"]:
                    for item in meeting["action_items"]:
                        st.markdown(f"- {item}")
                else:
                    st.write("None")

                st.markdown("**Key Decisions**")
                if meeting["key_decisions"]:
                    for decision in meeting["key_decisions"]:
                        st.markdown(f"- {decision}")
                else:
                    st.write("None")

                st.markdown("**Full Transcript**")
                st.text_area(
                    "Transcript",
                    meeting["transcript"],
                    height=150,
                    key=f"transcript_{meeting['id']}",
                    label_visibility="collapsed",
                )
