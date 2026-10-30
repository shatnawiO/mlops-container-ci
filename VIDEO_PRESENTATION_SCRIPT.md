# AI381 MLOps - Lab 2: Video Recording Script & Submission Walkthrough

This document provides a step-by-step blueprint and word-for-word script to record your **5 to 8-minute submission video** and score **100/100** on the rubric.

---

## 📋 Pre-Flight Checklist Before You Record

- [ ] Video format: MP4, 720p (or 1080p).
- [ ] Terminal font size: **14 pt or larger** (clear and readable).
- [ ] Webcam picture-in-picture showing your face throughout the video.
- [ ] Your own voice (speaking clearly in English or Arabic).
- [ ] Video duration: **Between 5:00 and 8:00 minutes** (do not exceed 8 minutes, do not make it shorter than 5 minutes).
- [ ] Video file naming convention: `StudentID_FirstName_LastName_Lab2.mp4` (no spaces, exactly as in JUST e-learning). Example: `123456789_Ahmad_Alhasan_Lab2.mp4`.

---

## 🎬 Step-by-Step Video Script (Checkpoints 0 - 5)

> **Important Rule:** Always clearly say each checkpoint aloud (e.g., *"Checkpoint 1"*) and keep the result on screen for at least **5 seconds**.

---

### ⏱️ Checkpoint 0: Identity (First 30 Seconds)

**What to show on screen:**
1. Browser open to your JUST e-learning profile: `https://elearn.just.edu.jo` (Click top-right menu → **Profile**).
2. Ensure your **Full Name** and **Student ID** are clearly visible on screen for **at least 5 seconds**.
3. Webcam shows your face.

**What to say (Verbatim Script):**
> *"Hello Dr. Tariq. My name is [Your Full Name], my student ID is [Your Student ID]. Today is [Current Date, e.g., October 30, 2026], and this is my video submission for AI381 Machine Learning Operations - Lab 2: Bring Your Own Model – Container and Continuous Integration."*

**Action in Terminal:**
Open your terminal and run:
```bash
echo "AI381 <StudentID> $(date)"
```
*(On Windows PowerShell, run: `Write-Output "AI381 <StudentID> $(Get-Date)"` or `bash -c 'echo "AI381 <StudentID> $(date)"'`)*

Hold the terminal output on screen for **5 seconds**.

---

### ⏱️ Checkpoint 1: Local Tests Passing & What Each One Protects (~1 Minute)

**What to say:**
> *"Now moving to **Checkpoint 1**: running our test suite locally and explaining the protection provided by each test."*

**Action in Terminal:**
```powershell
.\.venv\Scripts\pytest -v
```

**What to explain while the 11 passed tests are visible on screen:**
> *"As you can see, all 11 test cases have passed. Let me explain what each category protects in production:*
> 1. *`test_api_contract_health` and `test_api_contract_predict`: Protect against breaking API contract changes. They guarantee that `/health` returns HTTP 200 with `model_loaded: true`, and that `/predict` returns the exact schema expected by downstream applications (integers, strings, and probability distributions).*
> 2. *`test_input_schema_validation`: Protects against unhandled server 500 crashes by catching missing payload fields, empty requests, or wrong data types (e.g. string instead of float) at the Pydantic validation layer with HTTP 422.*
> 3. *`test_edge_cases_boundary_constraints`: Protects the ML pipeline from adversarial or nonsensical biological inputs, such as negative dimensions (`-1.0`), zeroes (`0.0`), or impossible biological values (`> 20.0 cm`).*
> 4. *`test_deterministic_prediction_setosa` and `virginica`: Protect against silent model drift, corrupt weights, or broken standard scaling by asserting exact deterministic predictions and high confidence probabilities on canonical benchmark samples.*
> 5. *`test_model_loads_and_has_required_attributes`: Protects against missing or corrupt joblib artifacts on disk, verifying pipeline structure, feature names, and minimum accuracy thresholds."*

Hold the green passing test output on screen for **5 seconds**.

---

### ⏱️ Checkpoint 2: Dockerfile Line-by-Line & Container Live Endpoints (~1.5 Minutes)

**What to say:**
> *"Now for **Checkpoint 2**: our multi-stage, non-root Dockerfile, followed by testing the running container with `/health` and `/predict`."*

**Show `Dockerfile` in your editor and explain line by line:**
> 1. *Line 6: We use a multi-stage build. In Stage 1 (`builder`), we use `python:3.11.9-slim` pinned to an immutable SHA256 digest (`@sha256:8fb099199b9f...`). Pinning the cryptographic hash guarantees 100% reproducible builds and eliminates supply-chain tag mutations.*
> 2. *Line 13: We create an isolated virtual environment at `/opt/venv` and install our dependencies with `--no-cache-dir` to keep the layer small.*
> 3. *Line 23: In Stage 2 (`runtime`), we start from the same clean pinned base image. We copy ONLY the built `/opt/venv` from the builder stage and leave behind all build tools and temporary caches, reducing image size by over 60%.*
> 4. *Line 32: We create a dedicated non-root system user and group `appuser` with UID 1000. Running as an unprivileged user prevents container breakouts and privilege escalation attacks.*
> 5. *Line 42: We copy the source code and serialized model into `/app` and adjust ownership to `appuser`.*
> 6. *Line 48: `USER appuser` drops root privileges before process execution.*
> 7. *Line 52: We define a native `HEALTHCHECK` using Python standard library `urllib.request`. This checks `http://localhost:8000/health` every 30 seconds without requiring `curl` to be installed, preventing added CVE attack surface.*
> 8. *Line 56: The `CMD` executes `uvicorn src.app.main:app` on port 8000."*

