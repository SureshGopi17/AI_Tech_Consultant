// Task 1 Knowledge Brain UI Client

const API_BASE = window.location.origin;

document.addEventListener("DOMContentLoaded", () => {
  fetchHealth();
  fetchEscalations();
  setupTabs();
  setupChat();
  setupSync();
});

async function fetchHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`);
    const data = await res.json();
    document.getElementById("stat-articles").innerText = data.total_articles;
    document.getElementById("stat-images").innerText = data.total_images;
  } catch (err) {
    console.error("Health check failed:", err);
  }
}

function setupTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      document.getElementById(targetId).classList.add("active");

      if (targetId === "tab-escalations") fetchEscalations();
      if (targetId === "tab-articles") fetchArticles();
    });
  });
}

function setupChat() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (text) {
      askQuestion(text);
      input.value = "";
    }
  });
}

async function askQuestion(questionText) {
  appendMessage("user", questionText);
  const sendBtn = document.getElementById("send-btn");
  sendBtn.disabled = true;
  sendBtn.innerText = "Thinking...";

  try {
    const res = await fetch(`${API_BASE}/api/v1/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: questionText })
    });
    const data = await res.json();

    appendMessage("bot", data.answer, data.can_answer, data.escalation_id);
    renderEvidence(data);

    if (data.escalation_id) {
      fetchEscalations();
    }
  } catch (err) {
    appendMessage("bot", "Network error communicating with the Knowledge Brain server.");
  } finally {
    sendBtn.disabled = false;
    sendBtn.innerText = "Ask";
  }
}

function appendMessage(sender, text, canAnswer = true, escId = null) {
  const history = document.getElementById("chat-history");
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}-message`;

  const author = document.createElement("div");
  author.className = "msg-author";
  author.innerText = sender === "user" ? "You" : "Knowledge Brain";

  const body = document.createElement("div");
  body.className = "msg-body";
  body.innerText = text;

  msgDiv.appendChild(author);
  msgDiv.appendChild(body);
  history.appendChild(msgDiv);
  history.scrollTop = history.scrollHeight;
}

function renderEvidence(data) {
  const confBox = document.getElementById("confidence-banner");
  const confVal = document.getElementById("conf-val");
  const confBar = document.getElementById("conf-bar");
  const citationsList = document.getElementById("citations-list");
  const screenshotsList = document.getElementById("screenshots-list");

  confBox.style.display = "block";
  const pct = Math.round(data.confidence * 100);
  confVal.innerText = `${pct}%`;
  confBar.style.width = `${pct}%`;
  confBar.style.backgroundColor = data.can_answer ? "#10b981" : "#f43f5e";

  // Render citations
  if (data.citations && data.citations.length > 0) {
    citationsList.innerHTML = data.citations.map(c => `
      <div class="citation-card">
        <div>
          <a href="${c.url}" target="_blank" class="cit-title">${c.title}</a>
          <span class="cit-badge">${c.category}</span>
        </div>
        <p class="cit-snippet">${c.snippet}</p>
      </div>
    `).join("");
  } else {
    citationsList.innerHTML = `<p class="empty-state">No matching citations found.</p>`;
  }

  // Render screenshots
  if (data.screenshots && data.screenshots.length > 0) {
    screenshotsList.innerHTML = data.screenshots.map(img => `
      <div class="screenshot-card">
        <div style="background: #1e293b; padding: 1rem; text-align: center; border-radius: 4px; color: #94a3b8; font-family: monospace; font-size: 0.75rem;">
          📷 [Screenshot: ${img.alt_text || img.caption}]<br/>
          <span style="font-size: 0.65rem; color: #64748b;">${img.url}</span>
        </div>
        <div class="screenshot-caption"><strong>Context:</strong> ${img.caption}</div>
      </div>
    `).join("");
  } else {
    screenshotsList.innerHTML = `<p class="empty-state">No screenshots applicable for this query.</p>`;
  }
}

async function fetchEscalations() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/escalations?status=PENDING`);
    const escalations = await res.json();
    document.getElementById("esc-count").innerText = escalations.length;

    const container = document.getElementById("escalations-list");
    if (!escalations.length) {
      container.innerHTML = `<p class="empty-state">No pending escalations. All queries answered or resolved!</p>`;
      return;
    }

    container.innerHTML = escalations.map(esc => `
      <div class="esc-card" id="esc-card-${esc.id}">
        <div class="esc-header">
          <span>TASK ${esc.id}</span>
          <span>Confidence: ${Math.round(esc.confidence * 100)}%</span>
        </div>
        <div class="esc-q">${esc.question}</div>
        <form class="esc-form" onsubmit="submitEscalation(event, '${esc.id}')">
          <textarea id="esc-ans-${esc.id}" placeholder="Type verified technical solution to flow into Knowledge Brain memory..." required></textarea>
          <button type="submit" class="btn btn-primary" style="font-size: 0.75rem; padding: 0.35rem 0.75rem;">Submit Expert Answer</button>
        </form>
      </div>
    `).join("");
  } catch (err) {
    console.error("Failed to fetch escalations:", err);
  }
}

async function submitEscalation(e, escId) {
  e.preventDefault();
  const textarea = document.getElementById(`esc-ans-${escId}`);
  const answer = textarea.value.trim();
  if (!answer) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/escalations/${escId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expert_answer: answer, resolved_by: "Lead Solutions Architect" })
    });
    if (res.ok) {
      alert(`Success! Escalation ${escId} resolved. Verified answer saved to Knowledge Brain memory.`);
      fetchEscalations();
      fetchHealth();
    }
  } catch (err) {
    alert("Failed to submit escalation answer.");
  }
}

async function fetchArticles() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/articles?limit=30`);
    const articles = await res.json();
    const container = document.getElementById("articles-list");
    container.innerHTML = articles.map(a => `
      <div class="art-row">
        <div class="art-info">
          <h4>${a.title}</h4>
          <span>${a.category} &bull; ${a.folder} &bull; ${a.images.length} screenshots</span>
        </div>
        <a href="${a.url}" target="_blank" class="btn btn-secondary" style="font-size: 0.7rem; padding: 0.25rem 0.5rem;">View URL</a>
      </div>
    `).join("");
  } catch (err) {
    console.error("Failed to load articles:", err);
  }
}

function setupSync() {
  const btn = document.getElementById("btn-sync");
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.innerText = "Syncing...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/sync?max_scrapes=5`, { method: "POST" });
      const data = await res.json();
      alert(`Differential Sync Complete!\nTotal Articles: ${data.total_articles}\nNew Added: ${data.added_count}\nUpdated: ${data.updated_count}\nRemoved: ${data.removed_count}`);
      fetchHealth();
    } catch (err) {
      alert("Sync failed to complete.");
    } finally {
      btn.disabled = false;
      btn.innerText = "⚡ Run Daily Sync";
    }
  });
}
