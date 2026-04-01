(function() {
  const messageUrl = window.CHAT_MESSAGE_URL;
  const csrfToken = window.CSRF_TOKEN;
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  const messages = document.getElementById('chat-messages');

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }
  function send() {
    const text = (input && input.value || '').trim();
    if (!text) return;
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user-message';
    userMsg.innerHTML = '<div class="dumpling-avatar-small user-avatar" aria-hidden="true"><span class="dumpling-emoji">☺</span></div><div class="message-bubble"><p>' + escapeHtml(text) + '</p></div>';
    messages.appendChild(userMsg);
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    fetch(messageUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({ message: text }),
    }).then(function(r) { return r.json(); }).then(function(data) {
      const dumplingMsg = document.createElement('div');
      dumplingMsg.className = 'chat-message dumpling-message';
      dumplingMsg.innerHTML = '<div class="dumpling-avatar-small" aria-hidden="true"><span class="dumpling-emoji">🥟</span></div><div class="message-bubble"><p>' + escapeHtml(data.reply || "I'm here for you!") + '</p></div>';
      messages.appendChild(dumplingMsg);
      messages.scrollTop = messages.scrollHeight;
    });
  }
  sendBtn?.addEventListener('click', send);
  input?.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });
  document.getElementById('report-problem')?.addEventListener('click', function(e) {
    e.preventDefault();
    alert('Thanks for your feedback! You can email us at feedback@cozycorner.app (this is a prototype).');
  });
})();
