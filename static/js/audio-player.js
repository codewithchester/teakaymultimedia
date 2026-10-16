/* ─── Accessible Audio Player ─────────────────────────── */
(function () {
    'use strict';

    function init() {
        const player = document.querySelector('[data-audio-player]');
        if (!player) return;

        const audio = player.querySelector('audio');
        const playBtn = player.querySelector('[data-audio-play]');
        const progress = player.querySelector('[data-audio-progress]');
        const fill = player.querySelector('[data-audio-fill]');
        const timeEl = player.querySelector('[data-audio-time]');
        const toggleTranscript = player.querySelector('[data-audio-transcript-toggle]');
        const transcript = player.querySelector('[data-audio-transcript]');

        if (!audio || !playBtn) return;

        const PLAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
        const PAUSE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>';

        function fmt(t) {
            if (!isFinite(t)) return '0:00';
            const m = Math.floor(t / 60);
            const s = Math.floor(t % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        }

        function updateUI() {
            const cur = audio.currentTime || 0;
            const dur = audio.duration || 0;
            const pct = dur ? (cur / dur) * 100 : 0;
            if (fill) fill.style.width = pct + '%';
            if (timeEl) timeEl.textContent = `${fmt(cur)} / ${fmt(dur)}`;
            playBtn.innerHTML = audio.paused ? PLAY_ICON : PAUSE_ICON;
            playBtn.setAttribute('aria-label', audio.paused ? 'Play audio introduction' : 'Pause audio introduction');
        }

        playBtn.addEventListener('click', () => {
            if (audio.paused) {
                audio.play().catch(() => {
                    // Autoplay or codec issue — fail silently, UI stays paused
                    updateUI();
                });
            } else {
                audio.pause();
            }
        });

        audio.addEventListener('timeupdate', updateUI);
        audio.addEventListener('loadedmetadata', updateUI);
        audio.addEventListener('play', updateUI);
        audio.addEventListener('pause', updateUI);
        audio.addEventListener('ended', () => {
            audio.currentTime = 0;
            updateUI();
        });

        if (progress) {
            progress.addEventListener('click', (e) => {
                const rect = progress.getBoundingClientRect();
                const pct = (e.clientX - rect.left) / rect.width;
                if (audio.duration) audio.currentTime = pct * audio.duration;
            });
        }

        if (toggleTranscript && transcript) {
            toggleTranscript.addEventListener('click', () => {
                const hidden = transcript.hasAttribute('hidden');
                if (hidden) {
                    transcript.removeAttribute('hidden');
                    toggleTranscript.textContent = 'Hide transcript';
                    toggleTranscript.setAttribute('aria-expanded', 'true');
                } else {
                    transcript.setAttribute('hidden', '');
                    toggleTranscript.textContent = 'Show transcript';
                    toggleTranscript.setAttribute('aria-expanded', 'false');
                }
            });
        }

        updateUI();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();