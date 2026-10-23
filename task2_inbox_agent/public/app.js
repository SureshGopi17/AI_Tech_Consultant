// Task 2 Inbox Agent Web Client - Gmail Experience & Self-Improving Learning Loop

const API_BASE = window.location.origin;
let emails = [];
let selectedEmailId = null;
let currentFolder = 'inbox';
let activeCategoryFilter = null;
let searchQuery = '';
let autoSendThreshold = 3;

document.addEventListener("DOMContentLoaded", () => {
  fetchThresholdSettings();
  fetchGmailConfig();
  fetchEmails();
  fetchGraduation();
  fetchFeedback();
  setupNavigation();
  setupSearch();
  setupActionHandlers();
  setupSettingsModal();
});

// =====================================================================
// 1. Data Loading & Email Rendering
// =====================================================================
async function fetchEmails() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/emails`);
    const data = await res.json();
    emails = data.emails;
    updateSidebarCounts();
    renderGmailTable();

    if (!selectedEmailId && emails.length > 0) {
      selectEmail(emails[0].id);
    }
  } catch (err) {
    console.error("Failed to load emails:", err);
  }
}

function updateSidebarCounts() {
  const unread = emails.filter(e => e.status === 'unread' || e.status === 'drafted').length;
  const autoSent = emails.filter(e => e.status === 'auto_sent').length;
  const drafts = emails.filter(e => e.status === 'drafted').length;

  document.getElementById("inbox-unread-count").innerText = unread;
  document.getElementById("autosent-count").innerText = autoSent;
  document.getElementById("drafts-count").innerText = drafts;

  // Category counts
  document.getElementById("lbl-count-howto").innerText = emails.filter(e => e.category === 'how_to').length;
  document.getElementById("lbl-count-refund").innerText = emails.filter(e => e.category === 'refund').length;
  document.getElementById("lbl-count-complaint").innerText = emails.filter(e => e.category === 'complaint').length;
  document.getElementById("lbl-count-project").innerText = emails.filter(e => e.category === 'new_project').length;
  document.getElementById("lbl-count-quote").innerText = emails.filter(e => e.category === 'quote').length;
  document.getElementById("lbl-count-followup").innerText = emails.filter(e => e.category === 'follow_up').length;
}

function getFilteredEmails() {
  return emails.filter(e => {
    // Search query filter
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const match = (e.subject || '').toLowerCase().includes(q) ||
                    (e.body || '').toLowerCase().includes(q) ||
                    (e.customer_name || '').toLowerCase().includes(q) ||
                    (e.customer_email || '').toLowerCase().includes(q) ||
                    (e.label_name || '').toLowerCase().includes(q);
      if (!match) return false;
    }

    // Category / Label filter
    if (activeCategoryFilter && e.category !== activeCategoryFilter) {
      return false;
    }

    // Folder filter
    if (currentFolder === 'inbox') return true;
    if (currentFolder === 'starred') return e.is_starred === true;
    if (currentFolder === 'auto_sent') return e.status === 'auto_sent';
    if (currentFolder === 'drafts') return e.status === 'drafted';
    if (currentFolder === 'sent') return e.status === 'approved' || e.status === 'edited_and_sent' || e.status === 'custom_sent' || e.status === 'auto_sent';
    return true;
  });
}

function renderGmailTable() {
  const container = document.getElementById("gmail-table-container");
  const filtered = getFilteredEmails();

  document.getElementById("email-page-range").innerText = `1–${filtered.length} of ${emails.length}`;

  if (filtered.length === 0) {
    container.innerHTML = `<div style="padding: 2rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">No conversations in this view.</div>`;
    return;
  }

  container.innerHTML = filtered.map(e => {
    const isSelected = e.id === selectedEmailId;
    const isUnread = e.status === 'unread';
    const isStarred = e.is_starred ? 'starred' : '';
    const dateStr = formatDate(e.date);

    let categoryBadge = `<span class="row-badge" style="background: rgba(59, 130, 246, 0.15); color: #93c5fd;">${e.label_name || formatCategory(e.category)}</span>`;
    if (e.category === 'refund') categoryBadge = `<span class="row-badge" style="background: rgba(139, 92, 246, 0.15); color: #c084fc;">${e.label_name || 'Refund'}</span>`;
    if (e.category === 'complaint') categoryBadge = `<span class="row-badge" style="background: rgba(234, 67, 53, 0.15); color: #fca5a5;">${e.label_name || 'Outage'}</span>`;
    if (e.category === 'new_project') categoryBadge = `<span class="row-badge" style="background: rgba(52, 168, 83, 0.15); color: #86efac;">${e.label_name || 'Project'}</span>`;

    let statusPill = '';
    if (e.status === 'auto_sent') {
      statusPill = `<span class="row-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-weight: 700;">🤖 Auto-Sent</span>`;
    } else if (e.status === 'drafted') {
      statusPill = `<span class="row-badge" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">Draft Ready</span>`;
    }

    return `
      <div class="gmail-row ${isUnread ? 'unread' : ''} ${isSelected ? 'active' : ''}" onclick="selectEmail('${e.id}')">
        <input type="checkbox" onclick="event.stopPropagation();" />
        <span class="row-star ${isStarred}" onclick="toggleStar(event, '${e.id}')">★</span>
        <div class="row-sender">${escapeHtml(e.customer_name)}</div>
        <div class="row-content">
          <span class="row-subject">${escapeHtml(e.subject)}</span>
          <span class="row-snippet">— ${escapeHtml(e.body)}</span>
        </div>
        ${categoryBadge}
        ${statusPill}
        <div class="row-date">${dateStr}</div>
      </div>
    `;
  }).join("");
}

