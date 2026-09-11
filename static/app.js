const messages = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("input");
const typing = document.getElementById("typing");
const clearBtn = document.getElementById("clearBtn");

let sessionId = localStorage.getItem("cyberguard_session");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("cyberguard_session", sessionId);
}

function addMessage(text, role) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "bot" ? "AI" : "أنت";
  const bubble = document.createElement("div");
  bubble.className = "bubble markdown-body";
  // تحويل Markdown لـ HTML
  bubble.innerHTML = marked.parse(text);
  wrapper.append(avatar, bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text) {
  addMessage(text, "user");
  typing.style.display = "block";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({session_id: sessionId, message: text})
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "حدث خطأ");
    addMessage(data.answer, "bot");
  } catch (err) {
    addMessage("تعذر الحصول على الإجابة: " + err.message, "bot");
  } finally {
    typing.style.display = "none";
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".topics button").forEach(btn => {
  btn.addEventListener("click", () => {
    input.value = btn.dataset.q;
    input.focus();
  });
});

clearBtn.addEventListener("click", async () => {
  await fetch(`/api/chat/${sessionId}`, {method: "DELETE"});
  messages.innerHTML = "";
  addMessage("تم مسح سجل المحادثة. اطرح سؤالك الجديد في الأمن السيبراني.", "bot");
});
