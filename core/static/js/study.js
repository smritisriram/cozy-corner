(function() {
  const generateBtn = document.getElementById('study-generate');
  const topicEl = document.getElementById('study-topic');
  const output = document.getElementById('study-output');
  const explanationEl = document.getElementById('study-explanation-text');
  const practiceArea = document.getElementById('study-practice-area');
  const nextBtn = document.getElementById('study-practice-next');
  const encouragementEl = document.getElementById('study-encouragement');
  const generateUrl = window.STUDY_GENERATE_URL;
  const csrfToken = window.CSRF_TOKEN;

  let questions = [];
  let qIndex = 0;
  let selectedOption = null;

  const encouragements = [
    'Nice — thinking it through is what matters.',
    'That works. Keep going gently.',
    'Good effort. There is no rush here.',
    'Thanks for practicing. You are building skill bit by bit.',
  ];

  function showEncouragement() {
    encouragementEl.textContent = encouragements[Math.floor(Math.random() * encouragements.length)];
    encouragementEl.classList.remove('study-hidden');
  }

  function renderQuestion() {
    selectedOption = null;
    nextBtn.classList.add('study-hidden');
    encouragementEl.classList.add('study-hidden');
    encouragementEl.textContent = '';
    const q = questions[qIndex];
    if (!q) {
      practiceArea.innerHTML = '<p class="study-done-msg">You finished this practice round. Come back anytime — no grades, just care. ✨</p>';
      nextBtn.classList.add('study-hidden');
      return;
    }
    practiceArea.innerHTML = '';
    const title = document.createElement('p');
    title.className = 'study-q-text';
    title.textContent = q.q;
    practiceArea.appendChild(title);
    const opts = document.createElement('div');
    opts.className = 'study-options';
    q.options.forEach(function(opt, i) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'study-option';
      btn.textContent = opt;
      btn.addEventListener('click', function() {
        opts.querySelectorAll('.study-option').forEach(function(b) { b.classList.remove('selected'); });
        btn.classList.add('selected');
        selectedOption = i;
        showEncouragement();
        nextBtn.classList.remove('study-hidden');
      });
      opts.appendChild(btn);
    });
    practiceArea.appendChild(opts);
    nextBtn.textContent = qIndex >= questions.length - 1 ? 'Finish' : 'Next';
  }

  nextBtn.addEventListener('click', function() {
    if (selectedOption === null && questions[qIndex]) return;
    qIndex += 1;
    renderQuestion();
  });

  generateBtn?.addEventListener('click', function() {
    const topic = (topicEl && topicEl.value || '').trim();
    if (topic.length < 2) {
      alert('Please enter a topic (at least a couple of characters).');
      return;
    }
    generateBtn.disabled = true;
    fetch(generateUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ topic: topic }),
    })
      .then(function(r) {
        return r.text().then(function(text) {
          try {
            return { ok: r.ok, data: JSON.parse(text) };
          } catch (e) {
            return { ok: false, data: { error: 'Unexpected response' } };
          }
        });
      })
      .then(function(res) {
        generateBtn.disabled = false;
        if (!res.ok) {
          alert((res.data && res.data.error) || 'Something went wrong. Try again.');
          return;
        }
        output.classList.remove('study-output--hidden');
        explanationEl.textContent = res.data.explanation || '';
        questions = res.data.questions || [];
        qIndex = 0;
        renderQuestion();
      })
      .catch(function() {
        generateBtn.disabled = false;
        alert('Could not reach the server. Check your connection.');
      });
  });
})();