window.toggleStar = function(event, id) {
  event.stopPropagation();
  const email = emails.find(e => e.id === id);
  if (email) {
    email.is_starred = !email.is_starred;
    renderGmailTable();
  }
};

// =====================================================================
// 2. Thread Selection & AI Grounded Reply Drafting
// =====================================================================
async function selectEmail(id) {
  selectedEmailId = id;
  renderGmailTable();

  const email = emails.find(e => e.id === id);
  if (!email) return;

  document.getElementById("empty-thread-state").style.display = "none";
  document.getElementById("thread-content").style.display = "flex";

  document.getElementById("thread-subject").innerText = email.subject;
  document.getElementById("thread-sender-name").innerText = email.customer_name;
  document.getElementById("thread-sender-email").innerText = `<${email.customer_email}>`;
  document.getElementById("thread-company-name").innerText = email.company_name;
  document.getElementById("thread-urgency-badge").innerText = email.urgency.toUpperCase();
  document.getElementById("thread-body-text").innerText = email.body;
  document.getElementById("thread-timestamp").innerText = formatDate(email.date);

  // Avatar initials
  const initials = email.customer_name.split(" ").map(p => p[0]).join("").slice(0, 2).toUpperCase();
  document.getElementById("thread-sender-avatar").innerText = initials;

  // Labels & Parent Setting Badges (Requirement 7)
  document.getElementById("thread-parent-setting-badge").innerText = email.parent_setting_type || "Member & Directory Settings";
  document.getElementById("thread-category-badge").innerText = email.label_name || formatCategory(email.category);

  // Draft section
  const textarea = document.getElementById("draft-reply-textarea");
  const confTag = document.getElementById("draft-confidence-badge");
  const citationsBox = document.getElementById("draft-citations-box");
  const diffCard = document.getElementById("diff-learning-card");

  diffCard.style.display = "none";

  if (email.drafted_reply) {
    textarea.value = email.drafted_reply;
    confTag.innerText = `Confidence: ${Math.round((email.confidence || 0.94) * 100)}%`;
    renderCitations(citationsBox, email.citations || []);
  } else {
    textarea.value = "Consulting Knowledge Brain and drafting personalized reply in company voice...";
    confTag.innerText = "Drafting...";
    citationsBox.innerHTML = "";

    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${id}/draft`, { method: "POST" });
      const data = await res.json();
      email.drafted_reply = data.email.drafted_reply;
      email.confidence = data.email.confidence;
      email.citations = data.email.citations;
      email.status = "drafted";

      textarea.value = email.drafted_reply;
      confTag.innerText = `Confidence: ${Math.round(email.confidence * 100)}%`;
      renderCitations(citationsBox, email.citations);
      renderGmailTable();
      updateSidebarCounts();
    } catch (err) {
      textarea.value = "Failed to draft reply.";
    }
  }
}

function renderCitations(container, citations) {
  if (!citations || citations.length === 0) {
    container.innerHTML = `<span style="color: #64748b;">No direct Knowledge Brain match cited. Drafted using verified consultant standard practices.</span>`;
    return;
  }

  container.innerHTML = `<strong style="color: #93c5fd;">📚 Knowledge Brain Citations Grounding this Draft:</strong>` + citations.map(c => `
    <div style="margin-top: 2px;">
      • <a href="${c.url}" target="_blank" style="color: #38bdf8; text-decoration: underline;">${escapeHtml(c.title)}</a>
      <span style="color: #94a3b8;">(${c.category})</span>
    </div>
  `).join("");
}

// =====================================================================
// 3. Send Actions & Self-Improving Feedback Loop
// =====================================================================
function setupActionHandlers() {
  // Send Unchanged (Requirement 7: counts towards consecutive unedited graduation streak)
  document.getElementById("btn-send-unchanged").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/approve`, { method: "POST" });
      const data = await res.json();
      const streak = data.graduation_state.consecutive_unchanged;
      const threshold = data.graduation_state.threshold;

      if (data.graduation_state.auto_send_eligible) {
        alert(`🎓 AUTONOMOUS GRADUATION! Category '${data.email.category}' reached ${streak}/${threshold} consecutive unedited approvals. Status: AUTO_SEND_ELIGIBLE! Future replies will now send automatically.`);
      } else {
        alert(`✅ Draft sent unchanged via Gmail! Consecutive unedited streak: ${streak}/${threshold}`);
      }

      fetchEmails();
      fetchGraduation();
    } catch (err) {
      alert("Send approval failed: " + err.message);
    }
  });

  // Edit & Send (Requirement 2 & 7: Learn from edits)
  document.getElementById("btn-send-edited").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    const editedText = document.getElementById("draft-reply-textarea").value.trim();
    if (!editedText) return;

    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ edited_reply: editedText })
      });
      const data = await res.json();

      // Show Learning Diff Card
      const diffCard = document.getElementById("diff-learning-card");
      diffCard.style.display = "block";
      document.getElementById("diff-similarity-badge").innerText = `Similarity: ${(data.feedback.similarity_ratio * 100).toFixed(1)}%`;
      document.getElementById("diff-distance-val").innerText = `${data.feedback.edit_distance} characters modified`;
      document.getElementById("diff-rule-text").innerText = `"${data.feedback.learned_rule}"`;

      alert(`✉️ Edited reply sent! Agent calculated Levenshtein distance (${data.feedback.edit_distance} chars) and learned rule: "${data.feedback.learned_rule}". Prompt incremented.`);

      fetchEmails();
      fetchGraduation();
      fetchFeedback();
    } catch (err) {
      alert("Failed to send edited email: " + err.message);
    }
  });

  // Custom Reply
  document.getElementById("btn-custom-send").addEventListener("click", async () => {
    if (!selectedEmailId) return;
    const custom = prompt("Enter custom email reply to dispatch via Gmail:");
    if (!custom) return;

    try {
      await fetch(`${API_BASE}/api/v1/emails/${selectedEmailId}/custom`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ custom_reply: custom })
      });
      alert("Custom reply dispatched through Gmail and recorded to training store.");
      fetchEmails();
      fetchGraduation();
      fetchFeedback();
    } catch (err) {
      alert("Failed to send custom reply.");
    }
  });

  // Discard draft
  document.getElementById("btn-discard-draft").addEventListener("click", () => {
    document.getElementById("draft-reply-textarea").value = "";
  });

  // Back to list button (mobile/narrow view)
  document.getElementById("btn-back-to-list").addEventListener("click", () => {
    document.getElementById("thread-content").style.display = "none";
    document.getElementById("empty-thread-state").style.display = "flex";
  });

  // Regenerate draft
  document.getElementById("btn-regenerate-draft").addEventListener("click", () => {
    if (!selectedEmailId) return;
    const email = emails.find(e => e.id === selectedEmailId);
    if (email) {
      email.drafted_reply = undefined;
      selectEmail(selectedEmailId);
    }
  });

  // Batch auto-process
  document.getElementById("btn-batch-process").addEventListener("click", async () => {
    const btn = document.getElementById("btn-batch-process");
    btn.disabled = true;
    btn.innerText = "Processing...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/emails/auto-process`, { method: "POST" });
      const data = await res.json();
      alert(`⚡ Batch processed ${data.total_processed} emails! (${data.auto_sent_count} automatically dispatched, ${data.drafted_count} prepared for review).`);
      fetchEmails();
      fetchGraduation();
    } catch (e) {
      alert("Batch processing error: " + e.message);
    } finally {
      btn.disabled = false;
      btn.innerText = "⚡ Batch Auto-Process";
    }
  });

  // Sync with Gmail (Requirement 8)
  document.getElementById("btn-sync-gmail").addEventListener("click", async () => {
    const btn = document.getElementById("btn-sync-gmail");
    btn.disabled = true;
    btn.innerText = "Syncing...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/gmail/sync`, { method: "POST" });
      const data = await res.json();
      alert(`📥 ${data.message}`);
      fetchEmails();
    } catch (e) {
      alert("Gmail sync error: " + e.message);
    } finally {
      btn.disabled = false;
      btn.innerText = "📥 Sync Gmail";
    }
  });

  document.getElementById("btn-refresh-mail").addEventListener("click", fetchEmails);
}

