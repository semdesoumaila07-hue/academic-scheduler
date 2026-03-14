// Small script to toggle background image and remember choice in localStorage
(function () {
  function updateButton(btn, disabled) {
    btn.setAttribute('aria-pressed', disabled ? 'true' : 'false');
    btn.textContent = disabled ? 'Fond : Off' : 'Fond : On';
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('bg-toggle');
    if (!btn) return;
    var body = document.body;
    var saved = localStorage.getItem('bgDisabled') === 'true';
    if (saved) {
      body.classList.add('bg-disabled');
    }
    updateButton(btn, saved);

    btn.addEventListener('click', function () {
      var disabled = body.classList.toggle('bg-disabled');
      updateButton(btn, disabled);
      localStorage.setItem('bgDisabled', disabled);
    });
  });
})();
