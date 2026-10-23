// Task 1 Knowledge Brain UI Client - Multi-Dashboard & Verification Suite

const API_BASE = window.location.origin;

function getStorageItem(key) {
  try {
    return localStorage.getItem(key);
  } catch (e) {
    return null;
  }
}

function setStorageItem(key, val) {
  try {
    localStorage.setItem(key, val);
  } catch (e) {}
}

// Auto-inject JWT Bearer Token into all API requests
const originalFetch = window.fetch.bind(window);
window.fetch = function(url, options) {
  try {
    const token = getStorageItem("kb_jwt_token");
    if (token && typeof url === "string" && url.includes("/api/v1/")) {
      options = options ? Object.assign({}, options) : {};
      const headers = Object.assign({}, options.headers || {});
      if (!headers["Authorization"]) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      options.headers = headers;
    }
  } catch (e) {
    console.warn("Fetch interceptor warning:", e);
  }
  return originalFetch(url, options);
};

// Global helpers for modals and controls
window.setExampleSitemap = function(url) {
  const input = document.getElementById("input-new-sitemap-url");
  if (input) {
    input.value = url;
    input.focus();
    input.style.borderColor = "#3b82f6";
    setTimeout(() => { input.style.borderColor = ""; }, 1500);
  }
};

window.openCreateDashboardModal = function() {
  const modal = document.getElementById("modal-create-dashboard");
  if (modal) modal.style.display = "flex";
};

window.closeCreateDashboardModal = function() {
  const modal = document.getElementById("modal-create-dashboard");
  if (modal) modal.style.display = "none";
};

window.openAuthModal = function() {
  const modal = document.getElementById("modal-auth");
  if (modal) {
    const displayEl = document.getElementById("jwt-token-display");
    if (displayEl) {
      displayEl.innerText = getStorageItem("kb_jwt_token") || "No active JWT token found.";
    }
    modal.style.display = "flex";
  }
};

window.closeAuthModal = function() {
  const modal = document.getElementById("modal-auth");
  if (modal) modal.style.display = "none";
};

let activeDashboardId = "dash-bd-prod-01";
let currentInventoryUrls = [];
let selectedUrls = new Set();
let currentFilter = "all";

document.addEventListener("DOMContentLoaded", () => {
  // 1. Synchronously bind all event handlers immediately
  setupAuth();
  setupDashboardSwitcher();
  setupTabs();
  setupChat();
  setupSync();
  setupSitemapsHub();
  setupRefreshRun();
  setupReconciliationAndHealth();
  setupPreFlightAndConfirmation();
  setupScheduleAndRetention();
  setupArchivedSafeStore();
  setupModals();

  // 2. Load dashboard data immediately
  loadDashboardData();

  // 3. Initialize/validate JWT session asynchronously in the background
  initSession().then(() => {
    fetchDashboardsList();
  }).catch(err => {
    console.warn("Session init warning:", err);
  });
});

async function initSession() {
  const token = getStorageItem("kb_jwt_token");
  if (token) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/me`);
      if (res.ok) {
        const user = await res.json();
        const userEl = document.getElementById("session-user");
        const roleEl = document.getElementById("session-role");
        if (userEl) userEl.innerText = user.name;
        if (roleEl) roleEl.innerText = `${user.role} (JWT Active)`;
        activeDashboardId = user.active_dashboard_id || "dash-bd-prod-01";
        return;
      }
    } catch (e) {
      console.warn("Could not resume saved JWT session, renewing...", e);
    }
  }

  // Auto initialize demo session with JWT
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/demo-login`, { method: "POST" });
    const data = await res.json();
    if (data.success && data.token) {
      setStorageItem("kb_jwt_token", data.token);
      const userEl = document.getElementById("session-user");
      const roleEl = document.getElementById("session-role");
      if (userEl) userEl.innerText = data.user.name;
      if (roleEl) roleEl.innerText = `${data.user.role} (JWT Active)`;
      activeDashboardId = data.user.active_dashboard_id || "dash-bd-prod-01";
    }
  } catch (err) {
    console.error("Auto demo login error:", err);
  }
}

