/* ─── Persistent Audio Player ─────────────────────────
   • Keeps playing across page navigations (sessionStorage)
   • Resumes from last position
   • OS-level media controls via MediaSession API
   • Works with Boxicons or SVG icons
   ──────────────────────────────────────────────────── */
(function () {
    'use strict';

    var KEY_TIME     = 'tkm-audio-time';
    var KEY_PLAYING  = 'tkm-audio-playing';
    var KEY_TITLE    = 'tkm-audio-title';

    function storageGet(key, fallback) {
        try { return sessionStorage.getItem(key) ?? fallback; } catch (e) { return fallback; }
    }
    function storageSet(key, value) {
        try { sessionStorage.setItem(key, value); } catch (e) {}
    }

    function init() {
        var player = document.querySelector('[data-audio-player]');
        if (!player) return;

        var audio = player.querySelector('audio');
        var playBtn = player.querySelector('[data-audio-play]');
        var progress = player.querySelector('[data-audio-progress]');
        var fill = player.querySelector('[data-audio-fill]');
        var timeEl = player.querySelector('[data-audio-time]');
        var toggleTranscript = player.querySelector('[data-audio-transcript-toggle]');
        var transcript = player.querySelector('[data-audio-transcript]');

        if (!audio || !playBtn) return;

        // ── 1. Restore saved position ──
        var savedTime = parseFloat(storageGet(KEY_TIME, '0')) || 0;
        var wasPlaying = storageGet(KEY_PLAYING, '0') === '1';

        if (savedTime > 0.5) {
            // Wait for metadata before seeking
            audio.addEventListener('loadedmetadata', function () {
                try {
                    if (savedTime < audio.duration) {
                        audio.currentTime = savedTime;
                    }
                } catch (e) {}
            }, { once: true });
        }

        // ── 2. Icon switcher (Boxicons or SVG) ──
        function setIcon(isPlaying) {
            var i = playBtn.querySelector('i');
            if (i) {
                i.className = isPlaying ? 'bx bx-pause' : 'bx bx-play';
            } else {
                playBtn.innerHTML = isPlaying
                    ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5h4v14H6zM14 5h4v14h-4z"/></svg>'
                    : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>';
            }
            playBtn.setAttribute('aria-label',
                isPlaying ? 'Pause audio introduction' : 'Play audio introduction');
        }

        function fmt(t) {
            if (!isFinite(t) || isNaN(t)) return '0:00';
            var m = Math.floor(t / 60);
            var s = Math.floor(t % 60);
            return m + ':' + (s < 10 ? '0' + s : s);
        }

        function updateUI() {
            var cur = audio.currentTime || 0;
            var dur = audio.duration || 0;
            var pct = dur ? (cur / dur) * 100 : 0;
            if (fill) fill.style.width = pct + '%';
            if (timeEl) timeEl.textContent = fmt(cur) + ' / ' + fmt(dur);
            setIcon(!audio.paused);
        }

        // ── 3. Play / Pause ──
        function doPlay() {
            audio.play().then(function () {
                updateUI();
            }).catch(function (err) {
                console.warn('[Audio] Play blocked:', err);
                setIcon(false);
                storageSet(KEY_PLAYING, '0');
            });
        }

        playBtn.addEventListener('click', function () {
            if (audio.paused) doPlay();
            else audio.pause();
        });

        // ── 4. Persistence: save time + playing state ──
        audio.addEventListener('timeupdate', function () {
            storageSet(KEY_TIME, String(audio.currentTime));
            updateUI();
        });

        audio.addEventListener('play', function () {
            storageSet(KEY_PLAYING, '1');
            updateUI();
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'playing';
            }
        });

        audio.addEventListener('pause', function () {
            // Don't overwrite "playing" flag when pause is due to page navigation
            if (!document.hidden) {
                storageSet(KEY_PLAYING, '0');
            }
            updateUI();
            if ('mediaSession' in navigator) {
                navigator.mediaSession.playbackState = 'paused';
            }
        });

        audio.addEventListener('ended', function () {
            audio.currentTime = 0;
            storageSet(KEY_PLAYING, '0');
            storageSet(KEY_TIME, '0');
            updateUI();
        });

        audio.addEventListener('loadedmetadata', updateUI);
        audio.addEventListener('canplay', updateUI);

        // ── 5. Progress bar seek ──
        if (progress) {
            progress.addEventListener('click', function (e) {
                var rect = progress.getBoundingClientRect();
                var pct = (e.clientX - rect.left) / rect.width;
                if (audio.duration && isFinite(audio.duration)) {
                    audio.currentTime = pct * audio.duration;
                }
            });
        }

        // ── 6. Transcript toggle ──
        if (toggleTranscript && transcript) {
            toggleTranscript.addEventListener('click', function () {
                var hidden = transcript.hasAttribute('hidden');
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

        // ── 7. Media Session API (OS-level controls) ──
        if ('mediaSession' in navigator) {
            try {
                navigator.mediaSession.metadata = new MediaMetadata({
                    title: storageGet(KEY_TITLE, 'TK Multimedia — Introduction'),
                    artist: 'TK Multimedia',
                    album: 'Brand Introduction'
                });

                navigator.mediaSession.setActionHandler('play', function () {
                    doPlay();
                });
                navigator.mediaSession.setActionHandler('pause', function () {
                    audio.pause();
                });
                navigator.mediaSession.setActionHandler('seekbackward', function () {
                    audio.currentTime = Math.max(0, audio.currentTime - 10);
                });
                navigator.mediaSession.setActionHandler('seekforward', function () {
                    audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 10);
                });
                navigator.mediaSession.setActionHandler('seekto', function (details) {
                    if (details.seekTime != null) audio.currentTime = details.seekTime;
                });
            } catch (e) {
                // MediaSession not fully supported — silently ignore
            }
        }

        // ── 8. Auto-resume if it was playing on the previous page ──
        if (wasPlaying) {
            // Try to resume once metadata is loaded.
            // Note: some browsers may block this because it's not a fresh user gesture.
            // We attempt it; if blocked, a "tap to resume" hint appears.
            audio.addEventListener('canplay', function tryResume() {
                audio.removeEventListener('canplay', tryResume);
                if (!audio.paused) return;
                doPlay();
            }, { once: false });

            // Fallback: if resume is blocked, show prompt
            setTimeout(function () {
                if (audio.paused && storageGet(KEY_PLAYING, '0') === '1') {
                    showResumeHint();
                }
            }, 1200);
        }

        function showResumeHint() {
            if (player.querySelector('[data-resume-hint]')) return;
            var hint = document.createElement('button');
            hint.type = 'button';
            hint.setAttribute('data-resume-hint', '');
            hint.className = 'audio-intro__resume';
            hint.innerHTML = '<i class="bx bx-play-circle"></i> Tap to resume audio';
            hint.addEventListener('click', function () {
                hint.remove();
                doPlay();
            });
            player.appendChild(hint);
        }

        // ── 9. Save time before unload (for smoother cross-page resume) ──
        window.addEventListener('beforeunload', function () {
            storageSet(KEY_TIME, String(audio.currentTime));
            storageSet(KEY_PLAYING, audio.paused ? '0' : '1');
        });

        updateUI();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else { init(); }
})();