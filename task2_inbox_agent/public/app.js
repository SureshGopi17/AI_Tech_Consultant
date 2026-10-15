// Task 2 Inbox Agent Web Client

const API_BASE = window.location.origin;
let emails = [];
let selectedEmailId = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchEmails();
  fetchGraduation();
  fetchFeedback();
  setupFilterHandlers();
  setupActionHandlers();
});

async function fetchEmails() {
  const catFilter = document.getElementById("filter-category").value;
  const statusFilter = document.getElementById("filter-status").value;

  let url = `${API_BASE}/api/v1/emails?`;
  if (catFilter) url += `category=${catFilter}&`;
  if (statusFilter) url += `status=${statusFilter}&`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    emails = data.emails;
    document.getElementById("total-emails").innerText = emails.length;
    renderEmailList();

    if (!selectedEmailId && emails.length > 0) {
      selectEmail(emails[0].id);
    }
  } catch (err) {
    console.error("Failed to load emails:", err);
  }
}

function renderEmailList() {
  const container = document.getElementById("email-list");
  if (emails.length === 0) {
    container.innerHTML = `<p style="padding: 1rem; color: #64748b; font-size: 0.8rem;">No emails matching filter.</p>`;
    return;
  }

  container.innerHTML = emails.map(e => `
    <div class="email-card ${e.id === selectedEmailId ? 'selected' : ''}" onclick="selectEmail('${e.id}')">
      <div class="card-top">
        <span class="email-author">${escapeHtml(e.customer_name)}</span>
        <span style="font-size: 0.65rem; color: #94a3b8;">${formatDate(e.date)}</span>
      </div>
      <div class="email-card-subject">${escapeHtml(e.subject)}</div>
      <div class="card-bottom">
        <span class="badge badge-${e.category}">${formatCategory(e.category)}</span>
        <span class="status-tag status-${e.status}">${formatStatus(e.status)}</span>
      </div>
    </div>
  `).join("");
}

async function selectEmail(id) {
  selectedEmailId = id;
  renderEmailList();

  const email = emails.find(e => e.id === id);
  if (!email) return;

  document.getElementById("empty-detail-state").style.display = "none";
  document.getElementById("detail-content").style.display = "flex";

  document.getElementById("email-subject").innerText = email.subject;
  document.getElementById("email-from").innerText = email.customer_name;
  document.getElementById("email-sender").innerText = email.customer_email;
  document.getElementById("email-company").innerText = email.company_name;
  document.getElementById("email-urgency").innerText = email.urgency.toUpperCase();
  document.getElementById("email-body").innerText = email.body;

  const catBadge = document.getElementById("email-category-badge");
  catBadge.className = `badge badge-${email.category}`;
  catBadge.innerText = formatCategory(email.category);

  // If already drafted, show it; otherwise request draft from server
  const textarea = document.getElementById("draft-textarea");
  const confTag = document.getElementById("draft-conf-tag");
  const citationsDiv = document.getElementById("draft-citations");

  if (email.drafted_reply) {
    textarea.value = email.drafted_reply;
    confTag.innerText = `Confidence: ${Math.round((email.confidence || 0.9) * 100)}%`;
    renderCitations(citationsDiv, email.citations || []);
  } else {
    textarea.value = "Consulting Knowledge Brain and drafting in company voice...";
    confTag.innerText = "Drafting...";
    citationsDiv.innerHTML = "";

    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${id}/draft`, { method: "POST" });
      const data = await res.json();
      email.drafted_reply = data.email.drafted_reply;
      email.confidence = data.email.confidence;
      email.citations = data.email.citations;
      email.status = "drafted";

      textarea.value = email.drafted_reply;
      confTag.innerText = `Confidence: ${Math.round(email.confidence * 100)}%`;
      renderCitations(citationsDiv, email.citations);
      renderEmailList();
    } catch (err) {
      textarea.value = "Failed to draft reply.";
    }
  }
}

function renderCitations(container, citations) {
  if (!citations || citations.length === 0) {
    container.innerHTML = `<span style="color: #64748b;">No specific Knowledge Brain citation. Drafted using consultant standard practice.</span>`;
    return;
  }

  container.innerHTML = `<strong>Knowledge Brain Citations:</strong><br/>` + citations.map(c => `
    • <a href="${c.url}" target="_blank" style="color: #93c5fd; text-decoration: underline;">${escapeHtml(c.title)}</a>
    <span style="color: #94a3b8;">(${c.category})</span>
  `).join("<br/>");
}

function setupFilterHandlers() {
  document.getElementById("filter-category").addEventListener("change", fetchEmails);
  document.getElementById("filter-status").addEventListener("change", fetchEmails);
}

function setupActionHandlers() {
  // Approve as-is
  document.getElementById("btn-approve").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/approve`, { method: "POST" });
      const data = await res.json();
      alert(`Success! Email sent to customer without edits. (Graduation streak: ${data.graduation_state.consecutive_unchanged}/20)`);
      fetchEmails();
      fetchGraduation();
    } catch (err) {
      alert("Approval failed.");
    }
  });

  // Edit and Send
  document.getElementById("btn-edit-send").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    const edited = document.getElementById("draft-textarea").value.trim();
    if (!edited) return;

    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ edited_reply: edited })
      });
      const data = await res.json();
      alert(`Email sent! Feedback recorded (Edit distance: ${data.feedback.edit_distance} chars). Agent learned rule: "${data.feedback.learned_rule}"`);
      fetchEmails();
      fetchGraduation();
      fetchFeedback();
    } catch (err) {
      alert("Failed to send edited email.");
    }
  });

  // Custom Reply
  document.getElementById("btn-custom-reply").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    const custom = prompt("Enter your custom reply to send to the client:");
    if (!custom) return;

    try {
      await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/custom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ custom_reply: custom })
      });
      alert("Custom reply sent and saved to learning store.");
      fetchEmails();
      fetchGraduation();
      fetchFeedback();
    } catch (err) {
      alert("Failed to send custom reply.");
    }
  });

  // Regenerate Draft
  document.getElementById("btn-redraft").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    const email = emails.find(e => e.id === selectedEmailId);
    if (email) {
      email.drafted_reply = undefined;
      selectEmail(selectedEmailId);
    }
  });

  // Batch Auto-Process
  document.getElementById("btn-batch-process").addEventListener("click", async () => {
    const btn = document.getElementById("btn-batch-process");
    btn.disabled = true;
    btn.innerText = "Processing...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/auto-process`, { method: "POST" });
      const data = await res.json();
      alert(`Auto-Process Batch Completed!\nAuto-Sent: ${data.auto_sent_count}\nDrafted for Review: ${data.drafted_count}`);
      fetchEmails();
      fetchGraduation();
    } catch (err) {
      alert("Batch processing failed.");
    } finally {
      btn.disabled = false;
      btn.innerText = "⚡ Auto-Process Batch";
    }
  });
}