// =====================================================================
// 1. User Authentication & Demo Credentials
// =====================================================================
function setupAuth() {
  const authModalBtn = document.getElementById("btn-user-auth-modal");
  const authModal = document.getElementById("modal-auth");
  const closeAuthBtn = document.getElementById("btn-close-auth-modal");
  const oneClickDemoBtn = document.getElementById("btn-one-click-demo");
  const authForm = document.getElementById("form-auth-login");
  const feedbackEl = document.getElementById("auth-feedback");

  function updateJwtDisplay() {
    const token = localStorage.getItem("kb_jwt_token");
    const displayEl = document.getElementById("jwt-token-display");
    if (displayEl) {
      displayEl.innerText = token || "No active JWT token found.";
    }
  }

  authModalBtn.addEventListener("click", () => {
    updateJwtDisplay();
    authModal.style.display = "flex";
  });
  closeAuthBtn.addEventListener("click", () => {
    authModal.style.display = "none";
  });

  const copyJwtBtn = document.getElementById("btn-copy-jwt");
  if (copyJwtBtn) {
    copyJwtBtn.addEventListener("click", () => {
      const token = localStorage.getItem("kb_jwt_token") || "";
      navigator.clipboard.writeText(token);
      copyJwtBtn.innerText = "✅ Copied!";
      setTimeout(() => { copyJwtBtn.innerText = "📋 Copy Token"; }, 1500);
    });
  }

  const verifyJwtBtn = document.getElementById("btn-verify-jwt-server");
  if (verifyJwtBtn) {
    verifyJwtBtn.addEventListener("click", async () => {
      const statusEl = document.getElementById("jwt-verify-status");
      statusEl.innerText = "Verifying with server...";
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/verify-token`, { method: "POST" });
        const data = await res.json();
        if (data.valid) {
          statusEl.innerText = `✅ Verified (Role: ${data.user.role})`;
          statusEl.style.color = "#34d399";
        } else {
          statusEl.innerText = "❌ Invalid Token";
          statusEl.style.color = "#f43f5e";
        }
      } catch (err) {
        statusEl.innerText = "❌ " + err.message;
        statusEl.style.color = "#f43f5e";
      }
    });
  }

  oneClickDemoBtn.addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/demo-login`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        if (data.token) {
          localStorage.setItem("kb_jwt_token", data.token);
        }
        document.getElementById("session-user").innerText = data.user.name;
        document.getElementById("session-role").innerText = `${data.user.role} (JWT Active)`;
        activeDashboardId = data.user.active_dashboard_id || "dash-bd-prod-01";
        authModal.style.display = "none";
        loadDashboardData();
      }
    } catch (e) {
      alert("Error logging into demo account: " + e.message);
    }
  });

  authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("auth-email").value.trim();
    const password = document.getElementById("auth-password").value.trim();

    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        if (data.token) {
          localStorage.setItem("kb_jwt_token", data.token);
        }
        document.getElementById("session-user").innerText = data.user.name;
        document.getElementById("session-role").innerText = `${data.user.role} (JWT Active)`;
        activeDashboardId = data.user.active_dashboard_id || "dash-bd-prod-01";
        authModal.style.display = "none";
        loadDashboardData();
      } else {
        feedbackEl.style.display = "block";
        feedbackEl.style.color = "#f43f5e";
        feedbackEl.innerText = data.detail || "Authentication failed.";
      }
    } catch (err) {
      feedbackEl.style.display = "block";
      feedbackEl.style.color = "#f43f5e";
      feedbackEl.innerText = err.message;
    }
  });
}

// =====================================================================
// 2. Multi-Dashboard Management (CRUD + Switcher)
// =====================================================================
function setupDashboardSwitcher() {
  const dashSelect = document.getElementById("select-active-dashboard");
  const openCreateBtn = document.getElementById("btn-open-create-dash");
  const createModal = document.getElementById("modal-create-dashboard");
  const closeCreateBtn = document.getElementById("btn-close-dash-modal");
  const cancelCreateBtn = document.getElementById("btn-cancel-dash-modal");
  const createForm = document.getElementById("form-create-dashboard");

  dashSelect.addEventListener("change", (e) => {
    activeDashboardId = e.target.value;
    loadDashboardData();
  });

  openCreateBtn.addEventListener("click", () => {
    createModal.style.display = "flex";
  });
  const hideCreate = () => { createModal.style.display = "none"; };
  closeCreateBtn.addEventListener("click", hideCreate);
  cancelCreateBtn.addEventListener("click", hideCreate);

  createForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("dash-new-name").value.trim();
    const website = document.getElementById("dash-new-website").value.trim();
    const sitemap = document.getElementById("dash-new-sitemap").value.trim();
    const desc = document.getElementById("dash-new-desc").value.trim();

    const submitBtn = createForm.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.innerText : "Create Dashboard";

    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "⏳ Ingesting Sitemap URLs...";
      }

      const res = await fetch(`${API_BASE}/api/v1/dashboards`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          website_name: website,
          sitemap_urls: [sitemap],
          description: desc,
          consecutive_failure_threshold: 3
        })
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: "Error creating dashboard" }));
        throw new Error(errData.detail || "Error creating dashboard");
      }
      const newDash = await res.json();
      activeDashboardId = newDash.id;
      hideCreate();
      createForm.reset();
      await fetchDashboardsList();
      await loadDashboardData();

      // Automatically switch to Screenshot 2: Refresh Run & URLs tab
      if (window.switchTab) {
        window.switchTab("tab-refresh-run");
      }
    } catch (err) {
      alert("Error creating dashboard: " + err.message);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = originalText;
      }
    }
  });
}

