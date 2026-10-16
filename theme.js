/* ─── Theme Management ────────────────────────────────── */
(function () {
    'use strict';

    const STORAGE_KEY = 'tkm-theme';
    const root = document.documentElement;

    function getStoredTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            return null;
        }
    }

    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';
    }

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        updateToggleUI(theme);
    }

    function updateToggleUI(theme) {
        const buttons = document.querySelectorAll('[data-theme-toggle]');
        buttons.forEach((btn) => {
            btn.setAttribute(
                'aria-label',
                theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'
            );
            btn.setAttribute('data-current-theme', theme);
        });
    }

    function setTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            /* localStorage unavailable — theme still applies for this session */
        }
        applyTheme(theme);
    }

    function toggleTheme() {
        const current = root.getAttribute('data-theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }

    // Initial theme — inline script in <head> already set this to avoid flash.
    // This just syncs the toggle UI once DOM is ready.
    function init() {
        const current = root.getAttribute('data-theme') || getStoredTheme() || getSystemTheme();
        applyTheme(current);

        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            btn.addEventListener('click', toggleTheme);
        });

        // Listen for system changes only if user hasn't set a preference
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!getStoredTheme()) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();