// =====================================================================
// 4. Navigation & Search Filtering
// =====================================================================
function setupNavigation() {
  const folderItems = document.querySelectorAll(".gmail-folder-nav .nav-item");
  folderItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      folderItems.forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      currentFolder = item.getAttribute("data-folder");
      activeCategoryFilter = null;
      document.querySelectorAll(".label-item").forEach(l => l.classList.remove("active"));
      renderGmailTable();
    });
  });

  const labelItems = document.querySelectorAll(".label-item");
  labelItems.forEach(lbl => {
    lbl.addEventListener("click", () => {
      labelItems.forEach(l => l.classList.remove("active"));
      lbl.classList.add("active");
      activeCategoryFilter = lbl.getAttribute("data-category");
      renderGmailTable();
    });
  });
}

function setupSearch() {
  const searchInput = document.getElementById("gmail-search-input");
  searchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value.trim();
    renderGmailTable();
  });
}

// =====================================================================
// 5. Configurable Threshold X & Gmail Settings (Requirement 7 & 8)
// =====================================================================
function setupSettingsModal() {
  const settingsModal = document.getElementById("modal-settings");
  const openSettingsBtn = document.getElementById("btn-open-settings");
  const closeSettingsBtn = document.getElementById("btn-close-settings");

  openSettingsBtn.addEventListener("click", () => {
    settingsModal.style.display = "flex";
    fetchGraduation();
  });
  closeSettingsBtn.addEventListener("click", () => {
    settingsModal.style.display = "none";
  });

  // Settings sub-tabs
  const stabBtns = document.querySelectorAll(".settings-tab-btn");
  stabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      stabBtns.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".settings-tab-content").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-stab");
      document.getElementById(targetId).classList.add("active");
    });
  });

  // Threshold X Save
  document.getElementById("btn-save-threshold").addEventListener("click", async () => {
    const val = parseInt(document.getElementById("input-threshold-x").value, 10);
    try {
      const res = await fetch(`${API_BASE}/api/v1/settings/threshold`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threshold_x: val })
      });
      const data = await res.json();
      autoSendThreshold = data.threshold_x;
      alert(`✅ ${data.message}`);
      fetchGraduation();
    } catch (e) {
      alert("Failed to save threshold: " + e.message);
    }
  });

  // Test Gmail Connection
  document.getElementById("btn-test-gmail-conn").addEventListener("click", async () => {
    const email = document.getElementById("gmail-email-input").value.trim();
    const mode = document.getElementById("gmail-mode-select").value;
    const pwd = document.getElementById("gmail-password-input").value;
    const feedback = document.getElementById("gmail-test-feedback");

    feedback.style.display = "block";
    feedback.style.background = "rgba(59, 130, 246, 0.15)";
    feedback.style.color = "#93c5fd";
    feedback.innerText = "Testing IMAP/SMTP handshake...";

    try {
      const res = await fetch(`${API_BASE}/api/v1/gmail/test-connection`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gmail_address: email, mode, app_password: pwd })
      });
      const data = await res.json();
      if (data.success) {
        feedback.style.background = "rgba(16, 185, 129, 0.2)";
        feedback.style.color = "#34d399";
        feedback.innerText = `✅ ${data.message}`;
        document.getElementById("sync-status-text").innerText = mode === 'live' ? 'Gmail Live Connected' : 'Gmail Demo Sandbox';
      } else {
        feedback.style.background = "rgba(244, 63, 94, 0.2)";
        feedback.style.color = "#f43f5e";
        feedback.innerText = `❌ ${data.message}`;
      }
    } catch (err) {
      feedback.style.background = "rgba(244, 63, 94, 0.2)";
      feedback.style.color = "#f43f5e";
      feedback.innerText = err.message;
    }
  });

  // Analytics Modal
  const analyticsModal = document.getElementById("modal-analytics");
  document.getElementById("btn-open-analytics").addEventListener("click", () => {
    analyticsModal.style.display = "flex";
    fetchFeedback();
  });
  document.getElementById("btn-close-analytics").addEventListener("click", () => {
    analyticsModal.style.display = "none";
  });
}