async function fetchDashboardsList() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/dashboards`);
    if (!res.ok) return;
    const dashboards = await res.json();
    if (!Array.isArray(dashboards)) return;
    const select = document.getElementById("select-active-dashboard");
    if (select) {
      select.innerHTML = dashboards.map(d => `
        <option value="${d.id}" ${d.id === activeDashboardId ? 'selected' : ''}>${d.name} (${d.website_name})</option>
      `).join("");
    }
  } catch (e) {
    console.error("Failed to fetch dashboards:", e);
  }
}

// =====================================================================
// 3. Tab Navigation & Data Routing
// =====================================================================
window.switchTab = function(targetId) {
  if (!targetId) return;
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(b => {
    if (b.getAttribute("data-tab") === targetId) {
      b.classList.add("active");
    } else {
      b.classList.remove("active");
    }
  });

  document.querySelectorAll(".tab-pane").forEach(p => {
    if (p.id === targetId) {
      p.classList.add("active");
    } else {
      p.classList.remove("active");
    }
  });

  if (targetId === "tab-dashboard-summary") fetchDashboardSummary();
  if (targetId === "tab-sitemaps") fetchSitemapsView();
  if (targetId === "tab-refresh-run") fetchRefreshRunData();
  if (targetId === "tab-reconciliation") fetchReconciliationReport();
  if (targetId === "tab-archived") fetchArchivedUrls();
  if (targetId === "tab-escalations") fetchEscalations();
};

function setupTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      window.switchTab(targetId);
    });
  });
}

async function loadDashboardData() {
  await fetchDashboardsList();
  fetchHealth();
  fetchDashboardSummary();
  fetchEscalations();
  fetchRefreshRunData();
  fetchReconciliationReport();
  fetchArchivedUrls();
}

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

// =====================================================================
// 4. Knowledge Brain Dashboard Summary (Requirement 8)
// =====================================================================
async function fetchDashboardSummary() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/dashboard/summary?dash_id=${activeDashboardId}`);
    const d = await res.json();

    document.getElementById("dash-summary-title").innerText = `📊 Knowledge Brain Dashboard: ${d.website_name}`;
    document.getElementById("dash-website-name").innerText = d.website_name;
    document.getElementById("dash-kb-status").innerText = d.current_status;
    document.getElementById("dash-last-crawl-time").innerText = d.last_crawl_datetime || "Just now";
    document.getElementById("dash-website-summary").innerText = d.website_summary;

    document.getElementById("dash-total-discovered").innerText = d.total_discovered;
    document.getElementById("dash-successfully-indexed").innerText = d.successfully_indexed;
    document.getElementById("dash-pending-processing").innerText = d.pending_processing;
    document.getElementById("dash-quarantined-urls").innerText = d.quarantined_urls + d.failed_urls;
    document.getElementById("dash-skipped-urls").innerText = d.skipped_duplicates;

    // Sitemaps list
    const sitemapsContainer = document.getElementById("dash-sitemaps-list");
    sitemapsContainer.innerHTML = d.sitemap_urls.map(u => `<div>• <a href="${u}" target="_blank" style="color: #38bdf8;">${u}</a></div>`).join("");

    // Topics chips
    const topicsContainer = document.getElementById("dash-main-topics");
    topicsContainer.innerHTML = d.main_topics.map(t => `
      <span class="badge" style="background: rgba(59, 130, 246, 0.15); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3);">${t}</span>
    `).join("");
  } catch (err) {
    console.error("Dashboard summary fetch failed:", err);
  }
}

// =====================================================================
// 5. Multiple Sitemap Management (Parent & Child Sitemaps)
// =====================================================================
function setupSitemapsHub() {
  const addBtn = document.getElementById("btn-add-sitemap");
  const input = document.getElementById("input-new-sitemap-url");
  const feedback = document.getElementById("sitemap-add-feedback");

  addBtn.addEventListener("click", async () => {
    const sitemapUrl = input.value.trim();
    if (!sitemapUrl) return;

    try {
      addBtn.disabled = true;
      addBtn.innerText = "Validating...";
      const res = await fetch(`${API_BASE}/api/v1/sitemaps/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sitemap_url: sitemapUrl, dashboard_id: activeDashboardId })
      });
      const data = await res.json();
      feedback.style.display = "block";
      if (res.ok) {
        feedback.style.color = "#34d399";
        feedback.innerText = `✅ ${data.message}`;
        input.value = "";
        await fetchSitemapsView();
        await fetchRefreshRunData();
        await fetchDashboardSummary();
        await fetchReconciliationReport();
      } else {
        feedback.style.color = "#f43f5e";
        feedback.innerText = `❌ ${data.detail || "Validation failed"}`;
      }
    } catch (e) {
      feedback.style.display = "block";
      feedback.style.color = "#f43f5e";
      feedback.innerText = e.message;
    } finally {
      addBtn.disabled = false;
      addBtn.innerText = "Add & Validate";
    }
  });
}

async function fetchSitemapsView() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/dashboards/${activeDashboardId}`);
    const dash = await res.json();

    const countEl = document.getElementById("sitemaps-count");
    if (countEl) countEl.innerText = (dash.sitemap_urls || []).length;

    const container = document.getElementById("configured-sitemaps-container");
    container.innerHTML = (dash.sitemap_urls || []).map((url, i) => `
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <span style="font-size: 0.75rem; font-weight: 700; color: #38bdf8;">Parent Sitemap [${i + 1}]</span>
            <div style="font-family: var(--font-mono); font-size: 0.78rem; color: #f8fafc; margin-top: 0.2rem;">
              <a href="${url}" target="_blank" style="color: #93c5fd; text-decoration: none;">${url}</a>
            </div>
          </div>
          <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">Validated & Live</span>
        </div>
        ${(dash.child_sitemaps && dash.child_sitemaps.length > 0) ? `
          <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed var(--border-color);">
            <span style="font-size: 0.7rem; color: #94a3b8; font-weight: 600;">Discovered Child Sitemaps (${dash.child_sitemaps.length}):</span>
            <div style="margin-top: 0.25rem; font-family: var(--font-mono); font-size: 0.72rem; color: #cbd5e1; display: flex; flex-direction: column; gap: 0.2rem;">
              ${dash.child_sitemaps.map(c => `<div>↳ <a href="${c}" target="_blank" style="color: #cbd5e1;">${c}</a></div>`).join("")}
            </div>
          </div>
        ` : ''}
      </div>
    `).join("");
  } catch (e) {
    console.error("Error fetching sitemaps view:", e);
  }
}

// =====================================================================
// 6. Refresh Run & Complete Scrollable URL List (Requirements 3 & 4)
// =====================================================================
function setupRefreshRun() {
  // Filter pills
  const filterBtns = document.querySelectorAll("[data-url-filter]");
  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.getAttribute("data-url-filter");
      renderUrlsTable();
    });
  });

  // Select all checkbox
  const selectAllChk = document.getElementById("chk-select-all-urls");
  selectAllChk.addEventListener("change", (e) => {
    const checked = e.target.checked;
    selectedUrls.clear();
    if (checked) {
      const filtered = getFilteredUrls();
      filtered.forEach(u => selectedUrls.add(u.url));
    }
    updateSelectedCount();
    renderUrlsTable();
  });

  // Crawl Selected URLs button
  document.getElementById("btn-crawl-selected").addEventListener("click", async () => {
    if (selectedUrls.size === 0) {
      alert("Please select one or more URLs using the checkboxes.");
      return;
    }
    const btn = document.getElementById("btn-crawl-selected");
    btn.disabled = true;
    btn.innerText = "Crawling...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/urls/crawl-selected`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls: Array.from(selectedUrls), force_reindex: true })
      });
      const data = await res.json();
      alert(`Crawled ${data.crawled_count} URLs. Successfully indexed: ${data.successfully_indexed}, Failed: ${data.failed_count}`);
      selectedUrls.clear();
      updateSelectedCount();
      await fetchRefreshRunData();
      await fetchReconciliationReport();
    } catch (e) {
      alert("Crawl error: " + e.message);
    } finally {
      btn.disabled = false;
      btn.innerText = "🕷️ Crawl Selected";
    }
  });

  // Human Approve Selected button
  document.getElementById("btn-approve-selected").addEventListener("click", async () => {
    if (selectedUrls.size === 0) {
      alert("Please select URLs to approve.");
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/api/v1/urls/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ urls: Array.from(selectedUrls), approved: true })
      });
      const data = await res.json();
      alert(`✅ ${data.message}`);
      selectedUrls.clear();
      updateSelectedCount();
      await fetchRefreshRunData();
      await fetchReconciliationReport();
    } catch (e) {
      alert("Approval error: " + e.message);
    }
  });
}

