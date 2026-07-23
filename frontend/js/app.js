// CampusConnect Shared Client Library
const API_BASE = "/api";

// 1. JWT & Session Management
function getToken() {
  return localStorage.getItem("cc_token");
}

function getRole() {
  return localStorage.getItem("cc_role");
}

function getUsername() {
  return localStorage.getItem("cc_username");
}

function setSession(token, role, username) {
  localStorage.setItem("cc_token", token);
  localStorage.setItem("cc_role", role);
  localStorage.setItem("cc_username", username);
}

function clearSession() {
  localStorage.removeItem("cc_token");
  localStorage.removeItem("cc_role");
  localStorage.removeItem("cc_username");
}

function isLoggedIn() {
  return !!getToken();
}

// 2. Fetch Wrapper with Loader & JWT
async function apiCall(endpoint, options = {}) {
  showLoader(true);
  const token = getToken();
  
  options.headers = options.headers || {};
  if (token) {
    options.headers["Authorization"] = `Bearer ${token}`;
  }
  
  // Auto JSON Content-Type if not Form Data (multipart/form-data doesn't want manual Content-Type header)
  if (options.body && !(options.body instanceof FormData) && typeof options.body === "object") {
    options.body = JSON.stringify(options.body);
    options.headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    
    if (response.status === 401) {
      clearSession();
      showToast("Session expired. Please log in again.", "danger");
      setTimeout(() => { window.location.href = "/login.html"; }, 1500);
      throw new Error("Unauthorized");
    }
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }
    
    // Check if output is a blob (e.g. PDF streaming)
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/pdf")) {
      return await response.blob();
    }
    
    return await response.json();
  } catch (error) {
    console.error("API Call error:", error.message);
    throw error;
  } finally {
    showLoader(false);
  }
}

// 3. UI Helpers: Loader
function showLoader(show) {
  let loader = document.getElementById("cc-loader");
  if (!loader) {
    loader = document.createElement("div");
    loader.id = "cc-loader";
    loader.className = "loader-overlay d-none";
    loader.innerHTML = `
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    `;
    document.body.appendChild(loader);
  }
  
  if (show) {
    loader.classList.remove("d-none");
  } else {
    loader.classList.add("d-none");
  }
}

// 4. UI Helpers: Toast Notification
function showToast(message, type = "info") {
  let toastContainer = document.getElementById("cc-toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "cc-toast-container";
    toastContainer.className = "toast-container-cc";
    document.body.appendChild(toastContainer);
  }
  
  const toastId = "toast_" + Date.now();
  const bgClass = `bg-${type}`;
  const textClass = type === "light" ? "text-dark" : "text-white";
  
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} ${textClass} border-0 shadow-lg animate-fade-in" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="4000">
      <div class="d-flex">
        <div class="toast-body font-weight-bold">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  toastContainer.insertAdjacentHTML("beforeend", toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const bsToast = new bootstrap.Toast(toastElement);
  bsToast.show();
  
  toastElement.addEventListener("hidden.bs.toast", () => {
    toastElement.remove();
  });
}

