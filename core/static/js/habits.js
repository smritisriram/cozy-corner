(function() {
  const colorInput = document.getElementById('habit-color-input');
  const options = document.querySelectorAll('.habit-color-picker .color-option');
  if (!colorInput || !options.length) return;
  options.forEach(function(opt) {
    opt.addEventListener('click', function() {
      options.forEach(function(o) { o.classList.remove('selected'); });
      opt.classList.add('selected');
      colorInput.value = opt.dataset.color;
    });
  });
})();