async function fetchRefreshRunData() {
  try {
    const queryParam = activeDashboardId ? `?dash_id=${encodeURIComponent(activeDashboardId)}` : "";
    const res = await fetch(`${API_BASE}/api/v1/refresh-run${queryParam}`);
    const data = await res.json();

    document.getElementById("rr-first-fetch").innerText = data.first_fetch_datetime;
    document.getElementById("rr-last-fetch").innerText = data.last_fetch_datetime;
    document.getElementById("rr-latency").innerText = `${data.duration_ms} ms`;
    document.getElementById("rr-total-bottom").innerText = `${data.total_fetched_urls} URLs Total`;

    currentInventoryUrls = data.urls || [];
    updateFilterCounts();
    renderUrlsTable();
  } catch (e) {
    console.error("Refresh run fetch error:", e);
  }
}

function updateFilterCounts() {
  const all = currentInventoryUrls.length;
  const succ = currentInventoryUrls.filter(u => u.http_code === 200 && !u.quarantine_level && u.is_indexed).length;
  const pend = currentInventoryUrls.filter(u => u.status.includes("Pending") || (!u.is_indexed && !u.quarantine_level && !u.status.includes("Skipped"))).length;
  const skip = currentInventoryUrls.filter(u => u.status.includes("Skipped")).length;
  const quar = currentInventoryUrls.filter(u => u.quarantine_level || u.status.includes("Quarantine")).length;

  document.getElementById("cnt-all").innerText = all;
  document.getElementById("cnt-succ").innerText = succ;
  document.getElementById("cnt-pend").innerText = pend;
  document.getElementById("cnt-skip").innerText = skip;
  document.getElementById("cnt-quar").innerText = quar;

  const urlsCountBadge = document.getElementById("urls-count");
  if (urlsCountBadge) urlsCountBadge.innerText = all;
}

function getFilteredUrls() {
  return currentInventoryUrls.filter(item => {
    if (currentFilter === "all") return true;
    if (currentFilter === "successful") return item.http_code === 200 && !item.quarantine_level && item.is_indexed;
    if (currentFilter === "pending") return item.status.includes("Pending") || (!item.is_indexed && !item.quarantine_level && !item.status.includes("Skipped"));
    if (currentFilter === "skipped") return item.status.includes("Skipped");
    if (currentFilter === "quarantined") return item.quarantine_level !== null || item.status.includes("Quarantine");
    return true;
  });
}

function updateSelectedCount() {
  document.getElementById("selected-urls-badge").innerText = `${selectedUrls.size} selected`;
}

