/* ===============================
   NAVBAR LOGIN DETECTION
================================ */

document.addEventListener("DOMContentLoaded", () => {
  const navRight = document.getElementById("navRight");
  const loggedIn = localStorage.getItem("loggedIn");
  const username = localStorage.getItem("username");

  if (loggedIn === "true" && username) {
    navRight.innerHTML = `
      <div class="user-menu">
        <span class="user-name">👤 ${username}</span>
        <div class="dropdown">
          <a href="dashboard.html">Dashboard</a>
          <a href="#" onclick="logout()">Logout</a>
        </div>
      </div>
    `;
  } else {
    navRight.innerHTML = `
      <a href="login.html"><button class="login-btn">LOGIN</button></a>
      <a href="signup.html"><button class="signup-btn">GET FREE ACCOUNT</button></a>
    `;
  }

  loadTicker();
});

/* ===============================
   TICKER DATA
================================ */

const tickerData = [
  "NIFTY ▲0.85%",
  "RELIANCE ₹2950 ▲1.2%",
  "TCS ₹3890 ▲0.6%",
  "INFOSYS ₹1671 ▲0.53%",
  "HDFCBANK ₹1420 ▲0.74%",
  "ICICIBANK ₹1351 ▲1.26%",
  "SBIN ₹620 ▲1.1%",
  "ITC ₹462 ▲0.9%",
  "LT ₹3580 ▲0.8%",
  "AXISBANK ₹1120 ▲0.5%",
  "BHARTIARTL ₹1189 ▲1.4%",
  "TATAMOTORS ₹364 ▲1.6%",
  "ADANIENT ₹3120 ▲2.1%",
  "WIPRO ₹510 ▲0.45%",
  "TITAN ₹3280 ▲0.95%"
];

function loadTicker() {
  const ticker = document.getElementById("ticker");

  if (ticker) {
    const content = tickerData.join("  |  ");
    ticker.innerText = content + "  |  " + content; // duplicate for smooth loop
  }
}

/* ===============================
   LOGOUT
================================ */

function logout() {
  localStorage.removeItem("loggedIn");
  localStorage.removeItem("username");
  window.location.reload();
}
