// DOM Elements
const messagesContainer = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");
const input = document.getElementById("input");
const typingIndicator = document.getElementById("typing");
const clearBtn = document.getElementById("clearBtn");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const mobileToggle = document.getElementById("mobileToggle");

// Session Management
let sessionId = localStorage.getItem("cyberguard_session");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("cyberguard_session", sessionId);
}

// Local Storage Functions
function saveMessagesToLocal(messages) {
  localStorage.setItem("cyberguard_messages", JSON.stringify(messages));
}

function getMessagesFromLocal() {
  const saved = localStorage.getItem("cyberguard_messages");
  return saved ? JSON.parse(saved) : [];
}

// Copy Button Function (always visible)
function createCopyButton(text) {
  const btn = document.createElement("button");
  btn.className = "copy-btn copy-btn-visible";
  btn.innerHTML = "📋";
  btn.title = "نسخ";
  btn.addEventListener("click", async (e) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(text);
      btn.innerHTML = "✓";
      setTimeout(() => btn.innerHTML = "📋", 1500);
    } catch (err) {
      console.error("فشل النسخ:", err);
    }
  });
  return btn;
}

// Click on code to copy
function makeCodeClickable(bubble) {
  bubble.querySelectorAll("code").forEach(code => {
    code.style.cursor = "pointer";
    code.title = "انقر للنسخ";
    
    // Skip if already has click handler
    if (code.dataset.clickCopyAdded) return;
    code.dataset.clickCopyCreated = "true";
    
    code.addEventListener("click", async () => {
      const text = code.textContent;
      try {
        await navigator.clipboard.writeText(text);
        // Show temporary feedback
        code.style.color = "#7ee787";
        setTimeout(() => code.style.color = "", 500);
      } catch (err) {
        console.error("فشل النسخ:", err);
      }
    });
  });
}

// Highlight Code Function
function highlightCode(bubble) {
  bubble.querySelectorAll("pre code").forEach(block => {
    const classes = block.className.split(" ");
    const langClass = classes.find(c => c.startsWith("language-"));
    const lang = langClass ? langClass.replace("language-", "") : '';
    
    if (!lang || !hljs.getLanguage(lang)) {
      block.removeAttribute('class');
      hljs.highlightElement(block);
    } else {
      hljs.highlightElement(block);
    }
  });
}

// Add Message to Chat
function addMessage(text, role, save = true) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;
  
  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "bot" ? "AI" : "أنت";
  
  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.innerHTML = marked.parse(text);
  
  // Highlight code blocks
  highlightCode(bubble);
  
  // Add copy buttons to pre blocks
  bubble.querySelectorAll("pre").forEach(pre => {
    const code = pre.querySelector("code");
    if (code) {
      const btn = createCopyButton(code.textContent);
      pre.style.position = "relative";
      pre.appendChild(btn);
    }
  });
  
  // Make inline code clickable to copy
  makeCodeClickable(bubble);
  
  // Add copy buttons to tables (convert to CSV and copy)
  bubble.querySelectorAll("table").forEach(table => {
    const rows = table.querySelectorAll("tr");
    let csv = "";
    rows.forEach(row => {
      const cells = row.querySelectorAll("th, td");
      const rowData = [];
      cells.forEach(cell => {
        rowData.push(cell.textContent.trim());
      });
      csv += rowData.join(",") + "\n";
    });
    
    const btn = createCopyButton(csv.trim());
    btn.style.position = "absolute";
    btn.style.top = "8px";
    btn.style.left = "8px";
    table.style.position = "relative";
    table.style.paddingTop = "40px";
    table.parentNode.style.position = "relative";
    table.parentNode.insertBefore(btn, table);
  });
  
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(bubble);
  messagesContainer.appendChild(messageDiv);
  
  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  
  // Save message if needed
  if (save) {
    const messages = getMessagesFromLocal();
    messages.push({ role, text });
    saveMessagesToLocal(messages);
  }
}

// Load Saved Messages
function loadSavedMessages() {
  const saved = getMessagesFromLocal();
  
  if (saved.length === 0) {
    // Welcome message
    addMessage("**مرحباً! 👋**\n\nأنا **CyberGuard AI**، مساعدك التعليمي في مجال الأمن السيبراني.\n\nاسألني عن أي موضوع متعلق بـ:\n- أمن الشبكات\n- التشفير\n- البرمجيات الخبيثة\n- SOC و SIEM\n- أمان الويب\n- التحليل الجنائي الرقمي\n\nوسأشرح لك بشكل تعليمي مبسط.", "bot", false);
    return;
  }
  
  // Load all saved messages
  saved.forEach(msg => {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${msg.role}`;
    
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = msg.role === "bot" ? "AI" : "أنت";
    
    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = marked.parse(msg.text);
    
    highlightCode(bubble);
    makeCodeClickable(bubble);
    
    // Add copy buttons to tables
    bubble.querySelectorAll("table").forEach(table => {
      const rows = table.querySelectorAll("tr");
      let csv = "";
      rows.forEach(row => {
        const cells = row.querySelectorAll("th, td");
        const rowData = [];
        cells.forEach(cell => {
          rowData.push(cell.textContent.trim());
        });
        csv += rowData.join(",") + "\n";
      });
      
      const btn = createCopyButton(csv.trim());
      btn.style.position = "absolute";
      btn.style.top = "8px";
      btn.style.left = "8px";
      table.style.position = "relative";
      table.style.paddingTop = "40px";
      table.parentNode.style.position = "relative";
      table.parentNode.insertBefore(btn, table);
    });
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
  });
  
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Send Message to API
async function sendMessage(text) {
  addMessage(text, "user");
  typingIndicator.style.display = "flex";
  input.disabled = true;
  chatForm.querySelector(".send-btn").disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message: text })
    });

    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.detail || "حدث خطأ أثناء الاتصال");
    }
    
    addMessage(data.answer, "bot");
  } catch (err) {
    addMessage(`**خطأ**\n\n${err.message}`, "bot");
  } finally {
    typingIndicator.style.display = "none";
    input.disabled = false;
    chatForm.querySelector(".send-btn").disabled = false;
    input.focus();
  }
}

// Event Listeners
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  await sendMessage(text);
});

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

// Topic Buttons
document.querySelectorAll(".topic-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    input.value = btn.dataset.q;
    input.focus();
    
    // Close sidebar on mobile
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
  });
});

// Clear Chat
clearBtn.addEventListener("click", async () => {
  try {
    await fetch(`/api/chat/${sessionId}`, { method: "DELETE" });
  } catch (e) {
    console.log("فشل مسح المحادثة من السيرفر");
  }
  
  localStorage.removeItem("cyberguard_messages");
  messagesContainer.innerHTML = "";
  addMessage("**تم مسح المحادثة** 🔄\n\nابدأ محادثة جديدة في مجال الأمن السيبراني.", "bot", false);
});

// Mobile Sidebar Toggle
function toggleSidebar() {
  sidebar.classList.toggle("open");
  sidebarOverlay.classList.toggle("active");
}

mobileToggle.addEventListener("click", toggleSidebar);
sidebarOverlay.addEventListener("click", toggleSidebar);

// Initialize
loadSavedMessages();