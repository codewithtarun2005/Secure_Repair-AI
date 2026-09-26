import streamlit as st
import tempfile
import subprocess
import os
import shutil
import zipfile

from scanner import scan_repository
from repair_agent import repair_code


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SecureRepair AI",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827, #1e293b);
    border: 1px solid #334155;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    color: #94a3b8;
    font-size: 18px;
}

.finding-box {
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #334155;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<h1>🛡️ SecureRepair AI</h1>

<p>
AI-Powered Code Vulnerability Detection & Auto-Repair Agent
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "scan_results" not in st.session_state:
    st.session_state.scan_results = None

if "repo_path" not in st.session_state:
    st.session_state.repo_path = None

if "workspace" not in st.session_state:
    st.session_state.workspace = None

if "repair_results" not in st.session_state:
    st.session_state.repair_results = {}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Scan Configuration")

    analysis_type = st.selectbox(
        "Analysis Type",
        [
            "Full Security Scan",
            "Vulnerability Detection",
            "Code Quality Analysis"
        ]
    )

    st.divider()

    st.write("### 🤖 Agent Pipeline")

    st.write("🔍 Repository Scanner")
    st.write("🌳 AST Analyzer")
    st.write("🛡️ Security Agent")
    st.write("🤖 Repair Agent")
    st.write("🐳 Sandbox Verification")
    st.write("🧪 Test Validation")


# ============================================================
# REPOSITORY INPUT
# ============================================================

st.subheader("📦 Repository Input")

input_type = st.radio(
    "Choose repository source",
    [
        "GitHub Repository",
        "Upload ZIP"
    ],
    horizontal=True
)


github_url = None
uploaded_file = None


if input_type == "GitHub Repository":

    github_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository"
    )

else:

    uploaded_file = st.file_uploader(
        "Upload source-code ZIP",
        type=["zip"]
    )


# ============================================================
# START SCAN
# ============================================================

st.divider()

start_scan = st.button(
    "🔍 START SECURITY SCAN",
    type="primary",
    use_container_width=True
)


# ============================================================
# SCANNING
# ============================================================

if start_scan:

    if input_type == "GitHub Repository" and not github_url:

        st.error(
            "❌ Please enter a GitHub repository URL."
        )

        st.stop()


    if input_type == "Upload ZIP" and not uploaded_file:

        st.error(
            "❌ Please upload a ZIP file."
        )

        st.stop()


    # Create temporary workspace

    workspace = tempfile.mkdtemp()

    st.session_state.workspace = workspace

    try:

        # ====================================================
        # GITHUB REPOSITORY
        # ====================================================

        if input_type == "GitHub Repository":

            st.info(
                "📥 Cloning GitHub repository..."
            )

            repo_path = os.path.join(
                workspace,
                "repository"
            )

            clone_result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    github_url,
                    repo_path
                ],
                capture_output=True,
                text=True
            )


            if clone_result.returncode != 0:

                st.error(
                    "❌ Repository clone failed."
                )

                st.code(
                    clone_result.stderr
                )

                st.stop()


        # ====================================================
        # ZIP REPOSITORY
        # ====================================================

        else:

            st.info(
                "📦 Extracting ZIP..."
            )

            repo_path = os.path.join(
                workspace,
                "repository"
            )

            os.makedirs(
                repo_path,
                exist_ok=True
            )

            zip_path = os.path.join(
                workspace,
                "repository.zip"
            )

            with open(
                zip_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )


            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_ref:

                zip_ref.extractall(
                    repo_path
                )


        st.session_state.repo_path = repo_path


        # ====================================================
        # AST SCAN
        # ====================================================

        st.info(
            "🌳 Running AST security analysis..."
        )

        files_scanned, findings = scan_repository(
            repo_path
        )


        # Store results

        st.session_state.scan_results = (
            files_scanned,
            findings
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            "✅ Repository scanned successfully!"
        )


    except Exception as e:

        st.error(
            f"❌ Scan error: {e}"
        )


# ============================================================
# SHOW RESULTS
# ============================================================

