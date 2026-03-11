(function() {
  const entryId = window.JOURNAL_ENTRY_ID;
  const saveUrl = window.JOURNAL_SAVE_URL;
  const csrfToken = window.CSRF_TOKEN;
  const contentEl = document.getElementById('journal-content');
  if (!contentEl) return;

  let saveTimeout;
  function save() {
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(function() {
      fetch(saveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ content: contentEl.innerHTML }),
      });
    }, 500);
  }
  contentEl.addEventListener('input', save);

  document.getElementById('add-text')?.addEventListener('click', function() {
    const div = document.createElement('div');
    div.contentEditable = 'true';
    div.style.cssText = 'padding:0.5rem;margin:0.5rem 0;border-radius:8px;background:rgba(255,255,255,0.7);';
    div.textContent = 'Write here...';
    contentEl.appendChild(div);
  });
  document.getElementById('add-sticker')?.addEventListener('click', function() {
    const span = document.createElement('span');
    span.textContent = '★';
    span.style.cssText = 'font-size:2rem;color:var(--brown);cursor:move;';
    contentEl.appendChild(span);
  });
  document.getElementById('add-mood')?.addEventListener('click', function() {
    const span = document.createElement('span');
    span.textContent = '😊';
    span.style.cssText = 'font-size:2rem;cursor:move;';
    contentEl.appendChild(span);
  });
})();