**Action in Terminal: Start Container & Test Endpoints:**
```bash
docker compose up -d --build
```

Test `/health`:
```bash
curl -X GET http://localhost:8000/health
```
*(Show JSON output: `{"status": "healthy", "model_loaded": true, "model_type": "LogisticRegression"}`)*

Test `/predict`:
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"sepal_length\": 5.1, \"sepal_width\": 3.5, \"petal_length\": 1.4, \"petal_width\": 0.2}"
```
*(Show prediction output: `{"prediction": 0, "class_name": "setosa", "probabilities": {...}}`)*

Keep results on screen for **5 seconds**.

---

### ⏱️ Checkpoint 3: Pull Request Running CI, Trivy Scan & GHCR Image (~1 Minute)

**What to show on screen:**
1. **GitHub Pull Request Page:**
   - Show your Pull Request (e.g. from branch `feature/container-and-ci` to `main`).
   - Show the required status check `Lint & Pytest Suite` passing with a green checkmark.
2. **GitHub Actions Workflow Execution:**
   - Click on the Actions tab for the commit on `main`.
   - Show the job: `Build, Scan & Push to GHCR`.
   - Expand the **Run Trivy Security Vulnerability Scan** step: show that Trivy scanned the image for critical and high vulnerabilities with zero unfixed vulnerabilities.
   - Point out that every action is pinned to a **full 40-character commit SHA** (`actions/checkout@11bd71...`, `docker/login-action@9780b0...`, `aquasecurity/trivy-action@57a97c...`).
3. **GitHub Packages (GHCR):**
   - Navigate to your repository or user profile → **Packages**.
   - Show the package image tagged with the **commit SHA** and the **image digest**.

**What to say:**
> *"In **Checkpoint 3**, we observe our continuous integration and delivery pipeline. On pull requests, the linting and pytest jobs run automatically to protect the branch. Once merged to main, GitHub Actions builds the image, executes an automated vulnerability scan using Aqua Security Trivy, and pushes the container image to GitHub Container Registry (GHCR) tagged with the exact Git commit SHA. Notice in our workflow that every third-party action is pinned to an immutable 40-character commit SHA to protect against supply-chain attacks."*

Keep the GHCR digest on screen for **5 seconds**.

---

### ⏱️ Checkpoint 4: Branch Protection, README & Green Badge (~45 Seconds)

**What to show on screen:**
1. **GitHub Settings → Branches / Branch Rulesets:**
   - Show that branch protection is active for `main`.
   - Show **Require a pull request before merging** is enabled.
   - Show **Require status checks to pass before merging** with `Lint & Pytest Suite` selected.
2. **Repository README:**
   - Show the green CI badge at the very top of `README.md`.
   - Show the **One-Command Quickstart** section (`docker compose up --build`).

**What to say:**
> *"In **Checkpoint 4**, we review branch hygiene and documentation. In the repository settings, branch protection is enforced on `main`. Direct pushes are disabled, requiring pull requests and requiring the `Lint & Pytest Suite` status check to pass before merging. Looking at our README, we have a green passing CI badge at the top and a one-command quickstart so anyone can reproduce and run the service instantly."*

Keep the green badge and branch protection on screen for **5 seconds**.

---

### ⏱️ Checkpoint 5: Reflection - Trade-offs, What Broke & What Was Learned (~1.5 Minutes)

*(Rubric Criterion: Explains why + trade-offs + failure cases for maximum 20/20 points)*

**What to say:**
> *"Finally, **Checkpoint 5: Reflection and Technical Trade-offs**:*
> 1. *Trade-off 1: Pinning Action SHAs vs Automatic Updates. Pinning third-party GitHub Actions to 40-character commit SHAs sacrifices automatic minor version updates, meaning we must deliberately manage bumps. However, the trade-off is critical: as seen in the March 2026 supply chain incident with mutable Trivy tags, attackers can hijack tags. SHA pinning provides cryptographic immutability and complete supply-chain security.*
> 2. *Trade-off 2: Python Urllib Healthcheck vs Curl. While installing `curl` makes Dockerfile commands slightly shorter, adding curl to a slim Debian image pulls in additional networking libraries and increases CVE exposure. By implementing the healthcheck using Python's built-in `urllib.request`, we keep the attack surface minimal and keep Trivy scans clean.*
> 3. *What Broke / Failure Case 1: GitHub Container Registry Lowercase Requirement. In Docker and GHCR, repository names must be strictly lowercase. If a user's GitHub username contains uppercase letters, a standard push using `${{ github.repository }}` immediately fails with `invalid reference format`. We solved this by adding an environment step `echo "IMAGE_NAME=ghcr.io/${GITHUB_REPOSITORY,,}"` to normalize all characters before buildx pushes.*
> 4. *What Broke / Failure Case 2: Pytest Module Discovery. When running `pytest` directly in automated CI environments without installing the project as an editable package, imports like `from src.app.main import app` can cause `ModuleNotFoundError`. We fixed this cleanly by introducing `pytest.ini` with `pythonpath = .`, ensuring both local development and remote GitHub Action runners resolve imports identically.*
>
> *Thank you Dr. Tariq for listening to my presentation!"*

Hold terminal or face on screen for the final 5 seconds and conclude the video.

---

## 📤 Submission Steps on Microsoft Teams

1. Make sure your video is between **5 and 8 minutes**.
2. Rename video to: `StudentID_FirstName_LastName_Lab2.mp4`
3. Go to **Microsoft Teams** → **AI381 MLOPs** team.
4. Open **Assignments** → **Lab 2**.
5. Click **Add work** → Upload your `.mp4` video.
6. In **Add work** / comments, paste your **GitHub Repository URL**.
7. Click **Turn in**!
