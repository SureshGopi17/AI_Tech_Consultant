# AI_LOG.md — AI Pairing Insights & Prompt Engineering Log

**Tool Used:** Antigravity / Claude  
**Project:** AI Tech Consultant Monorepo  

---

## The 5 Most Useful Prompts

### Prompt 1: Strict Decoupling via Clean API (Architecture Design)
> *"We are building three tasks where Task 1 is the Knowledge Brain, Task 2 is a TypeScript Inbox Agent, and Task 3 is a Python Multi-Agent SOW pipeline. Define strict API boundaries so Tasks 2 and 3 call Task 1 exclusively through HTTP REST endpoints. Tasks 2 and 3 must never import or copy Task 1 code. Generate typed request/response schemas for `/api/v1/search`."*
- **Why it worked:** It prevented code duplication and forced clean microservice boundaries from Day 1, ensuring zero cross-language dependency leakage.

### Prompt 2: Polite Sitemap Crawler with Resumable Checkpoints (Task 1)
> *"Write a polite Python crawler for `support.brilliantdirectories.com/support/sitemap.xml`. Add a 0.5s rate-limit delay, batching of 10 pages, exponential backoff on HTTP 429, and an atomic checkpoint file (`scraper_checkpoint.json`) that records completed URLs so the crawl can be interrupted and resumed without refetching."*
- **Why it worked:** Prevented IP bans against the public help center while guaranteeing scraper fault-tolerance if network drops halfway.

### Prompt 3: Levenshtein Self-Improving Feedback Loop with Undo (Task 2)
> *"Build a TypeScript feedback store that computes the exact Levenshtein edit distance and similarity ratio between an AI-generated draft and the final human-edited email. When an edit occurs, extract the stylistic or policy difference as a reusable rule and increment the prompt version. Provide a rollback function `undoFeedback(id)` that deactivates the rule and reverts the prompt version."*
- **Why it worked:** Satisfied the requirement to prove the agent gets better with measurable numbers (edit distance reduction) and provided full undo safety.

### Prompt 4: 20-Streak Autonomous Graduation & Demotion Engine (Task 2)
> *"Implement an autonomous graduation state machine for customer email categories. Define 'the same kind' as the email intent cluster, and 'without changing' as Levenshtein similarity &ge; 95%. When a category reaches 20 consecutive unchanged sends, unlock `AUTO_SEND_ELIGIBLE`. If any subsequent human edit or complaint occurs, reset the streak to 0 and immediately demote back to `HUMAN_REVIEW_REQUIRED`."*
- **Why it worked:** Turned an ambiguous brief requirement into mathematical, testable business logic with clear safety demotion guardrails.

### Prompt 5: Scope Creep Delta Engine with Change Order Quoting (Task 3)
> *"Build a semantic diff engine that compares Meeting 1 (initial discovery) with Meeting 2 (follow-up pivot). Classify items into MODIFIED, DROPPED, and SCOPE_CREEP. For scope creep items (like Native Mobile Apps and QuickBooks Sync), do not fold them into the Phase 1 web scope. Instead, itemize them into an Add-On Change Order quote with hours and cost at \$95/hr so Phase 1 web launch is not delayed."*
- **Why it worked:** Solved the primary problem tech agencies face: scope creep eroding profit margins.

---

## One Time I Rejected the AI's Answer and Why

### The Incident
During the design of the Solution Architect Agent in Task 3, the AI proposed running a heavy local PyTorch sentence-transformer (`all-MiniLM-L6-v2`) inside Task 3 to calculate embeddings locally for matching meeting requirements against Brilliant Directories features.

### Why I Rejected It
1. **Broken Architectural Boundary:** Having Task 3 compute embeddings locally duplicated knowledge base responsibilities and violated the core rule: *"Tasks 2 and 3 must call Task 1 through its API, not copy its code."*
2. **Environment Bloat:** Downloading a 2 GB PyTorch binary would bloat the repo, slow down container builds, and cause installation failures on student machines with different CUDA/Python versions.
3. **Speed & Efficiency:** Task 1's `/api/v1/search` endpoint already computes hybrid BM25 + dense semantic similarity in **12 ms**. Calling Task 1 over HTTP took less than 15 ms total, maintained single-source-of-truth knowledge, and required zero additional dependencies in Task 3.

### What Was Built Instead
I rejected the local embedding model and enforced that Task 3 must call Task 1's `POST /api/v1/search` endpoint via HTTP with connection caching. This cut test suite runtime from 35 seconds to **0.88 seconds**, preserved clean decoupling, and ensured the monorepo runs effortlessly out-of-the-box.