function renderUrlsTable() {
  const container = document.getElementById("refresh-urls-list");
  const urls = getFilteredUrls();

  if (!urls.length) {
    container.innerHTML = `<p class="empty-state">No URLs match the selected filter.</p>`;
    return;
  }

  container.innerHTML = urls.map(u => {
    const isSelected = selectedUrls.has(u.url);
    let statusBadge = `<span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">200 OK (Indexed)</span>`;
    if (u.quarantine_level) {
      statusBadge = `<span class="badge" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e;">${u.quarantine_level}</span>`;
    } else if (u.status.includes("Pending")) {
      statusBadge = `<span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24;">Pending Crawl</span>`;
    } else if (u.status.includes("Skipped")) {
      statusBadge = `<span class="badge" style="background: rgba(148, 163, 184, 0.2); color: #cbd5e1;">Skipped (Duplicate)</span>`;
    }

    const isDup = u.is_duplicate_across_sitemaps || (u.referencing_sitemaps && u.referencing_sitemaps.length > 1);
    const dupBadge = isDup
      ? `<span class="badge" style="background: rgba(168, 85, 247, 0.2); color: #c084fc;">Multi-Sitemap Duplicate (${u.referencing_sitemaps ? u.referencing_sitemaps.length : 2} Refs)</span>`
      : '';
    const redirBadge = u.redirect_target
      ? `<span class="badge" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24;">301 Redirect Target Followed</span>`
      : '';

    return `
      <div class="url-card" style="background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem;">
          <div style="display: flex; align-items: flex-start; gap: 0.6rem;">
            <input type="checkbox" class="url-chk" data-url="${u.url}" ${isSelected ? 'checked' : ''} style="margin-top: 0.25rem;" />
            <div>
              <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
                <strong style="font-size: 0.82rem; color: #f8fafc;">${u.title}</strong>
                <span class="badge" style="font-size: 0.65rem;">${u.category}</span>
                ${statusBadge}
                ${dupBadge}
                ${redirBadge}
              </div>
              <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #38bdf8; margin: 0.2rem 0;">
                <a href="${u.url}" target="_blank" style="color: #38bdf8; text-decoration: none;">${u.url}</a>
              </div>
              <p style="font-size: 0.72rem; color: #94a3b8; margin: 0.2rem 0;">${u.summary}</p>
              ${u.parent_sitemap ? `<div style="font-size: 0.68rem; color: #64748b; margin-top: 0.15rem;">📍 Discovered from Sitemap: <span style="font-family: var(--font-mono); color: #93c5fd;">${u.parent_sitemap}</span></div>` : ''}
            </div>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="inspectUrl('${encodeURIComponent(u.url)}')">Inspect</button>
        </div>
      </div>
    `;
  }).join("");

  // Attach checkbox listeners
  container.querySelectorAll(".url-chk").forEach(chk => {
    chk.addEventListener("change", (e) => {
      const url = e.target.getAttribute("data-url");
      if (e.target.checked) selectedUrls.add(url);
      else selectedUrls.delete(url);
      updateSelectedCount();
    });
  });
}

window.inspectUrl = async function(encodedUrl) {
  const url = decodeURIComponent(encodedUrl);
  try {
    const res = await fetch(`${API_BASE}/api/v1/urls/inspect?url=${encodeURIComponent(url)}`);
    const d = await res.json();
    const modal = document.getElementById("modal-inspect-url");
    document.getElementById("inspect-modal-title").innerText = `🔍 Inspection: ${d.title}`;

    const refSitemapsHtml = (d.referencing_sitemaps && d.referencing_sitemaps.length > 0)
      ? d.referencing_sitemaps.map(s => `<div>↳ <span style="font-family: var(--font-mono); color: #c084fc;">${s}</span></div>`).join("")
      : `<div>↳ <span style="font-family: var(--font-mono); color: #cbd5e1;">${d.parent_sitemap || 'Primary Sitemap'}</span></div>`;

    const redirectHtml = d.redirect_target
      ? `<div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); padding: 0.4rem 0.6rem; border-radius: 6px; margin-top: 0.4rem;">
           <strong>301 Redirect Target Destination:</strong>
           <div style="font-family: var(--font-mono); color: #fde68a;">${d.redirect_target} (Re-indexed Active)</div>
         </div>`
      : '';

    const historyHtml = (d.change_history && d.change_history.length > 0)
      ? d.change_history.map(h => `
          <div style="font-size: 0.7rem; color: #94a3b8; border-left: 2px solid #38bdf8; padding-left: 0.5rem; margin-top: 0.3rem;">
            <strong style="color: #cbd5e1;">[${h.timestamp}] ${h.change_type}</strong>: ${h.summary}
          </div>
        `).join("")
      : `<div style="font-size: 0.7rem; color: #64748b;">No content modifications recorded.</div>`;

    document.getElementById("inspect-modal-body").innerHTML = `
      <div><strong>Full Target URL:</strong> <a href="${d.url}" target="_blank" style="color: #38bdf8; font-family: var(--font-mono);">${d.url}</a></div>
      ${redirectHtml}
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">
        <div><strong>HTTP Response Code:</strong> ${d.http_code}</div>
        <div><strong>Status:</strong> ${d.status}</div>
        <div><strong>Category / Folder:</strong> ${d.category} / ${d.folder || 'N/A'}</div>
        <div><strong>Consecutive Failures:</strong> ${d.consecutive_failures}</div>
        <div><strong>Quarantine Level:</strong> ${d.quarantine_level || 'None (Active)'}</div>
        <div><strong>Successfully Indexed:</strong> ${d.is_indexed ? '✅ YES' : '❌ NO'}</div>
        <div><strong>Human Approved:</strong> ${d.approved_by_human ? '✅ YES' : '❌ NO'}</div>
        <div><strong>Content SHA-256 Hash:</strong> <span style="font-family: var(--font-mono);">${d.hash ? d.hash.slice(0, 14) + '...' : 'N/A'}</span></div>
        <div><strong>Discovered At:</strong> ${d.discovered_at || 'N/A'}</div>
        <div><strong>Last Checked:</strong> ${d.last_checked || 'N/A'}</div>
      </div>
      <div style="margin-top: 0.5rem; background: rgba(0,0,0,0.25); padding: 0.5rem; border-radius: 6px;">
        <strong>Multi-Sitemap References:</strong>
        ${refSitemapsHtml}
      </div>
      <div style="margin-top: 0.5rem; background: rgba(0,0,0,0.25); padding: 0.5rem; border-radius: 6px;">
        <strong>Content Change History:</strong>
        ${historyHtml}
      </div>
      <div style="margin-top: 0.5rem;">
        <strong>Content Summary / Preview:</strong>
        <p style="background: rgba(0,0,0,0.3); padding: 0.6rem; border-radius: 6px; color: #cbd5e1; margin-top: 0.3rem;">${d.summary}</p>
      </div>
    `;
    modal.style.display = "flex";
  } catch (err) {
    alert("Inspect error: " + err.message);
  }
};

