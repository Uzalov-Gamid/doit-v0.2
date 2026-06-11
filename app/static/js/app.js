document.documentElement.classList.add('js-ready');

document.querySelectorAll('.status-form select').forEach((select) => {
    select.addEventListener('change', () => {
        select.closest('.status-form')?.classList.add('is-dirty');
    });
});

document.querySelectorAll('form').forEach((form) => {
    form.addEventListener('submit', () => {
        form.classList.add('is-submitting');
    });
});
