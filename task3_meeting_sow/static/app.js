// Task 3 Meeting to Scope of Work Web Client

const API_BASE = window.location.origin;
let currentProposalId = null;
let currentPipelineData = null;

document.addEventListener("DOMContentLoaded", () => {
  loadTranscript("meeting_1");
  loadFollowup("meeting_2");
  setupTabs();
  setupPipelineRun();
  setupApproval();
});

async function loadTranscript(transcriptId) {
  // Update buttons
  document.querySelectorAll(".selector-btn").forEach(b => b.classList.remove("active"));
  const btn = document.getElementById(`btn-${transcriptId === 'meeting_1' ? 'm1' : transcriptId === 'meeting_2' ? 'm2' : 'm3'}`);
  if (btn) btn.classList.add("active");

  try {
    const res = await fetch(`${API_BASE}/api/v1/transcripts/${transcriptId}`);
    const data = await res.json();
    document.getElementById("transcript-text").value = data.content;
    document.getElementById("transcript-label").innerText = `${data.filename} (${data.id})`;
  } catch (err) {
    console.error("Failed to load transcript:", err);
  }
}

async function loadFollowup(transcriptId) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/transcripts/${transcriptId}`);
    const data = await res.json();
    document.getElementById("followup-text").value = data.content;
  } catch (err) {
    console.error("Failed to load followup:", err);
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
    });
  });
}

function setupPipelineRun() {
  const runBtn = document.getElementById("btn-run-pipeline");
  runBtn.addEventListener("click", async () => {
    const transcriptText = document.getElementById("transcript-text").value.trim();
    if (!transcriptText) {
      alert("Please provide a transcript text.");
      return;
    }

    const includeFollowup = document.getElementById("check-followup").checked;
    const followupText = includeFollowup ? document.getElementById("followup-text").value.trim() : null;

    runBtn.disabled = true;
    runBtn.innerText = "Running Multi-Agent Team...";

    // Stepper animation
    animateSteps();

    try {
      const res = await fetch(`${API_BASE}/api/v1/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcript_text: transcriptText,
          followup_transcript: followupText
        })
      });

      const data = await res.json();
      currentPipelineData = data;
      currentProposalId = data.proposal.proposal_id;

      renderPipelineOutputs(data);
    } catch (err) {
      alert("Pipeline analysis failed: " + err.message);
    } finally {
      runBtn.disabled = false;
      runBtn.innerText = "🚀 Run Multi-Agent Analysis";
    }
  });
}

function animateSteps() {
  const steps = ["step-consultant", "step-solution", "step-estimator", "step-proposal"];
  steps.forEach(s => document.getElementById(s).classList.remove("active"));

  let idx = 0;
  const interval = setInterval(() => {
    if (idx < steps.length) {
      document.getElementById(steps[idx]).classList.add("active");
      idx++;
    } else {
      clearInterval(interval);
    }
  }, 350);
}

