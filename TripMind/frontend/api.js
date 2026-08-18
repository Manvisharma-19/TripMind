// Use the same origin the page was served from. This means the app works
// unchanged whether you open http://localhost:8000 during development or a
// real https://your-app.onrender.com URL after deploying — no edits needed.
// (If you ever run the frontend separately from the backend, hard-code the
//  backend URL here instead, e.g. "https://your-api.onrender.com".)
const API_URL = window.location.origin;

function getToken() {
  return localStorage.getItem("tripmind_token");
}

function setToken(token) {
  localStorage.setItem("tripmind_token", token);
}

function clearToken() {
  localStorage.removeItem("tripmind_token");
}

function isLoggedIn() {
  return !!getToken();
}

async function apiRequest(path, options) {
  options = options || {};
  const token = getToken();
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    token ? { Authorization: "Bearer " + token } : {},
    options.headers || {}
  );

  const res = await fetch(API_URL + path, Object.assign({}, options, { headers: headers }));

  if (!res.ok) {
    let detail = "Request failed: " + res.status;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch (e) {}
    throw new Error(detail);
  }
  return res.json();
}

const api = {
  register: function (email, password, name) {
    return apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email: email, password: password, name: name }),
    });
  },
  login: function (email, password) {
    return apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: email, password: password }),
    });
  },
  sendMessage: function (message, conversationId) {
    return apiRequest("/chat", {
      method: "POST",
      body: JSON.stringify({ message: message, conversation_id: conversationId }),
    });
  },
  listBookings: function () {
    return apiRequest("/bookings");
  },
  cancelBooking: function (id) {
    return apiRequest("/bookings/" + id + "/cancel", { method: "POST" });
  },
  getStats: function () {
    return apiRequest("/stats");
  },
  me: function () {
    return apiRequest("/auth/me");
  },
  updatePreferences: function (prefs) {
    return apiRequest("/preferences", { method: "PUT", body: JSON.stringify(prefs) });
  },
};

function requireAuth() {
  if (!isLoggedIn()) window.location.href = "login.html";
}

function redirectIfLoggedIn() {
  if (isLoggedIn()) window.location.href = "chat.html";
}
