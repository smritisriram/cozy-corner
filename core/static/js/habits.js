(function() {
  const colorInput = document.getElementById('habit-color-input');
  const customColor = document.getElementById('habit-custom-color');
  const options = document.querySelectorAll('.habit-color-picker .color-option');
  if (colorInput && options.length) {
    options.forEach(function(opt) {
      opt.addEventListener('click', function() {
        options.forEach(function(o) { o.classList.remove('selected'); });
        opt.classList.add('selected');
        colorInput.value = opt.dataset.color;
        if (customColor) customColor.value = opt.dataset.color;
      });
    });
  }
  if (customColor && colorInput) {
    customColor.addEventListener('input', function() {
      colorInput.value = customColor.value;
      options.forEach(function(o) { o.classList.remove('selected'); });
    });
  }

  const csrfToken = window.CSRF_TOKEN;
  document.querySelectorAll('.habit-card').forEach(function(card) {
    const form = card.querySelector('.habit-toggle-form');
    const streakEl = card.querySelector('.habit-streak-num');
    const deleteBtn = card.querySelector('.habit-delete');

    function toggleFromCard(e) {
      if (e.target.closest('.habit-delete')) return;
      if (!form) return;
      e.preventDefault();
      const body = new FormData(form);
      fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
        },
        body: body,
      })
        .then(function(r) { return r.json(); })
        .then(function(data) {
          if (!data.ok) return;
          if (streakEl) streakEl.textContent = data.streak;
          card.classList.toggle('habit-done', data.completed_today);
          card.setAttribute('aria-pressed', data.completed_today ? 'true' : 'false');
          var hint = card.querySelector('.habit-tap-hint');
          if (hint) hint.textContent = data.completed_today ? 'Tap to undo' : 'Tap to complete';
        });
    }

    card.addEventListener('click', toggleFromCard);
    card.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggleFromCard(e);
      }
    });
    deleteBtn?.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  });
})();
