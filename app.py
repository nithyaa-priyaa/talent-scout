import streamlit as st
import re
from utils import extract_text, classify_document, rank_resumes

st.set_page_config(layout="wide")

st.title("Talent AI")

# ---------------- SESSION ----------------
if "files" not in st.session_state:
    st.session_state.files = []

if "results" not in st.session_state:
    st.session_state.results = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "limit_applied" not in st.session_state:
    st.session_state.limit_applied = False


# ---------------- JD CLEANING ----------------
def clean_jd(text):
    if not text:
        return ""
    # remove extra spaces + normalize
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_valid_jd(text):
    text = clean_jd(text)
    words = text.split()

    if len(words) < 2:
        return False

    clean_words = [w for w in words if re.search(r"[a-zA-Z0-9]", w)]
    return len(clean_words) >= 2


# ================== MAIN LAYOUT ==================
left, right = st.columns([2, 1])


# ================== LEFT ==================
with left:

    # -------- JD --------
    st.markdown("## Job Description")

    jd_mode = st.radio("Choose Input Type", ["Text", "Upload PDF"])

    jd_text = ""

    if jd_mode == "Text":
        jd_text = st.text_area("Enter Job Description")

    else:
        jd_file = st.file_uploader("Upload JD PDF", type=["pdf"], key="jd_pdf")

        if jd_file:
            jd_text = extract_text(jd_file)

            with st.expander("View Extracted Text", expanded=False):
                st.write(jd_text if jd_text else "No text found")

    jd_text = clean_jd(jd_text)
    st.session_state.jd_text = jd_text

    # -------- UPLOAD --------
    st.markdown("## Upload Resumes")

    col_left, col_right = st.columns([8, 1])

    with col_left:
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key=st.session_state.uploader_key
        )

    with col_right:
        if st.session_state.files:
            if st.button("✖", help="Clear all files"):
                st.session_state.files = []
                st.session_state.results = None
                st.session_state.jd_text = ""
                st.session_state.limit_applied = False
                st.session_state.uploader_key += 1
                st.rerun()

    # -------- APPEND FILES --------
    if uploaded_files:
        existing_names = [f.name for f in st.session_state.files]
        for f in uploaded_files:
            if f.name not in existing_names:
                st.session_state.files.append(f)

    files = st.session_state.files
    total_files = len(files)

    # ---------------- LIMIT ----------------
    if total_files > 50 and not st.session_state.limit_applied:
        st.warning(f"{total_files} files uploaded. Max allowed is 50.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Use first 50"):
                st.session_state.files = files[:50]
                st.session_state.limit_applied = True
                st.success("✅ Using first 50 files. You can now run evaluation.")
                st.rerun()

        with col2:
            if st.button("Clear"):
                st.session_state.files = []
                st.session_state.uploader_key += 1
                st.session_state.limit_applied = False
                st.rerun()

    # -------- RUN --------
    st.markdown("---")
    run_clicked = st.button("Run Evaluation")

    # -------- PROCESS --------
    if run_clicked:

        if not is_valid_jd(jd_text):
            st.error("Enter a valid Job Description")
            st.stop()

        if total_files == 0:
            st.error("Upload at least one resume")
            st.stop()

        if total_files > 50 and not st.session_state.limit_applied:
            st.error("Please reduce files using 'Use first 50'")
            st.stop()

        processed = []
        progress = st.progress(0)

        for i, f in enumerate(files):
            text = extract_text(f)
            doc_type = classify_document(text)

            processed.append({
                "name": f.name,
                "text": text,
                "type": doc_type
            })

            progress.progress((i + 1) / len(files))

        ranked, rejected = rank_resumes(jd_text, processed)
        st.session_state.results = (ranked, rejected)

    # -------- RESULTS --------
    if st.session_state.results:

        ranked, rejected = st.session_state.results

        st.success("Evaluation Complete")

        valid = [r for r in ranked if r["type"] in ["resume", "maybe_resume"]]

        if not valid:
            st.warning("No strong resumes detected. Showing fallback.")
            valid = [r for r in ranked if r["type"] != "empty"]

        if len(valid) == 0:
            st.error("No usable files found")
            st.stop()

        n = len(valid)
        top_n = 1 if n == 1 else st.slider("Top Candidates", 1, n, min(5, n))

        st.subheader("Ranking")

        for i, r in enumerate(valid[:top_n]):
            st.write(f"{i+1}. {r['name']} — {round(r['score']*100,2)}%")

        if n > top_n:
            with st.expander("View More"):
                for i, r in enumerate(valid[top_n:]):
                    st.write(f"{top_n+i+1}. {r['name']} — {round(r['score']*100,2)}%")

        # ==============================================================
        # ✅ CATALYST OUTREACH & COMBINED SCORING FEATURE
        # ==============================================================
        st.markdown("---")
        st.subheader("💬 AI Candidate Engagement & Combined Scoring")
        st.caption("Simulates conversational outreach to calculate an Interest Score.")

        if st.button("Simulate Outreach for Top Candidates"):
            with st.spinner("AI is reaching out to candidates..."):
                try:
                    from outreach import engage_and_evaluate
                    
                    for i, r in enumerate(valid[:top_n]):
                        engagement_data = engage_and_evaluate(st.session_state.jd_text, r['text'])
                        
                        match_score = r['score']
                        interest_score = engagement_data.get('interest_score', 0.5)
                        final_score = (match_score * 0.5) + (interest_score * 0.5)
                        
                        with st.expander(f"🤝 Outreach: {r['name']} | Combined Score: {round(final_score*100, 1)}%", expanded=False):
                            st.markdown(f"**Match Score:** {round(match_score*100, 1)}% | **Interest Score:** {round(interest_score*100, 1)}%")
                            
                            st.markdown("**📱 Simulated Transcript:**")
                            st.info(engagement_data.get('transcript', 'Simulation failed.'))
                            
                            st.caption("*(Note: This is a simulated conversation for prototype purposes. In a production environment, this module would integrate with a live chatbot API to engage the candidate in real-time.)*")
                            
                            st.markdown("**🔍 Resume Reasoning:**")
                            st.write(engagement_data.get('resume_reasoning', 'No explanation provided.'))
                            
                            st.markdown("**💡 Interest Score Reasoning:**")
                            st.write(engagement_data.get('score_reasoning', 'No explanation provided.'))
                            
                except ImportError:
                    st.error("Could not find 'outreach.py'. Please ensure it is in the same folder.")
                except Exception as e:
                    st.error(f"An error occurred during simulation: {e}")


