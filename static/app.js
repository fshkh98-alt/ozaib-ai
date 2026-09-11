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

// حفظ واسترجاع المحادثة من localStorage
function saveMessagesToLocal(messages) {
  localStorage.setItem("cyberguard_messages", JSON.stringify(messages));
}

function getMessagesFromLocal() {
  const saved = localStorage.getItem("cyberguard_messages");
  return saved ? JSON.parse(saved) : [];
}

function addMessage(text, role, save = true) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "bot" ? "AI" : "أنت";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = marked.parse(text);
  wrapper.append(avatar, bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;

  // حفظ الرسالة
  if (save) {
    const messages = getMessagesFromLocal();
    messages.push({ role, text });
    saveMessagesToLocal(messages);
  }
}

// استرجاع المحادثة عند تحميل الصفحة
function loadSavedMessages() {
  const saved = getMessagesFromLocal();
  if (saved.length === 0) {
    // رسالة الترحيب
    addMessage("**مرحباً 👋**\n\nأنا CyberGuard AI. اسألني عن أي موضوع في الأمن السيبراني وسأشرح لك بطريقة تعليمية مبسطة.", "bot", false);
    return;
  }

  // عرض جميع الرسائل المحفوظة
  saved.forEach(msg => {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${msg.role}`;
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = msg.role === "bot" ? "AI" : "أنت";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = marked.parse(msg.text);
    wrapper.append(avatar, bubble);
    messages.appendChild(wrapper);
  });
  messages.scrollTop = messages.scrollHeight;
}

// تحميل الرسائل المحفوظة عند بدء الصفحة
loadSavedMessages();

async function sendMessage(text) {
  addMessage(text, "user");
  typing.style.display = "flex";
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
    addMessage("**خطأ**\n\nتعذر الحصول على الإجابة: " + err.message, "bot");
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
  localStorage.removeItem("cyberguard_messages");
  messages.innerHTML = "";
  addMessage("**تم مسح المحادثة**\n\nاطرح سؤالك الجديد في الأمن السيبراني.", "bot", false);
});