async function fetchThresholdSettings() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/settings/threshold`);
    const data = await res.json();
    autoSendThreshold = data.threshold_x;
    document.getElementById("input-threshold-x").value = autoSendThreshold;
  } catch (e) {
    console.error("Threshold fetch error:", e);
  }
}

async function fetchGmailConfig() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/settings/gmail`);
    const cfg = await res.json();
    document.getElementById("gmail-mode-select").value = cfg.mode || 'demo';
    document.getElementById("gmail-email-input").value = cfg.gmail_address || 'consultant.demo@gmail.com';
    document.getElementById("sync-status-text").innerText = cfg.mode === 'live' ? 'Gmail Live Sync' : 'Gmail Demo Mode';
  } catch (e) {
    console.error("Gmail config fetch error:", e);
  }
}

async function fetchGraduation() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/graduation`);
    const data = await res.json();
    const container = document.getElementById("settings-graduation-table");
    if (!container) return;

    container.innerHTML = data.states.map(s => {
      const isGrad = s.auto_send_eligible;
      const pct = Math.min(100, Math.round((s.consecutive_unchanged / (s.threshold || autoSendThreshold)) * 100));

      return `
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.6rem; margin-bottom: 0.4rem; font-size: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <strong>${s.category_label}</strong>
            <span class="badge" style="${isGrad ? 'background: rgba(16, 185, 129, 0.2); color: #34d399;' : 'background: rgba(245, 158, 11, 0.15); color: #fbbf24;'}">
              ${isGrad ? '🎓 AUTO-SEND UNLOCKED' : `Streak: ${s.consecutive_unchanged} / ${s.threshold || autoSendThreshold}`}
            </span>
          </div>
          <div style="background: #334155; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="background: ${isGrad ? '#10b981' : '#3b82f6'}; width: ${pct}%; height: 100%;"></div>
          </div>
        </div>
      `;
    }).join("");
  } catch (e) {
    console.error("Graduation fetch error:", e);
  }
}

async function fetchFeedback() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/feedback`);
    const data = await res.json();

    const verEl = document.getElementById("metric-prompt-ver");
    if (verEl) verEl.innerText = data.prompt_version;
    const anaVerEl = document.getElementById("analytics-prompt-ver");
    if (anaVerEl) anaVerEl.innerText = data.prompt_version;

    const imp = data.metrics.improvement_percentage;
    const impEl = document.getElementById("metric-improvement");
    if (impEl) impEl.innerText = `+${imp.toFixed(1)}%`;
    const anaImpEl = document.getElementById("analytics-improvement");
    if (anaImpEl) anaImpEl.innerText = `+${imp.toFixed(1)}%`;

    const rulesCountEl = document.getElementById("analytics-rules-count");
    if (rulesCountEl) rulesCountEl.innerText = data.active_rules.length;

    const rulesList = document.getElementById("analytics-rules-list");
    if (rulesList) {
      if (data.recent_feedbacks.length === 0) {
        rulesList.innerHTML = `<p style="color: var(--text-muted); font-size: 0.75rem;">No edit feedback recorded yet. Edit any draft to train the agent.</p>`;
      } else {
        rulesList.innerHTML = data.recent_feedbacks.map(f => `
          <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.5rem; margin-bottom: 0.4rem; font-size: 0.75rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <strong>Rule from ${f.subject}:</strong>
              <button class="btn btn-secondary btn-sm" onclick="undoFeedback('${f.id}')" style="font-size: 0.68rem; padding: 2px 6px;">Undo</button>
            </div>
            <div style="color: #cbd5e1; margin-top: 0.2rem;">${f.learned_rule}</div>
          </div>
        `).join("");
      }
    }
  } catch (e) {
    console.error("Feedback fetch error:", e);
  }
}

window.undoFeedback = async function(id) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/feedback/undo/${id}`, { method: "POST" });
    const data = await res.json();
    alert(`Rule undone! Prompt rolled back to ${data.prompt_version}`);
    fetchFeedback();
  } catch (e) {
    alert("Undo failed: " + e.message);
  }
};

// Helpers
function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  if (d.toDateString() === now.toDateString()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function formatCategory(cat) {
  const map = {
    how_to: 'How-To Inquiry',
    new_project: 'New Project',
    refund: 'Billing & Refund',
    complaint: 'Urgent Incident',
    quote: 'Commercial Quote',
    follow_up: 'Work Follow-Up'
  };
  return map[cat] || cat;
}