# ================== RIGHT ==================
with right:

    st.markdown("## 📊 Processing Panel")

    if st.session_state.files:

        st.markdown("### 🔍 Resume Text Viewer")

        file_names = [f.name for f in st.session_state.files]
        selected_file_name = st.selectbox("Select a file", file_names)
        selected_file = next((f for f in st.session_state.files if f.name == selected_file_name), None)

        if selected_file:
            text = extract_text(selected_file)

            with st.expander("View Extracted Text", expanded=False):
                if text:
                    st.write(text[:3000])
                else:
                    st.warning("No text extracted")

    if st.session_state.files:

        st.markdown("### 📄 Selected Files")

        with st.expander(f"{len(st.session_state.files)} files loaded"):
            for f in st.session_state.files:
                st.write(f.name)

    if st.session_state.results:

        ranked, rejected = st.session_state.results

        valid = [r for r in ranked if r["type"] in ["resume", "maybe_resume"]]
        not_resume = [r for r in ranked + rejected if r["type"] == "not_resume"]
        empty = [r for r in ranked + rejected if r["type"] == "empty"]
        too_small = [r for r in ranked + rejected if r["type"] == "too_small"]

        st.markdown("### 📂 Classification")

        with st.expander(f"Valid ({len(valid)})"):
            st.write([r["name"] for r in valid] or "None")

        with st.expander(f"Not Resume ({len(not_resume)})"):
            st.write([r["name"] for r in not_resume] or "None")

        with st.expander(f"Empty ({len(empty)})"):
            st.write([r["name"] for r in empty] or "None")

        with st.expander(f"Too Small ({len(too_small)})"):
            st.write([r["name"] for r in too_small] or "None")