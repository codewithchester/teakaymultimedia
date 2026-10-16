/* ─── Theme Management ────────────────────────────────── */
(function () {
    'use strict';

    const STORAGE_KEY = 'tkm-theme';
    const root = document.documentElement;

    function getStoredTheme() {
        try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
    }
    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    function updateToggleUI(theme) {
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'bx bx-sun' : 'bx bx-moon';
            }
        });
    }
    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        updateToggleUI(theme);
    }
    function setTheme(theme) {
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
        applyTheme(theme);
    }
    function toggleTheme() {
        const current = root.getAttribute('data-theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }
    function init() {
        const current = root.getAttribute('data-theme') || getStoredTheme() || getSystemTheme();
        applyTheme(current);
        document.querySelectorAll('[data-theme-toggle]').forEach((btn) => {
            btn.addEventListener('click', toggleTheme);
        });
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!getStoredTheme()) applyTheme(e.matches ? 'dark' : 'light');
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();