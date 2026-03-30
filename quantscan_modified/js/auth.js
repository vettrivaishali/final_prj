function signupUser() {
  const email = document.getElementById("signupEmail").value;
  const password = document.getElementById("signupPassword").value;

  if (!email || !password) {
    document.getElementById("signupError").innerText = "All fields required";
    return;
  }

  localStorage.setItem("userEmail", email);
  localStorage.setItem("userPassword", password);

  alert("Signup successful! Please login.");
  window.location.href = "login.html";
}

function loginUser() {
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  const savedEmail = localStorage.getItem("userEmail");
  const savedPassword = localStorage.getItem("userPassword");

  if (!savedEmail) {
    document.getElementById("loginError").innerText =
      "No account found. Signup to continue.";
    return;
  }

  if (email === savedEmail && password === savedPassword) {
    localStorage.setItem("isLoggedIn", "true");
    localStorage.setItem("username", email.split("@")[0]);

    alert("Successfully logged in!");
    window.location.href = "dashboard.html";
  } else {
    document.getElementById("loginError").innerText =
      "Invalid credentials.";
  }
}
