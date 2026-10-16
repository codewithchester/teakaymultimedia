/* ─── Mobile Navigation ───────────────────────────────── */
(function () {
    'use strict';

    function init() {
        const toggle = document.querySelector('[data-nav-toggle]');
        const menu = document.querySelector('[data-nav-menu]');

        if (!toggle || !menu) return;

        function closeMenu() {
            menu.setAttribute('data-open', 'false');
            toggle.setAttribute('aria-expanded', 'false');
        }

        function openMenu() {
            menu.setAttribute('data-open', 'true');
            toggle.setAttribute('aria-expanded', 'true');
        }

        toggle.addEventListener('click', () => {
            const isOpen = menu.getAttribute('data-open') === 'true';
            isOpen ? closeMenu() : openMenu();
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && menu.getAttribute('data-open') === 'true') {
                closeMenu();
                toggle.focus();
            }
        });

        // Close when a link is clicked (mobile nav)
        menu.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', closeMenu);
        });

        // Close on resize above mobile breakpoint
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth > 900) closeMenu();
            }, 150);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();