function renderPipelineOutputs(data) {
  // 1. SOW Tab
  document.getElementById("savings-amount").innerText = `$${data.sow.estimated_savings_from_native.toLocaleString(undefined, { minimumFractionDigits: 2 })} Saved`;
  document.getElementById("savings-desc").innerText = `${data.sow.native_count} requirements solved with out-of-the-box Brilliant Directories settings without custom code.`;

  const reqList = document.getElementById("requirements-list");
  reqList.innerHTML = data.sow.requirements.map(r => `
    <div class="req-item-card">
      <div class="req-header">
        <span class="req-title">${escapeHtml(r.title)}</span>
        <span class="type-pill ${r.is_native_setting ? 'type-native' : 'type-custom'}">
          ${r.is_native_setting ? '⚡ NATIVE BD SETTING ($0 DEV COST)' : '🛠️ CUSTOM ENGINEERING'}
        </span>
      </div>
      <div class="req-statement">"${escapeHtml(r.raw_statement)}"</div>
      <div class="req-solution">
        ${r.is_native_setting ? `<strong>Configuration Path:</strong> ${escapeHtml(r.native_setting_path)}` : `<strong>Engineering Plan:</strong> ${escapeHtml(r.notes)}`}
        ${r.kb_citation_title ? `<br/><span style="color:#93c5fd; font-size:0.72rem;">KB Guide: ${escapeHtml(r.kb_citation_title)}</span>` : ''}
      </div>
    </div>
  `).join("");

  // 2. Task Breakdown Tab
  document.getElementById("stat-total-hours").innerText = `${data.tasks.total_hours} hrs`;
  document.getElementById("stat-qa-hours").innerText = `${data.tasks.qa_buffer_hours} hrs`;
  document.getElementById("stat-pm-hours").innerText = `${data.tasks.project_management_hours} hrs`;
  document.getElementById("stat-total-cost").innerText = `$${data.tasks.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}`;

  const tasksList = document.getElementById("tasks-list");
  tasksList.innerHTML = data.tasks.tasks.map(t => `
    <div class="task-item-card">
      <div class="task-meta">
        <h4>${escapeHtml(t.task_name)} <span style="font-size:0.65rem; color:#94a3b8; font-weight:normal;">(${t.dev_type})</span></h4>
        <p>${escapeHtml(t.description)}</p>
      </div>
      <div class="task-hours">
        <strong>${t.estimated_hours} hrs</strong><br/>
        <span style="color:#64748b; font-size:0.75rem;">$${t.cost.toLocaleString()}</span>
      </div>
    </div>
  `).join("");

  // 3. Client Proposal Tab
  document.getElementById("prop-title").innerText = data.proposal.title;
  document.getElementById("prop-id").innerText = data.proposal.proposal_id;
  document.getElementById("prop-client").innerText = data.proposal.client_name;
  document.getElementById("prop-company").innerText = data.proposal.company_name;
  document.getElementById("prop-timeline").innerText = data.proposal.timeline_weeks;
  document.getElementById("prop-executive").innerText = data.proposal.executive_summary;

  document.getElementById("prop-native-list").innerHTML = data.proposal.native_features_utilized.map(f => `<li>${escapeHtml(f)}</li>`).join("");
  document.getElementById("prop-custom-list").innerHTML = data.proposal.custom_deliverables.map(d => `<li>${escapeHtml(d)}</li>`).join("");

  // 4. Scope Delta & Scope Creep Tab
  if (data.delta) {
    document.getElementById("btn-tab-delta").style.display = "block";
    document.getElementById("delta-summary-text").innerText = data.delta.summary;
    document.getElementById("creep-total-quote").innerText = `$${data.delta.scope_creep_addon_quote.toLocaleString(undefined, { minimumFractionDigits: 2 })} (${data.delta.scope_creep_hours} hrs)`;

    // Creep list
    const creepList = document.getElementById("creep-items-list");
    creepList.innerHTML = data.delta.scope_creep_items.map(c => `
      <div class="req-item-card" style="border-color: rgba(244, 63, 94, 0.3);">
        <div class="req-header">
          <span class="req-title" style="color: #fda4af;">${escapeHtml(c.title)}</span>
          <span class="type-pill" style="background: rgba(244, 63, 94, 0.2); color: #fda4af;">+${c.updated_hours} hrs ($${c.extra_cost.toLocaleString()})</span>
        </div>
        <div class="req-statement" style="color: #cbd5e1;">${escapeHtml(c.change_description)}</div>
      </div>
    `).join("");

    // Modified & Dropped items
    const deltaItemsList = document.getElementById("delta-items-list");
    const diffs = [...data.delta.modified_items, ...data.delta.dropped_items];
    deltaItemsList.innerHTML = diffs.map(d => `
      <div class="req-item-card">
        <div class="req-header">
          <span class="req-title">${escapeHtml(d.title)}</span>
          <span class="type-pill" style="background: ${d.status === 'DROPPED' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(59, 130, 246, 0.2)'}; color: ${d.status === 'DROPPED' ? '#fcd34d' : '#93c5fd'};">
            ${d.status} (${d.status === 'DROPPED' ? `-${d.original_hours} hrs` : `+${d.updated_hours - d.original_hours} hrs`})
          </span>
        </div>
        <div class="req-statement">${escapeHtml(d.change_description)}</div>
      </div>
    `).join("");
  }
}

function setupApproval() {
  const btnApprove = document.getElementById("btn-approve-proposal");
  btnApprove.addEventListener("click", async () => {
    if (!currentProposalId) {
      alert("Please run multi-agent analysis first.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${currentProposalId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consultant_name: "Lead Solutions Director" })
      });
      const data = await res.json();
      alert(`Success! Proposal ${currentProposalId} approved by Human Consultant.\nApproved at: ${data.approved_at}\nClient-ready status unlocked.`);

      document.getElementById("metric-approval-status").innerText = "Approved & Signed";
      document.getElementById("metric-approval-status").className = "val text-green";
      document.getElementById("appr-status-text").innerText = `✅ Approved by Human Consultant on ${new Date(data.approved_at).toLocaleString()}`;
      btnApprove.disabled = true;
      btnApprove.innerText = "✅ Proposal Approved";
    } catch (err) {
      alert("Failed to approve proposal.");
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
