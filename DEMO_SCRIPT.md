# DEMO_SCRIPT.md — 10-Minute Video Presentation Guide

**Target Video Duration:** 10 Minutes Max  
**Audience:** Evaluators at BusinessLabs / Anthropic Applied AI  
**Structure:** 30s Face Intro &rarr; Architecture &rarr; Task 1 &rarr; Task 2 &rarr; Task 3 &rarr; Failure Case &rarr; Live Evals  

---

## Video Timeline Breakdown

### 0:00 – 0:30 | Face on Camera: Introduction & The Core Problem
- **Visual:** Your face full screen on webcam.
- **Script:**
  > *"Hi everyone, I'm presenting the Capstone Project: the AI Tech Consultant. Two years ago, building a custom directory cost \$2,000. Today, clients use Cursor and Claude for \$200—a 90% drop in price. To survive and thrive, tech companies must handle 10 to 20 times more work. Writing code is fast now; the real bottlenecks are product knowledge, customer inbox turnaround, and scope creep in client meetings. Today, I'm going to demonstrate one unified system that solves all three, running with one command across Python and TypeScript."*

---

### 0:30 – 1:30 | Unified Control Portal & Architecture
- **Visual:** Screen share of Master Portal at `http://localhost:8000`.
- **Key Points:**
  - Show the architecture diagram: Task 1 (Knowledge Brain in Python), Task 2 (Inbox Agent in TypeScript), Task 3 (Meeting SOW in Python).
  - Emphasize clean API decoupling: Tasks 2 and 3 call Task 1's REST API `/api/v1/search`; no shared code.
  - Show that all three services and the portal spin up with a single command: `python run_all.py` (or `run.bat`).

---

### 1:30 – 3:30 | Task 1: The Knowledge Brain in Action
- **Visual:** Navigate to `http://localhost:8001`.
- **Demonstration:**
  1. **Polite Crawling & Sitemap Sync:** Show the sitemap sync dashboard tracking 1,500+ articles and screenshots with polite rate limits and resumable checkpoints.
  2. **Ask a Factual Question:** Type *"How do I set up Stripe for automatic recurring member renewals?"*
     - Show the response citing exact settings: `Settings > General Settings > Payments`.
     - Highlight the **Verified Citations** and **Multimodal Screenshot Viewer** displaying the exact admin UI inputs.
  3. **Purge Test:** Explain that when an article is deleted from the sitemap, it is purged immediately and never appears in search answers.

---

### 3:30 – 5:30 | Task 2: The Inbox Agent & Self-Improving Learning Loop
- **Visual:** Navigate to `http://localhost:8002`.
- **Demonstration:**
  1. **50 Real Customer Emails:** Browse the inbox across the 6 categories (how-to, new project, refund, complaint, quote, follow-up).
  2. **Knowledge Brain Integration:** Open Email `EM-001` (Stripe setup inquiry). Show the AI draft quoting verified facts from Task 1's API.
  3. **1-Click Send:** Click *"Approve & Send (1-Click)"*. Show the streak counter incrementing towards 20.
  4. **Self-Improving Learning Loop:** Select a refund email (`EM-026`). Edit the draft to add custom company wording: *"Refunds typically reflect within 3 to 5 business days. Direct line: +1-800-555-0199."*
     - Click *"Edit & Send"*.
     - Show the system measuring Levenshtein edit distance, extracting the new rule into the **Learned Rules** tab, and incrementing the prompt version to `v2.0`!
     - Show the **Undo Rule** button that rolls back the prompt.
  5. **Autonomous Graduation & Demotion:**
     - Click *"Simulate 20"* on How-To category: show the badge turn green: `🎓 AUTO-SEND ELIGIBLE`.
     - Edit a draft in that category with significant changes (&lt; 95% similarity): show the immediate **Demotion** back to `🛡️ HUMAN REVIEW REQUIRED`.

---

### 5:30 – 7:30 | Task 3: Meeting to Scope of Work & Scope Creep Engine
- **Visual:** Navigate to `http://localhost:8003`.
- **Demonstration:**
  1. **Meeting 1 Discovery Analysis:** Select `Meeting 1 (LegalMatch Pro)`. Click *"🚀 Run Multi-Agent Analysis"*.
     - Watch the 4 agents execute: Consultant &rarr; Solution Architect &rarr; Estimator &rarr; Proposal Writer.
  2. **Native Feature Detection via KB API:**
     - Show the green banner: **\$7,125.00 Saved via Native Features**!
     - Show how Stripe recurring billing, location search, and auto-lead routing were identified as native 0-code settings in Brilliant Directories.
  3. **Developer Task Breakdown & Client Proposal:** Show modular tasks, 15% QA buffer, 10% PM buffer, and total investment at \$95/hr.
  4. **Human Consultant Gatekeeper:** Show the proposal is locked with `Approved: False` until you click *"Approve & Sign-off Proposal"*.
  5. **Scope Creep & Delta Analysis:**
     - Toggle on `Meeting 2 (Follow-up Changes & Creep)`.
     - Open the **Scope Creep Delta** tab:
       - Show **Modified**: Reactive slider (+19 hrs).
       - Show **Dropped**: Automated Bar Verification (-10 hrs).
       - Show **Scope Creep**: Native iOS & Android Apps (90 hrs) and QuickBooks Sync (20 hrs).
       - Highlight the separate **Add-On Change Order Quote: \$10,450.00 (110 hrs)** so Phase 1 web launch stays on schedule!

---

### 7:30 – 8:45 | The Failure Case & Recovery (Rubric Requirement)
- **Visual:** Return to Task 1 Knowledge Brain (`http://localhost:8001`).
- **Demonstration:**
  1. **The Failure:** Ask an unanswerable or out-of-domain question: *"How do we integrate biometric iris scanning into lawyer member checkins?"*
  2. **Honest Rejection:** The bot does not hallucinate. It responds: *"I do not have sufficient information in the documentation to answer accurately."*
  3. **Automatic Escalation:** Show the system automatically logged task `ESC-XXXXXX` into the **Human-in-the-Loop Escalation Queue**.
  4. **The Recovery (Memory Feedback):**
     - Switch to the Escalation Queue tab.
     - Type the verified solution: *"Iris scanning can be integrated by linking an external WebAuthn FIDO2 biometric endpoint to the BD Custom Header widget."*
     - Click *"Submit Expert Answer"*.
     - Re-ask the exact same question in the chatbot: **it now answers immediately with 98% confidence!**

---

### 8:45 – 10:00 | Live Automated Evals & Wrap-Up
- **Visual:** Terminal running `python run_evals.py`.
- **Key Points:**
  - Show all **69 automated test cases passing with 100% success rate in 4.17 seconds**:
    - Task 1: 22 passed
    - Task 2: 25 passed
    - Task 3: 22 passed
  - Review model economics: Claude 3.5 Sonnet for deep technical accuracy at ₹0.40/answer, Claude 3 Haiku for high-speed classification, and offline fallback for zero-failure reliability.
  - Conclude: *"This is how a software agency can do 10 to 20 times more work with the same team. Thank you!"*