// =====================================================================
// 7. Reconciliation Report & Health Settings (Requirements 3 & 4)
// =====================================================================
function setupReconciliationAndHealth() {
  document.getElementById("btn-save-health-settings").addEventListener("click", async () => {
    const threshold = parseInt(document.getElementById("input-health-threshold-x").value, 10);
    const rule = document.getElementById("select-quarantine-rule").value;

    try {
      const res = await fetch(`${API_BASE}/api/v1/settings/health?dash_id=${activeDashboardId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consecutive_failure_threshold: threshold, quarantine_action_rule: rule })
      });
      const data = await res.json();
      alert(`✅ ${data.message}`);
    } catch (e) {
      alert("Settings save error: " + e.message);
    }
  });

  document.getElementById("btn-run-health-check").addEventListener("click", async () => {
    const btn = document.getElementById("btn-run-health-check");
    btn.disabled = true;
    btn.innerText = "Running Check...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/health-check/run?dash_id=${activeDashboardId}`, { method: "POST" });
      const data = await res.json();
      alert(`Health check completed! Quarantined 404s: ${data.quarantined_404_purged.length}, Quarantined 301s: ${data.quarantined_301_redirect.length}, Recovered: ${data.recovered_urls.length}`);
      await fetchReconciliationReport();
      await fetchRefreshRunData();
    } catch (e) {
      alert("Health check error: " + e.message);
    } finally {
      btn.disabled = false;
      btn.innerText = "⚡ Run Health Check & Apply Rules";
    }
  });
}

async function fetchReconciliationReport() {
  try {
    const queryParam = activeDashboardId ? `?dash_id=${encodeURIComponent(activeDashboardId)}` : "";
    const res = await fetch(`${API_BASE}/api/v1/urls/reconciliation-report${queryParam}`);
    const r = await res.json();

    document.getElementById("rec-disc").innerText = r.discovered_count;
    document.getElementById("rec-indx").innerText = r.indexed_count;
    document.getElementById("rec-pend").innerText = r.pending_count;
    document.getElementById("rec-skip").innerText = r.skipped_count;
    document.getElementById("rec-fail").innerText = r.failed_count;
    document.getElementById("rec-quar").innerText = r.quarantined_count;

    const badge = document.getElementById("recon-badge");
    if (r.reconciliation_valid) {
      badge.innerText = "✅ AUDIT PASSED";
      badge.style.color = "#34d399";
    } else {
      badge.innerText = "❌ AUDIT FAILED";
      badge.style.color = "#f43f5e";
    }

    // Pending warnings container
    const warnContainer = document.getElementById("pending-warnings-container");
    const pendingUrls = currentInventoryUrls.filter(u => u.consecutive_failures > 0);
    if (!pendingUrls.length) {
      warnContainer.innerHTML = `<div style="color: #94a3b8;">No pending URLs currently at risk of quarantine. All active URLs healthy!</div>`;
    } else {
      warnContainer.innerHTML = pendingUrls.map(u => `
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); padding: 0.5rem; border-radius: 6px;">
          <div><strong>URL:</strong> <span style="font-family: var(--font-mono); color: #fbbf24;">${u.url}</span></div>
          <div>Consecutive Failed Fetches: <strong>${u.consecutive_failures}</strong> (Action threshold: 3)</div>
        </div>
      `).join("");
    }
  } catch (e) {
    console.error("Reconciliation report error:", e);
  }
}

// =====================================================================
// 8. Chat & Self-Directed Prompt Inspector (Requirement 2 & 7)
// =====================================================================
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

window.askQuestion = async function(questionText) {
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

    appendMessage("bot", data.answer, data.can_answer, data.escalation_id, data.thinking_trace, data.prompt_used, data.retrieval_chunks);
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
};