// 5. Dark Mode Logic
function initTheme() {
  const savedTheme = localStorage.getItem("cc_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("cc_theme", newTheme);
  
  // Update icon if present
  const icon = document.querySelector(".theme-switch i");
  if (icon) {
    icon.className = newTheme === "dark" ? "bi bi-sun-fill text-warning" : "bi bi-moon-fill";
  }
}

// 6. Navigation Bar Injection
function renderNavbar() {
  const container = document.getElementById("cc-navbar-container");
  if (!container) return;
  
  const logged = isLoggedIn();
  const role = getRole();
  const username = getUsername();
  const currentTheme = localStorage.getItem("cc_theme") || "light";
  const themeIcon = currentTheme === "dark" ? "bi-sun-fill text-warning" : "bi-moon-fill";
  
  let navItems = "";
  let authArea = "";
  
  if (logged) {
    navItems = `
      <li class="nav-item"><a class="nav-link" href="/dashboard.html"><i class="bi bi-speedometer2 me-1"></i>Dashboard</a></li>
      <li class="nav-item"><a class="nav-link" href="/experience.html"><i class="bi bi-chat-left-quote me-1"></i>Experiences</a></li>
      <li class="nav-item"><a class="nav-link" href="/companies.html"><i class="bi bi-building me-1"></i>Companies</a></li>
      <li class="nav-item"><a class="nav-link" href="/questions.html"><i class="bi bi-question-circle me-1"></i>Questions</a></li>
      <li class="nav-item"><a class="nav-link" href="/roadmap.html"><i class="bi bi-map me-1"></i>Roadmaps</a></li>
    `;
    
    if (role === "admin") {
      navItems += `<li class="nav-item"><a class="nav-link text-danger fw-bold" href="/admin.html"><i class="bi bi-shield-lock me-1"></i>Admin</a></li>`;
    }
    
    authArea = `
      <div class="d-flex align-items-center gap-3">
        <!-- Notification Dropdown -->
        <div class="dropdown">
          <a href="#" class="position-relative text-decoration-none text-reset" id="notifDropdown" data-bs-toggle="dropdown" aria-expanded="false" onclick="fetchNotifications()">
            <i class="bi bi-bell-fill fs-5"></i>
            <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger d-none" id="notif-count-badge">0</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end shadow-lg p-2" aria-labelledby="notifDropdown" id="notif-list-container" style="width: 320px; max-height: 400px; overflow-y: auto;">
            <li class="text-center py-3 text-muted">No notifications</li>
          </ul>
        </div>
        
        <!-- Profile Dropdown -->
        <div class="dropdown">
          <a href="#" class="d-flex align-items-center gap-2 text-decoration-none dropdown-toggle text-reset" id="profileDropdown" data-bs-toggle="dropdown" aria-expanded="false">
            <img src="/images/default-avatar.png" onerror="this.src='https://api.dicebear.com/7.x/adventurer/svg?seed=${username}'" class="profile-avatar-nav" alt="Profile">
            <span class="d-none d-md-inline fw-semibold">${username}</span>
          </a>
          <ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="profileDropdown">
            <li><a class="dropdown-menu-item dropdown-item" href="/profile.html?username=${username}"><i class="bi bi-person me-2"></i>My Profile</a></li>
            <li><a class="dropdown-menu-item dropdown-item" href="/profile.html?username=${username}#saved"><i class="bi bi-bookmark me-2"></i>Saved Posts</a></li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-menu-item dropdown-item text-danger" href="#" onclick="handleLogout(event)"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
          </ul>
        </div>
      </div>
    `;
  } else {
    navItems = `
      <li class="nav-item"><a class="nav-link" href="/index.html">Home</a></li>
      <li class="nav-item"><a class="nav-link" href="/experience.html">Experiences</a></li>
      <li class="nav-item"><a class="nav-link" href="/companies.html">Companies</a></li>
    `;
    authArea = `
      <div class="d-flex gap-2">
        <a class="btn btn-outline-premium" href="/login.html">Login</a>
        <a class="btn btn-premium" href="/register.html">Sign Up</a>
      </div>
    `;
  }
  
  container.innerHTML = `
    <nav class="navbar navbar-expand-lg navbar-cc fixed-top shadow-sm">
      <div class="container">
        <a class="navbar-brand fw-bold fs-4 d-flex align-items-center gap-2" href="/index.html">
          <i class="bi bi-link-45deg text-gradient fs-3"></i>
          <span>Campus<span class="text-gradient">Connect</span></span>
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent" aria-controls="navContent" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navContent">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0 gap-1 ms-lg-4">
            ${navItems}
          </ul>
          <div class="d-flex align-items-center gap-3">
            <div class="theme-switch" onclick="toggleTheme()">
              <i class="bi ${themeIcon}"></i>
            </div>
            ${authArea}
          </div>
        </div>
      </div>
    </nav>
  `;
  
  // Highlight active link
  const path = window.location.pathname;
  const links = document.querySelectorAll(".navbar-nav .nav-link");
  links.forEach(link => {
    const href = link.getAttribute("href");
    if (path.endsWith(href) || (path === "/" && href === "/index.html")) {
      link.classList.add("active");
    }
  });

  // Start notification poller
  if (logged) {
    updateUnreadNotificationsCount();
  }
}

// 7. Footer Injection
function renderFooter() {
  const container = document.getElementById("cc-footer-container");
  if (!container) return;
  
  container.innerHTML = `
    <footer class="py-5 mt-5 border-top" style="background-color: var(--bg-secondary); border-color: var(--border-color) !important;">
      <div class="container">
        <div class="row g-4">
          <div class="col-md-4">
            <h5 class="fw-bold mb-3 d-flex align-items-center gap-2">
              <i class="bi bi-link-45deg text-gradient fs-4"></i>
              <span>Campus<span class="text-gradient">Connect</span></span>
            </h5>
            <p class="text-muted small">A peer-to-peer placement preparation portal designed to help final-year students learn from seniors' interviews, strategies, and roadmaps.</p>
          </div>
          <div class="col-md-2 offset-md-1">
            <h6 class="fw-bold mb-3">Links</h6>
            <ul class="list-unstyled d-flex flex-column gap-2 small">
              <li><a href="/experience.html" class="text-muted text-decoration-none">Placement Experiences</a></li>
              <li><a href="/companies.html" class="text-muted text-decoration-none">Company Profiles</a></li>
              <li><a href="/questions.html" class="text-muted text-decoration-none">Interview Questions</a></li>
              <li><a href="/roadmap.html" class="text-muted text-decoration-none">Learning Roadmaps</a></li>
            </ul>
          </div>
          <div class="col-md-2">
            <h6 class="fw-bold mb-3">Support</h6>
            <ul class="list-unstyled d-flex flex-column gap-2 small">
              <li><a href="/faq.html" class="text-muted text-decoration-none">FAQ</a></li>
              <li><a href="/terms.html" class="text-muted text-decoration-none">Terms of Use</a></li>
              <li><a href="/privacy.html" class="text-muted text-decoration-none">Privacy Policy</a></li>
            </ul>
          </div>
          <div class="col-md-3">
            <h6 class="fw-bold mb-3">Major MCA Project</h6>
            <p class="text-muted small mb-0">Built as a final-year Major Project using Python, FastAPI, and MySQL.</p>
            <p class="text-muted small mt-2">© 2026 CampusConnect. All Rights Reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  `;
}

// 8. Notifications Operations
async function updateUnreadNotificationsCount() {
  try {
    const res = await apiCall("/notifications/unread-count");
    const badge = document.getElementById("notif-count-badge");
    if (badge) {
      if (res.unread_count > 0) {
        badge.innerText = res.unread_count;
        badge.classList.remove("d-none");
      } else {
        badge.classList.add("d-none");
      }
    }
  } catch (err) {
    console.error(err);
  }
}

async function fetchNotifications() {
  const container = document.getElementById("notif-list-container");
  if (!container) return;
  
  try {
    const notifs = await apiCall("/notifications/");
    if (notifs.length === 0) {
      container.innerHTML = `<li class="text-center py-3 text-muted">No notifications</li>`;
      return;
    }
    
    let html = `
      <div class="d-flex justify-content-between align-items-center px-2 py-1 mb-2 border-bottom">
        <span class="fw-semibold small">Notifications</span>
        <button class="btn btn-link btn-sm p-0 text-decoration-none small" onclick="markAllNotificationsAsRead(event)">Mark all read</button>
      </div>
    `;
    
    notifs.forEach(n => {
      const readClass = n.is_read ? "" : "fw-bold bg-light-gradient";
      const icon = n.type === "like" ? "bi-heart-fill text-danger" : 
                   n.type === "comment" ? "bi-chat-dots-fill text-primary" : 
                   n.type === "follow" ? "bi-person-plus-fill text-success" : "bi-check-circle-fill text-success";
      
      let link = "#";
      if (n.parent_type === "experience") link = `/experience.html?id=${n.parent_id}`;
      else if (n.parent_type === "question") link = `/questions.html?id=${n.parent_id}`;
      else if (n.parent_type === "roadmap") link = `/roadmap.html?id=${n.parent_id}`;
      else if (n.parent_type === "user") link = `/profile.html?username=${n.actor.username}`;

      html += `
        <li class="p-2 border-bottom ${readClass}" style="font-size: 0.85rem; border-radius: var(--border-radius-sm);">
          <a href="${link}" class="text-decoration-none text-reset d-flex align-items-start gap-2" onclick="readNotification(${n.id})">
            <i class="bi ${icon} mt-0.5"></i>
            <div>
              <div>${n.message}</div>
              <small class="text-muted">${new Date(n.created_at).toLocaleDateString()}</small>
            </div>
          </a>
        </li>
      `;
    });
    
    container.innerHTML = html;
  } catch (err) {
    console.error(err);
  }
}

async function readNotification(id) {
  try {
    await apiCall("/notifications/read", {
      method: "POST",
      body: { notification_id: id }
    });
    updateUnreadNotificationsCount();
  } catch (err) {
    console.error(err);
  }
}

async function markAllNotificationsAsRead(e) {
  e.preventDefault();
  e.stopPropagation();
  try {
    await apiCall("/notifications/read", {
      method: "POST",
      body: {}
    });
    updateUnreadNotificationsCount();
    fetchNotifications();
    showToast("All notifications marked as read.", "success");
  } catch (err) {
    console.error(err);
  }
}

// 9. Logout
function handleLogout(e) {
  if (e) e.preventDefault();
  clearSession();
  showToast("Logged out successfully.", "info");
  setTimeout(() => { window.location.href = "/index.html"; }, 1000);
}

// Bootstrap initialization
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  renderNavbar();
  renderFooter();
});
