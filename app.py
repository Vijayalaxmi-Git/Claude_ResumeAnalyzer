import streamlit as st
import pandas as pd
from utils import extract_text
from analyzer import safe_analyze_resume
from storage import (
    initialize_storage,
    save_result,
    load_results,
    filter_results,
    sort_results,
    update_notes,
    delete_candidate
)

# ── App Configuration ─────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ── Initialize Storage ────────────────────────────────────────
initialize_storage()

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .verdict-shortlist {
        background-color: #22c55e22;
        color: #22c55e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #22c55e44;
    }
    .verdict-maybe {
        background-color: #f59e0b22;
        color: #f59e0b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #f59e0b44;
    }
    .verdict-reject {
        background-color: #ef444422;
        color: #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #ef444444;
    }
    .score-high { color: #22c55e; font-size: 32px; font-weight: 700; }
    .score-mid  { color: #f59e0b; font-size: 32px; font-weight: 700; }
    .score-low  { color: #ef4444; font-size: 32px; font-weight: 700; }
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin: 3px;
    }
</style>
""", unsafe_allow_html=True)
# Section 3 — Sidebar navigation.
# ── Sidebar Navigation ────────────────────────────────────────
st.sidebar.image("https://www.anthropic.com/favicon.ico", width=30)
st.sidebar.title("📄 Resume Analyzer")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Analyze Resume", "📊 Dashboard", "📄 Candidate Detail"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Powered by Claude API**")
st.sidebar.markdown("Built for Recruiters & HR Teams")

#Section 4 — The Analyze Resume page!
# ── Page 1: Analyze Resume ────────────────────────────────────
if page == "🏠 Analyze Resume":
    st.title("🏠 Analyze Resume")
    st.markdown("Upload a resume and enter a job description to get AI-powered analysis.")
    st.markdown("---")

    # Job Description Input
    job_description = st.text_area(
        "📋 Job Description (optional but recommended)",
        height=150,
        placeholder="Paste the job description here for a tailored analysis..."
    )

    st.markdown("---")

    # Resume Input Method
    input_method = st.radio(
        "How would you like to provide the resume?",
        ["📁 Upload File (PDF/Word)", "📝 Paste Text"]
    )

    # ── Single File Upload ──
    if input_method == "📁 Upload File (PDF/Word)":
        upload_mode = st.radio(
            "Upload Mode",
            ["Single Resume", "Batch (Multiple Resumes)"]
        )

        if upload_mode == "Single Resume":
            uploaded_file = st.file_uploader(
                "Upload Resume",
                type=["pdf", "docx"]
            )

            if uploaded_file and st.button("▶ Analyze Resume", type="primary"):
                with st.spinner("Extracting text from file..."):
                    resume_text = extract_text(uploaded_file)

                if resume_text:
                    with st.spinner("Analyzing with Claude AI..."):
                        result, error = safe_analyze_resume(resume_text, job_description)

                    if error:
                        st.error(error)
                    else:
                        save_result(result)
                        st.session_state["last_result"] = result
                        st.success(f"✅ Analysis complete for **{result['candidate_name']}**!")
                        st.balloons()

#Section 5 — Batch upload and paste text input.
# ── Batch Upload ──
        elif upload_mode == "Batch (Multiple Resumes)":
            uploaded_files = st.file_uploader(
                "Upload Multiple Resumes",
                type=["pdf", "docx"],
                accept_multiple_files=True
            )

            if uploaded_files and st.button("▶ Analyze All Resumes", type="primary"):
                progress_bar = st.progress(0)
                total = len(uploaded_files)

                for i, file in enumerate(uploaded_files):
                    with st.spinner(f"Analyzing {file.name}... ({i+1}/{total})"):
                        resume_text = extract_text(file)
                        if resume_text:
                            result, error = safe_analyze_resume(resume_text, job_description)
                            if error:
                                st.error(f"❌ {file.name}: {error}")
                            else:
                                save_result(result)
                                st.success(f"✅ {result['candidate_name']} analyzed!")
                    progress_bar.progress((i + 1) / total)

                st.success(f"🎉 Batch analysis complete! {total} resumes analyzed.")
                st.balloons()

    # ── Paste Text ──
    elif input_method == "📝 Paste Text":
        resume_text = st.text_area(
            "📝 Paste Resume Text",
            height=300,
            placeholder="Paste the full resume text here..."
        )

        if resume_text and st.button("▶ Analyze Resume", type="primary"):
            with st.spinner("Analyzing with Claude AI..."):
                result, error = safe_analyze_resume(resume_text, job_description)

            if error:
                st.error(error)
            else:
                save_result(result)
                st.session_state["last_result"] = result
                st.success(f"✅ Analysis complete for **{result['candidate_name']}**!")
                st.balloons()

#Section 6 — The Dashboard page! 
# ── Page 2: Dashboard ─────────────────────────────────────────
elif page == "📊 Dashboard":
    st.title("📊 Candidate Dashboard")
    st.markdown("View, filter and sort all analyzed candidates.")
    st.markdown("---")

    # Load all results
    df = load_results()

    if df.empty:
        st.info("📭 No candidates analyzed yet. Go to the Analyze page to get started!")
    else:
        # ── Filters ──
        col1, col2, col3 = st.columns(3)

        with col1:
            verdict_filter = st.selectbox(
                "Filter by Verdict",
                ["All", "Shortlist", "Maybe", "Reject"]
            )

        with col2:
            min_score = st.number_input("Min Score", 0, 100, 0)

        with col3:
            max_score = st.number_input("Max Score", 0, 100, 100)

        # ── Sort ──
        sort_col1, sort_col2 = st.columns(2)

        with sort_col1:
            sort_by = st.selectbox(
                "Sort By",
                ["overall_score", "candidate_name", "date_analyzed", "experience_level"]
            )

        with sort_col2:
            sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

        # Apply filters and sorting
        df = filter_results(df, verdict_filter, min_score, max_score)
        df = sort_results(df, sort_by, sort_order == "Ascending")

        st.markdown("---")

        # ── Summary Stats ──
        stat1, stat2, stat3, stat4 = st.columns(4)

        with stat1:
            st.metric("Total Candidates", len(df))
        with stat2:
            st.metric("Shortlisted", len(df[df["verdict"] == "Shortlist"]))
        with stat3:
            st.metric("Maybe", len(df[df["verdict"] == "Maybe"]))
        with stat4:
            st.metric("Rejected", len(df[df["verdict"] == "Reject"]))

        st.markdown("---")

#Section 7 — Candidate table and export! 
# ── Candidate Table ──
        st.subheader(f"👥 Candidates ({len(df)})")

        for index, row in df.iterrows():
            with st.expander(f"👤 {row['candidate_name']} — Score: {row['overall_score']} | {row['verdict']}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    score = row["overall_score"]
                    if score >= 75:
                        st.markdown(f"<div class='score-high'>{score}</div>", unsafe_allow_html=True)
                    elif score >= 50:
                        st.markdown(f"<div class='score-mid'>{score}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='score-low'>{score}</div>", unsafe_allow_html=True)
                    st.caption("Overall Score")

                with col2:
                    st.markdown(f"**Experience:** {row['experience_level']}")
                    st.markdown(f"**Date:** {row['date_analyzed']}")

                with col3:
                    verdict = row["verdict"]
                    if verdict == "Shortlist":
                        st.markdown(f"<span class='verdict-shortlist'>✅ {verdict}</span>", unsafe_allow_html=True)
                    elif verdict == "Maybe":
                        st.markdown(f"<span class='verdict-maybe'>🤔 {verdict}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='verdict-reject'>❌ {verdict}</span>", unsafe_allow_html=True)

                st.markdown(f"**Summary:** {row['summary']}")

                # View Detail Button
                if st.button(f"View Full Detail", key=f"view_{index}"):
                    st.session_state["selected_candidate"] = row.to_dict()
                    st.session_state["page"] = "📄 Candidate Detail"
                    st.rerun()

        st.markdown("---")

        # ── Export CSV ──
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Results to CSV",
            data=csv_data,
            file_name="resume_analysis_results.csv",
            mime="text/csv",
            type="primary"
        )

# Section 8 — Candidate Detail page.
# ── Page 3: Candidate Detail ──────────────────────────────────
elif page == "📄 Candidate Detail":
    st.title("📄 Candidate Detail")
    st.markdown("---")

    candidate = st.session_state.get("selected_candidate", None)

    if candidate is None:
        st.info("👈 Please select a candidate from the Dashboard first.")
    else:
        # ── Header ──
        col1, col2, col3 = st.columns(3)

        with col1:
            score = candidate["overall_score"]
            if score >= 75:
                st.markdown(f"<div class='score-high'>{score}</div>", unsafe_allow_html=True)
            elif score >= 50:
                st.markdown(f"<div class='score-mid'>{score}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='score-low'>{score}</div>", unsafe_allow_html=True)
            st.caption("Overall Score")

        with col2:
            st.markdown(f"### {candidate['candidate_name']}")
            st.markdown(f"**Experience:** {candidate['experience_level']}")
            st.markdown(f"**Date Analyzed:** {candidate['date_analyzed']}")

        with col3:
            verdict = candidate["verdict"]
            if verdict == "Shortlist":
                st.markdown(f"<span class='verdict-shortlist'>✅ {verdict}</span>", unsafe_allow_html=True)
            elif verdict == "Maybe":
                st.markdown(f"<span class='verdict-maybe'>🤔 {verdict}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='verdict-reject'>❌ {verdict}</span>", unsafe_allow_html=True)
            st.markdown(f"_{candidate['verdict_reason']}_")

        st.markdown("---")

        # ── Tabs ──
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "🛠️ Skills", "⚠️ Red Flags", "📝 Notes"])

        with tab1:
            st.markdown("#### Overall Summary")
            st.info(candidate["summary"])
            st.markdown("#### Score Reason")
            st.markdown(candidate["score_reason"])

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### ✅ Matched Skills")
                skills = candidate["matched_skills"].split(", ")
                for skill in skills:
                    st.markdown(f"<span class='tag' style='background:#22c55e22;color:#22c55e;border:1px solid #22c55e44'>{skill}</span>", unsafe_allow_html=True)

            with col2:
                st.markdown("#### ❌ Missing Skills")
                missing = candidate["missing_skills"].split(", ")
                for skill in missing:
                    st.markdown(f"<span class='tag' style='background:#ef444422;color:#ef4444;border:1px solid #ef444444'>{skill}</span>", unsafe_allow_html=True)

        with tab3:
            st.markdown("#### ⚠️ Red Flags")
            red_flags = candidate["red_flags"].split(", ")
            if red_flags and red_flags[0]:
                for flag in red_flags:
                    st.warning(f"⚠️ {flag}")
            else:
                st.success("✅ No red flags detected!")

        with tab4:
            st.markdown("#### 📝 Recruiter Notes")
            current_notes = candidate.get("notes", "")
            new_notes = st.text_area("Add your notes here", value=current_notes, height=150)

            if st.button("💾 Save Notes", type="primary"):
                update_notes(candidate["candidate_name"], candidate["date_analyzed"], new_notes)
                st.success("✅ Notes saved successfully!")

        st.markdown("---")

        # ── Delete Candidate ──
        st.markdown("#### ⚠️ Danger Zone")
        st.warning("Deleting a candidate is permanent and cannot be undone.")

        confirm = st.checkbox("I understand this action is permanent and want to delete this candidate")

        if confirm:
            if st.button("🗑️ Delete Candidate", type="primary"):
                delete_candidate(candidate["candidate_name"], candidate["date_analyzed"])
                st.session_state["selected_candidate"] = None
                st.success("✅ Candidate deleted successfully!")
                st.rerun()