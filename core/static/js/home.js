(function() {
  const track = document.querySelector('.carousel-track');
  const slides = document.querySelectorAll('.carousel-slide');
  const dotsContainer = document.getElementById('carousel-dots');
  const total = slides.length;
  let index = 0;

  if (!track || !dotsContainer) return;

  for (let i = 0; i < total; i++) {
    const dot = document.createElement('button');
    dot.className = 'carousel-dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', 'Slide ' + (i + 1));
    dot.addEventListener('click', () => goToSlide(i));
    dotsContainer.appendChild(dot);
  }

  function goToSlide(i) {
    index = Math.max(0, Math.min(i, total - 1));
    track.style.transform = 'translateX(-' + index * 100 + '%)';
    dotsContainer.querySelectorAll('.carousel-dot').forEach(function(d, j) {
      d.classList.toggle('active', j === index);
    });
  }

  setInterval(function() { goToSlide((index + 1) % total); }, 5000);
})();

(function() {
  const guide = document.getElementById('dumpling-guide');
  const closeBtn = document.getElementById('close-dumpling-guide');
  if (sessionStorage.getItem('dumpling-guide-shown')) return;
  setTimeout(function() {
    if (guide) { guide.classList.add('visible'); sessionStorage.setItem('dumpling-guide-shown', 'true'); }
  }, 9000);
  if (closeBtn) closeBtn.addEventListener('click', function() { guide.classList.remove('visible'); });
})();