async function fetchGraduation() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/graduation`);
    const data = await res.json();
    const container = document.getElementById("graduation-list");

    container.innerHTML = data.states.map(s => {
      const pct = Math.min(100, Math.round((s.consecutive_unchanged / s.threshold) * 100));
      const isEligible = s.auto_send_eligible;
      return `
        <div class="grad-row">
          <div class="grad-top">
            <span class="name">${escapeHtml(s.category_label)}</span>
            <span class="streak">${s.consecutive_unchanged}/${s.threshold}</span>
          </div>
          <div class="grad-progress-bar">
            <div class="grad-progress-fill" style="width: ${pct}%; background-color: ${isEligible ? '#10b981' : '#3b82f6'};"></div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="grad-status-badge ${isEligible ? 'grad-eligible' : 'grad-review'}">
              ${isEligible ? '🎓 AUTO-SEND ELIGIBLE' : '🛡️ HUMAN REVIEW REQUIRED'}
            </span>
            <button onclick="simulateStreak('${s.category}')" class="btn btn-secondary btn-sm" style="font-size: 0.65rem; padding: 0.15rem 0.4rem;">Simulate 20</button>
          </div>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Graduation fetch error:", err);
  }
}

async function simulateStreak(category) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/graduation/${category}/simulate-streak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count: 20 })
    });
    const data = await res.json();
    alert(`Category ${category} reached 20 approvals! Now AUTO-SEND ELIGIBLE.`);
    fetchGraduation();
  } catch (err) {
    alert("Simulate streak failed.");
  }
}

async function fetchFeedback() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/feedback`);
    const data = await res.json();

    document.getElementById("metric-prompt-ver").innerText = data.prompt_version;
    document.getElementById("metric-improvement").innerText = `+${data.metrics.improvement_percentage}%`;
    document.getElementById("rules-count").innerText = data.active_rules.length;

    const container = document.getElementById("rules-list");
    if (!data.recent_feedbacks || data.recent_feedbacks.length === 0) {
      container.innerHTML = `<p style="color: #64748b; font-size: 0.75rem;">No human edits recorded yet. When you edit a draft, learned rules appear here.</p>`;
      return;
    }

    container.innerHTML = data.recent_feedbacks.map(f => `
      <div class="rule-item">
        <div class="rule-header">
          <span class="rule-cat">${formatCategory(f.category)}</span>
          ${f.active ? `<button class="btn-undo" onclick="undoFeedback('${f.id}')">Undo Rule</button>` : `<span style="color:#64748b; font-size:0.65rem;">(Undone)</span>`}
        </div>
        <div style="color: #cbd5e1; margin-bottom: 0.3rem;"><strong>Rule:</strong> ${escapeHtml(f.learned_rule)}</div>
        <div style="color: #64748b; font-size: 0.68rem;">Diff: ${f.edit_distance} chars &bull; Similarity: ${Math.round(f.similarity_ratio * 100)}%</div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Feedback fetch error:", err);
  }
}

async function undoFeedback(feedbackId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/feedback/undo/${feedbackId}`, { method: "POST" });
    if (res.ok) {
      alert(`Feedback ${feedbackId} undone. Prompt rolled back.`);
      fetchFeedback();
    }
  } catch (err) {
    alert("Failed to undo feedback.");
  }
}

function formatCategory(c) {
  const map = {
    how_to: 'How-To',
    new_project: 'New Project',
    refund: 'Refund / Billing',
    complaint: 'Complaint',
    quote: 'Quote',
    follow_up: 'Follow-Up'
  };
  return map[c] || c;
}

function formatStatus(s) {
  const map = {
    unread: 'Unread',
    drafted: 'Draft Ready',
    approved: 'Sent (1-Click)',
    edited_and_sent: 'Edited & Sent',
    custom_sent: 'Custom Sent',
    auto_sent: 'Auto-Sent 🚀'
  };
  return map[s] || s;
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