function appendMessage(sender, text, canAnswer = true, escId = null, thinkingTrace = null, promptUsed = null, retrievalChunks = null) {
  const history = document.getElementById("chat-history");
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}-message`;

  const author = document.createElement("div");
  author.className = "msg-author";
  author.innerText = sender === "user" ? "You" : "Knowledge Brain (Self-Directed Prompt Harness Active)";

  const body = document.createElement("div");
  body.className = "msg-body";
  body.innerText = text;

  msgDiv.appendChild(author);
  msgDiv.appendChild(body);

  if (sender === "bot" && (thinkingTrace || promptUsed)) {
    const details = document.createElement("details");
    details.className = "thinking-details";
    details.innerHTML = `
      <summary>🧠 AI Thinking Process (6 Steps) & Prompt Harness Inspector</summary>
      <div class="thinking-box">
        ${promptUsed ? `<h4>Target LLM Prompt (Self-Directed Harness):</h4><pre><code>${escapeHtml(promptUsed)}</code></pre>` : ''}
        ${thinkingTrace ? `<h4>Thinking Trace:</h4><pre><code>${escapeHtml(thinkingTrace)}</code></pre>` : ''}
      </div>
    `;
    msgDiv.appendChild(details);
  }

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

  // Citations
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

  // Screenshots
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

// =====================================================================
// 9. Escalations & Sync
// =====================================================================
async function fetchEscalations() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/escalations?status=PENDING`);
    const escalations = await res.json();
    const countEl = document.getElementById("esc-count");
    if (countEl) countEl.innerText = escalations.length;

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
    console.error("Fetch escalations failed:", err);
  }
}

window.submitEscalation = async function(e, escId) {
  e.preventDefault();
  const textarea = document.getElementById(`esc-ans-${escId}`);
  const answer = textarea.value.trim();
  if (!answer) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/escalations/${escId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expert_answer: answer, resolved_by: "Suresh Gopi (Lead AI Consultant)" })
    });
    if (res.ok) {
      const card = document.getElementById(`esc-card-${escId}`);
      if (card) {
        card.innerHTML = `<div style="color: #10b981; font-weight: 600;">✅ Resolved & Learned into Knowledge Brain memory!</div>`;
        setTimeout(() => fetchEscalations(), 1500);
      }
    }
  } catch (err) {
    alert("Failed to submit resolution: " + err.message);
  }
};

function setupSync() {
  const syncBtn = document.getElementById("btn-sync");
  syncBtn.addEventListener("click", async () => {
    syncBtn.disabled = true;
    syncBtn.innerText = "Syncing...";
    try {
      const res = await fetch(`${API_BASE}/api/v1/sync?max_scrapes=5`, { method: "POST" });
      const data = await res.json();
      alert(`Sync completed! Added: ${data.added_count}, Updated: ${data.updated_count}, Total Articles: ${data.total_articles}`);
      loadDashboardData();
    } catch (e) {
      alert("Sync failed: " + e.message);
    } finally {
      syncBtn.disabled = false;
      syncBtn.innerText = "⚡ Run Sync";
    }
  });
}

function setupModals() {
  document.getElementById("btn-close-inspect-modal").addEventListener("click", () => {
    document.getElementById("modal-inspect-url").style.display = "none";
  });
}

// =====================================================================
// 8. Pre-Flight Sitemap Inspection & Confirmation (Requirement 3)
// =====================================================================
function setupPreFlightAndConfirmation() {
  const openBtn = document.getElementById("btn-preflight-analyze");
  const modal = document.getElementById("modal-preflight-summary");
  const closeBtn = document.getElementById("btn-close-preflight-modal");
  const cancelBtn = document.getElementById("btn-cancel-preflight");
  const confirmBtn = document.getElementById("btn-confirm-ingestion");

  const hideModal = () => { modal.style.display = "none"; };
  if (closeBtn) closeBtn.addEventListener("click", hideModal);
  if (cancelBtn) cancelBtn.addEventListener("click", hideModal);

  if (openBtn) {
    openBtn.addEventListener("click", async () => {
      openBtn.disabled = true;
      openBtn.innerText = "Analyzing...";
      try {
        const res = await fetch(`${API_BASE}/api/v1/sitemaps/analyze`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dashboard_id: activeDashboardId })
        });
        const d = await res.json();

        document.getElementById("pf-total-sitemaps").innerText = d.total_sitemaps_found;
        document.getElementById("pf-total-urls").innerText = d.total_urls_found;
        document.getElementById("pf-first-url").innerText = d.first_url || "N/A";
        document.getElementById("pf-last-url").innerText = d.last_url || "N/A";
        document.getElementById("pf-expected-time").innerText = d.expected_completion_time_formatted;

        const tbody = document.getElementById("pf-nested-table-body");
        tbody.innerHTML = (d.nested_sitemaps || []).map(ns => `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
            <td style="padding: 0.4rem; font-family: var(--font-mono); color: #38bdf8;">${ns.sitemap_url}</td>
            <td style="padding: 0.4rem;"><span class="badge" style="font-size: 0.65rem;">${ns.is_index ? 'Index' : 'Part'}</span></td>
            <td style="padding: 0.4rem; font-weight: 700; color: #f8fafc;">${ns.url_count}</td>
            <td style="padding: 0.4rem; color: #34d399;">${ns.status}</td>
          </tr>
        `).join("");

        // Reset progress bar
        document.getElementById("pf-progress-container").style.display = "none";
        document.getElementById("pf-progress-bar").style.width = "0%";
        document.getElementById("pf-progress-pct").innerText = "0%";
        confirmBtn.disabled = false;
        confirmBtn.innerText = "✅ Confirm & Start Knowledge Base Creation";

        modal.style.display = "flex";
      } catch (e) {
        alert("Pre-flight analysis error: " + e.message);
      } finally {
        openBtn.disabled = false;
        openBtn.innerText = "🔍 Inspect & Pre-Analyze Sitemaps";
      }
    });
  }

  if (confirmBtn) {
    confirmBtn.addEventListener("click", async () => {
      confirmBtn.disabled = true;
      confirmBtn.innerText = "Processing Ingestion...";
      const progressContainer = document.getElementById("pf-progress-container");
      const progressBar = document.getElementById("pf-progress-bar");
      const progressPct = document.getElementById("pf-progress-pct");
      const progressDetail = document.getElementById("pf-progress-detail");

      progressContainer.style.display = "block";
      progressBar.style.width = "30%";
      progressPct.innerText = "30%";
      progressDetail.innerText = "Connecting to sitemaps and discovering candidate URLs...";

      try {
        setTimeout(() => {
          progressBar.style.width = "70%";
          progressPct.innerText = "70%";
          progressDetail.innerText = "Extracting multimodal screenshots and building hybrid BM25 + Vector chunks...";
        }, 400);

        const res = await fetch(`${API_BASE}/api/v1/sitemaps/confirm-ingest`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dashboard_id: activeDashboardId, confirmed: true })
        });
        const data = await res.json();

        progressBar.style.width = "100%";
        progressPct.innerText = "100%";
        progressDetail.innerText = `Ingestion complete! ${data.pages_indexed} indexed in ${data.elapsed_seconds}s.`;

        setTimeout(() => {
          hideModal();
          alert(`🎉 Ingestion Confirmed & Completed!\n${data.message}`);
          loadDashboardData();
        }, 800);
      } catch (err) {
        alert("Ingestion error: " + err.message);
        confirmBtn.disabled = false;
        confirmBtn.innerText = "Retry Ingestion";
      }
    });
  }
}

