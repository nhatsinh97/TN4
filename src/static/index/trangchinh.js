$(document).on('click', '.ajax-link', function (e) {
  e.preventDefault();
  var url = $(this).attr('href');

  $('#content').load(url, function (response, status, xhr) {
    if (status === 'error') {
      $('#content').html("<div class='alert alert-danger'>Không thể tải nội dung: " + xhr.status + "</div>");
    }
  });
});

function toggleSidebar() {
  document.body.classList.toggle('sidebar-collapsed');
}

function animateCounters() {
  document.querySelectorAll('[data-count]').forEach((el) => {
    const target = Number(el.dataset.count || 0);
    let current = 0;
    const step = Math.max(1, Math.round(target / 60));

    const tick = () => {
      current += step;
      if (current >= target) {
        el.textContent = target;
      } else {
        el.textContent = current;
        requestAnimationFrame(tick);
      }
    };

    tick();
  });
}

function updateTimestamp() {
  const el = document.querySelector('[data-last-updated]');
  if (!el) return;

  const now = new Date();
  const formatted = now.toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  el.textContent = formatted;
}

document.addEventListener('DOMContentLoaded', () => {
  animateCounters();
  updateTimestamp();
});