if st.session_state.scan_results:

    files_scanned, findings = (
        st.session_state.scan_results
    )


    # ========================================================
    # SECURITY OVERVIEW
    # ========================================================

    st.subheader(
        "📊 Security Overview"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Files Scanned",
            files_scanned
        )


    with col2:

        st.metric(
            "Vulnerabilities",
            len(findings)
        )


    with col3:

        high_count = sum(
            1
            for finding in findings
            if finding["severity"] == "HIGH"
        )

        st.metric(
            "High Severity",
            high_count
        )


    st.divider()


    # ========================================================
    # FINDINGS
    # ========================================================

    st.subheader(
        "🛡️ Security Findings"
    )


    if not findings:

        st.success(
            "🎉 No vulnerabilities detected "
            "by the current security rules."
        )


    # ========================================================
    # EACH FINDING
    # ========================================================

    for index, finding in enumerate(findings):

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [1, 4, 1]
            )


            # ----------------------------------------------
            # SEVERITY
            # ----------------------------------------------

            with col1:

                st.write(
                    f"**{finding['severity']}**"
                )


            # ----------------------------------------------
            # VULNERABILITY
            # ----------------------------------------------

            with col2:

                st.markdown(
                    f"### {finding['title']}"
                )

                st.code(
                    f"{finding['file']} "
                    f"→ Line {finding['line']}"
                )

                st.write(
                    finding["description"]
                )


            # ----------------------------------------------
            # CWE
            # ----------------------------------------------

            with col3:

                st.write(
                    f"**{finding['cwe']}**"
                )


            # =================================================
            # AUTO REPAIR BUTTON
            # =================================================

            repair_key = (
                f"{finding['file']}_"
                f"{finding['line']}_"
                f"{index}"
            )


            if st.button(
                "🤖 AUTO REPAIR",
                key=repair_key,
                use_container_width=True
            ):

                repo_path = (
                    st.session_state.repo_path
                )


                if not repo_path:

                    st.error(
                        "❌ Repository path not available."
                    )

                    st.stop()


                # ------------------------------------------
                # FIND FILE
                # ------------------------------------------

                file_path = os.path.join(
                    repo_path,
                    finding["file"]
                )


                if not os.path.exists(file_path):

                    st.error(
                        "❌ Vulnerable file could not be found."
                    )

                    st.stop()


                # ------------------------------------------
                # READ SOURCE
                # ------------------------------------------

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as f:

                        source_code = f.read()


                except Exception as e:

                    st.error(
                        f"❌ Could not read file: {e}"
                    )

                    st.stop()


                # ------------------------------------------
                # GEMINI REPAIR AGENT
                # ------------------------------------------

                with st.spinner(
                    "🤖 Repair Agent is analyzing the vulnerability..."
                ):

                    repair_result = repair_code(
                        code=source_code,
                        vulnerability=finding["title"],
                        cwe=finding["cwe"],
                        line=finding["line"]
                    )


                # ------------------------------------------
                # SAVE RESULT
                # ------------------------------------------

                st.session_state.repair_results[
                    repair_key
                ] = {
                    "original": source_code,
                    "result": repair_result,
                    "finding": finding
                }


    # ========================================================
    # DISPLAY REPAIR RESULTS
    # ========================================================

    if st.session_state.repair_results:

        st.divider()

        st.subheader(
            "🤖 AI Auto-Repair Results"
        )


        for key, repair_data in (
            st.session_state.repair_results.items()
        ):

            finding = repair_data["finding"]
            original = repair_data["original"]
            result = repair_data["result"]


            st.markdown(
                f"### 🔧 {finding['title']}"
            )


            if result.get("success"):

                st.success(
                    "✅ AI Repair Generated Successfully"
                )


                # ------------------------------------------
                # BEFORE
                # ------------------------------------------

                st.write(
                    "### 🔴 Before — Vulnerable Code"
                )

                st.code(
                    original,
                    language="python"
                )


                # ------------------------------------------
                # AFTER
                # ------------------------------------------

                st.write(
                    "### 🟢 After — AI Generated Repair"
                )

                st.code(
                    result["code"],
                    language="python"
                )


                # ------------------------------------------
                # NEXT STAGE
                # ------------------------------------------

                st.info(
                    "🐳 Next step: send this generated "
                    "patch to the Docker Sandbox for "
                    "syntax and test verification."
                )


            else:

                st.error(
                    "❌ AI Repair Failed"
                )

                st.code(
                    result.get(
                        "error",
                        "Unknown repair error"
                    )
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "SecureRepair AI — Autonomous Code Security & Auto-Repair System"
)