// =====================================================================
// 9. Recheck Schedules & Retention Settings
// =====================================================================
function setupScheduleAndRetention() {
  const saveScheduleBtn = document.getElementById("btn-save-schedule");
  const saveRetentionBtn = document.getElementById("btn-save-retention");
  const scheduleSelect = document.getElementById("select-recheck-schedule");
  const retentionSelect = document.getElementById("select-retention-rule");

  if (saveScheduleBtn) {
    saveScheduleBtn.addEventListener("click", async () => {
      const schedule = scheduleSelect.value;
      try {
        const res = await fetch(`${API_BASE}/api/v1/settings/schedule`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dashboard_id: activeDashboardId, schedule })
        });
        const data = await res.json();
        alert(`✅ ${data.message}`);
      } catch (e) {
        alert("Error saving schedule: " + e.message);
      }
    });
  }

  if (saveRetentionBtn) {
    saveRetentionBtn.addEventListener("click", async () => {
      const rule = retentionSelect.value;
      try {
        const res = await fetch(`${API_BASE}/api/v1/settings/retention`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dashboard_id: activeDashboardId, retention_rule: rule })
        });
        const data = await res.json();
        alert(`✅ ${data.message}`);
        fetchArchivedUrls();
      } catch (e) {
        alert("Error saving retention rule: " + e.message);
      }
    });
  }
}

// =====================================================================
// 10. Archived Safe Store (Never Permanently Deleted!)
// =====================================================================
function setupArchivedSafeStore() {
  // Event listeners if any
}

async function fetchArchivedUrls() {
  try {
    const res = await fetch(`${API_BASE}/api/v1/archived-urls`);
    const data = await res.json();

    const countBadge = document.getElementById("archived-count");
    if (countBadge) countBadge.innerText = data.total_archived;

    const policyLabel = document.getElementById("archived-policy-label");
    if (policyLabel) policyLabel.innerText = data.retention_policy_active;

    const container = document.getElementById("archived-urls-list");
    if (!container) return;

    if (!data.archived_urls || data.archived_urls.length === 0) {
      container.innerHTML = `<p class="empty-state">No archived URLs in the safe repository. Active knowledge base is 100% clean.</p>`;
      return;
    }

    container.innerHTML = data.archived_urls.map(item => `
      <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
          <div>
            <div style="display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap;">
              <strong style="font-size: 0.82rem; color: #f8fafc;">${item.title}</strong>
              <span class="badge" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e; font-size: 0.65rem;">Archived Safe Store</span>
              <span class="badge" style="font-size: 0.65rem;">${item.category}</span>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.72rem; color: #f87171; margin: 0.2rem 0;">
              <a href="${item.url}" target="_blank" style="color: #f87171; text-decoration: none;">${item.url}</a>
            </div>
            <div style="font-size: 0.72rem; color: #cbd5e1; margin: 0.2rem 0;">
              📌 <strong>Reason:</strong> ${item.archived_reason} | <strong>Checks Missed:</strong> ${item.consecutive_checks_missed} | <strong>Archived:</strong> ${item.archived_at}
            </div>
            <p style="font-size: 0.7rem; color: #94a3b8; margin: 0.2rem 0;">${item.summary}</p>
          </div>
          <button class="btn btn-primary btn-sm" onclick="restoreArchivedUrl('${encodeURIComponent(item.url)}')">↩️ Restore to Active KB</button>
        </div>
      </div>
    `).join("");
  } catch (e) {
    console.error("Error fetching archived URLs:", e);
  }
}

window.restoreArchivedUrl = async function(encodedUrl) {
  const url = decodeURIComponent(encodedUrl);
  try {
    const res = await fetch(`${API_BASE}/api/v1/archived-urls/restore`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls: [url] })
    });
    const data = await res.json();
    alert(`✅ ${data.message}`);
    await fetchArchivedUrls();
    await fetchRefreshRunData();
    await fetchReconciliationReport();
  } catch (e) {
    alert("Restore error: " + e.message);
  }
};

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
