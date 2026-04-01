(function() {
  const subject = window.EXAM_SUBJECT || 'math';
  const durationMin = window.EXAM_DURATION || 10;
  const completeUrl = window.EXAM_COMPLETE_URL || '/exams/complete/';
  const csrfToken = window.CSRF_TOKEN || '';

  const questions = {
    math: [
      { q: 'What is 3/4 + 1/2?', options: ['5/4', '1', '7/8', '4/6'], correct: 0 },
      { q: 'Solve for x: 2x + 5 = 15', options: ['x = 5', 'x = 10', 'x = 7', 'x = 3'], correct: 0 },
      { q: 'What is the area of a circle with radius 3?', options: ['9π', '6π', '3π', '12π'], correct: 0 },
      { q: 'What is the mean of 4, 8, 6, 10?', options: ['7', '6', '8', '5'], correct: 0 },
      { q: 'Simplify: 2(x + 3) - 4', options: ['2x + 2', '2x + 6', '2x - 2', '2x + 10'], correct: 0 },
    ],
    science: [
      { q: 'What organelle is known as the powerhouse of the cell?', options: ['Mitochondria', 'Nucleus', 'Ribosome', 'Golgi'], correct: 0 },
      { q: 'What type of energy does a moving object have?', options: ['Kinetic', 'Potential', 'Thermal', 'Chemical'], correct: 0 },
      { q: 'What is the chemical formula for water?', options: ['H2O', 'CO2', 'O2', 'H2O2'], correct: 0 },
      { q: 'Which planet is closest to the Sun?', options: ['Mercury', 'Venus', 'Earth', 'Mars'], correct: 0 },
      { q: 'What force keeps us on the ground?', options: ['Gravity', 'Magnetism', 'Friction', 'Inertia'], correct: 0 },
    ],
    history: [
      { q: 'In what year was the Declaration of Independence signed?', options: ['1776', '1787', '1775', '1789'], correct: 0 },
      { q: 'Who wrote the Declaration of Independence?', options: ['Thomas Jefferson', 'George Washington', 'Benjamin Franklin', 'John Adams'], correct: 0 },
      { q: 'The Civil Rights Movement aimed to end what?', options: ['Racial segregation', 'War', 'Poverty', 'Disease'], correct: 0 },
      { q: 'Who gave the "I Have a Dream" speech?', options: ['Martin Luther King Jr.', 'Malcolm X', 'Rosa Parks', 'Frederick Douglass'], correct: 0 },
      { q: 'World War II ended in what year?', options: ['1945', '1944', '1946', '1943'], correct: 0 },
    ],
    reading: [
      { q: 'What is the main idea of a passage?', options: ['The central point the author wants to convey', 'The first sentence', 'The title', 'The conclusion'], correct: 0 },
      { q: 'What is a thesis statement?', options: ['The main argument of an essay', 'A question', 'A quote', 'A summary'], correct: 0 },
      { q: 'Which is a proper noun?', options: ['Paris', 'city', 'beautiful', 'travel'], correct: 0 },
      { q: 'What does "foreshadowing" mean?', options: ['Hints about what will happen later', 'A flashback', 'Dialogue', 'Description'], correct: 0 },
      { q: 'What is the purpose of a topic sentence?', options: ['Introduce the main idea of a paragraph', 'Conclude an essay', 'Ask a question', 'Quote a source'], correct: 0 },
    ],
  };

  const examQuestions = (questions[subject] || questions.math).slice(0, 5);
  let currentIndex = 0;
  let answers = {};
  let timeLeft = durationMin * 60;
  let timerInterval;

  function pad(n) { return n < 10 ? '0' + n : n; }
  function updateTimer() {
    document.getElementById('exam-timer').textContent = Math.floor(timeLeft / 60) + ':' + pad(timeLeft % 60);
    if (timeLeft <= 0) finishExam();
    else timeLeft--;
  }
  function startTimer() {
    timerInterval = setInterval(updateTimer, 1000);
  }
  function renderQuestion() {
    const q = examQuestions[currentIndex];
    if (!q) return;
    document.getElementById('exam-question').textContent = q.q;
    const answersEl = document.getElementById('exam-answers');
    answersEl.innerHTML = '';
    q.options.forEach(function(opt, i) {
      const btn = document.createElement('button');
      btn.className = 'exam-answer' + (answers[currentIndex] === i ? ' selected' : '');
      btn.textContent = opt;
      btn.type = 'button';
      btn.addEventListener('click', function() {
        answers[currentIndex] = i;
        answersEl.querySelectorAll('.exam-answer').forEach(function(b, j) { b.classList.toggle('selected', j === i); });
      });
      answersEl.appendChild(btn);
    });
    document.getElementById('exam-prev').disabled = currentIndex === 0;
    document.getElementById('exam-next').textContent = currentIndex === examQuestions.length - 1 ? 'Finish' : 'Next';
  }
  function finishExam() {
    if (timerInterval) clearInterval(timerInterval);
    const total = examQuestions.length;
    if (window.EXAM_PRACTICE_MODE) {
      alert('Practice round complete.\n\nNo grades here — just you showing up. That already counts. Take a breath and be kind to yourself.');
    } else {
      let correct = 0;
      examQuestions.forEach(function(q, i) { if (answers[i] === q.correct) correct++; });
      const pct = Math.round((correct / total) * 100);
      alert('Exam complete!\n\nYou got ' + correct + ' out of ' + total + ' correct (' + pct + '%).\n\nThis is a supportive space — every attempt helps you build confidence. Keep practicing!');
    }
    fetch(completeUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify({}),
    }).then(function() { window.location.href = '/exams/'; });
  }

  document.getElementById('exam-prev').addEventListener('click', function() {
    if (currentIndex > 0) { currentIndex--; renderQuestion(); }
  });
  document.getElementById('exam-next').addEventListener('click', function() {
    if (currentIndex < examQuestions.length - 1) { currentIndex++; renderQuestion(); }
    else finishExam();
  });

  renderQuestion();
  startTimer();
})();
