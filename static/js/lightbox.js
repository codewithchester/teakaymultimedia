/* ─── Accessible Image Lightbox ───────────────────────── */
(function () {
    'use strict';

    function init() {
        const items = document.querySelectorAll('[data-lightbox]');
        if (!items.length) return;

        // Build the lightbox DOM once
        const box = document.createElement('div');
        box.className = 'lightbox';
        box.setAttribute('role', 'dialog');
        box.setAttribute('aria-modal', 'true');
        box.setAttribute('aria-label', 'Image viewer');
        box.setAttribute('data-open', 'false');
        box.innerHTML = `
            <button type="button" class="lightbox__close" aria-label="Close">&times;</button>
            <img class="lightbox__img" alt="">
            <div class="lightbox__caption"></div>
        `;
        document.body.appendChild(box);

        const img = box.querySelector('.lightbox__img');
        const cap = box.querySelector('.lightbox__caption');
        const closeBtn = box.querySelector('.lightbox__close');

        let lastFocus = null;

        function open(src, alt, caption) {
            lastFocus = document.activeElement;
            img.src = src;
            img.alt = alt || '';
            cap.textContent = caption || '';
            box.setAttribute('data-open', 'true');
            document.body.style.overflow = 'hidden';
            closeBtn.focus();
        }

        function close() {
            box.setAttribute('data-open', 'false');
            document.body.style.overflow = '';
            img.src = '';
            if (lastFocus) lastFocus.focus();
        }

        items.forEach((item) => {
            item.addEventListener('click', () => {
                const full = item.getAttribute('data-lightbox-src') || item.querySelector('img')?.src;
                const alt = item.getAttribute('data-lightbox-alt') || item.querySelector('img')?.alt || '';
                const caption = item.getAttribute('data-lightbox-caption') || '';
                if (full) open(full, alt, caption);
            });
            item.style.cursor = 'zoom-in';
        });

        closeBtn.addEventListener('click', close);
        box.addEventListener('click', (e) => { if (e.target === box) close(); });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && box.getAttribute('data-open') === 'true') close();
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();