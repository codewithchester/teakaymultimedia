/* ─── Portfolio Filter (progressive enhancement) ──────── */
(function () {
    'use strict';

    function init() {
        const bar = document.querySelector('[data-filter-bar]');
        if (!bar) return;

        const chips = bar.querySelectorAll('[data-filter]');
        const items = document.querySelectorAll('[data-project-category]');

        chips.forEach((chip) => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                const target = chip.getAttribute('data-filter');

                chips.forEach((c) => c.classList.remove('filter-chip--active'));
                chip.classList.add('filter-chip--active');

                items.forEach((item) => {
                    const cat = item.getAttribute('data-project-category');
                    const show = target === 'all' || cat === target;
                    item.style.display = show ? '' : 'none';
                });

                // Update URL without reload
                const url = new URL(window.location);
                if (target === 'all') url.searchParams.delete('category');
                else url.searchParams.set('category', target);
                window.history.replaceState({}, '', url);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();