// Dark mode
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    const html = document.documentElement;
    const saved = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-bs-theme', saved);
    darkModeToggle.innerHTML = saved === 'dark'
        ? '<i class="bi bi-sun-fill"></i>'
        : '<i class="bi bi-moon-stars-fill"></i>';

    darkModeToggle.addEventListener('click', () => {
        const current = html.getAttribute('data-bs-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        darkModeToggle.innerHTML = next === 'dark'
            ? '<i class="bi bi-sun-fill"></i>'
            : '<i class="bi bi-moon-stars-fill"></i>';
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Skip if in input/textarea
    if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)) return;

    if (e.key === 'n') {
        window.location.href = '/properties/new/';
    }
    if (e.key === '/') {
        e.preventDefault();
        const search = document.getElementById('global-search');
        if (search) search.focus();
    }
    if (e.key === 'd') {
        window.location.href = '/dashboard/';
    }
    if (e.key === 'p') {
        window.location.href = '/properties/';
    }
    if (e.key === 'Escape') {
        window.history.back();
    }
});

// Add Bootstrap classes to form inputs that don't have them
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[type=text], input[type=number], input[type=date], input[type=email], input[type=tel], textarea, select').forEach(el => {
        if (!el.classList.contains('form-control') && !el.classList.contains('form-select') && !el.classList.contains('form-check-input')) {
            if (el.tagName === 'SELECT') {
                el.classList.add('form-select', 'form-select-sm');
            } else if (el.tagName === 'TEXTAREA') {
                el.classList.add('form-control', 'form-control-sm');
            } else {
                el.classList.add('form-control', 'form-control-sm');
            }
        }
    });
});
