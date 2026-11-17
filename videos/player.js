let activePlayer;
let hoverPreview;
let hoverLink;
let hoverVersion = 0;
let youtubeApi;

function stopHoverPreview() {
  hoverVersion += 1;
  hoverLink = undefined;
  if (hoverPreview) {
    hoverPreview.player?.destroy();
    hoverPreview.frame.remove();
    hoverPreview = undefined;
  }
}

function loadYouTubeApi() {
  if (window.YT?.Player) return Promise.resolve(window.YT);
  if (!youtubeApi) {
    youtubeApi = new Promise((resolve, reject) => {
      window.onYouTubeIframeAPIReady = () => resolve(window.YT);
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.onerror = () => {
        script.remove();
        youtubeApi = undefined;
        reject(new Error('YouTube preview unavailable'));
      };
      document.head.appendChild(script);
    });
  }
  return youtubeApi;
}

function canPreview(link) {
  return !activePlayer
    && !document.hidden
    && window.matchMedia('(hover: hover) and (pointer: fine)').matches
    && !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    && link.closest('[data-video-section]').dataset.videoView !== 'list';
}

async function startHoverPreview(link) {
  if (!canPreview(link)) return;
  stopHoverPreview();
  hoverLink = link;
  const version = hoverVersion;
  try {
    const api = await loadYouTubeApi();
    if (version !== hoverVersion || !link.matches(':hover') || !canPreview(link)) return;
    const videoId = link.dataset.videoId;
    if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;
    const frame = document.createElement('iframe');
    frame.className = 'video-media video-hover-player';
    frame.title = `Muted preview: ${link.getAttribute('aria-label').replace(/^Play /, '')}`;
    frame.tabIndex = -1;
    frame.setAttribute('aria-hidden', 'true');
    frame.style.visibility = 'hidden';
    frame.allow = 'autoplay; encrypted-media';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    const params = new URLSearchParams({
      enablejsapi: '1', origin: window.location.origin, controls: '0',
      playsinline: '1', rel: '0', loop: '1', playlist: videoId,
    });
    frame.src = `https://www.youtube-nocookie.com/embed/${videoId}?${params}`;
    link.after(frame);
    const preview = { frame, link, player: undefined };
    hoverPreview = preview;
    const cancel = () => { if (hoverPreview === preview) stopHoverPreview(); };
    preview.player = new api.Player(frame, {
      events: {
        onReady: (event) => {
          if (hoverPreview !== preview) return;
          if (!link.matches(':hover') || !canPreview(link)) return cancel();
          event.target.mute();
          event.target.playVideo();
        },
        onStateChange: (event) => {
          if (hoverPreview === preview && event.data === api.PlayerState.PLAYING) {
            frame.style.visibility = 'visible';
          }
        },
        onError: cancel,
        onAutoplayBlocked: cancel,
      },
    });
  } catch {
    if (version === hoverVersion) stopHoverPreview();
  }
}

function setVideoView(section, view) {
  if (view === 'list' && hoverLink && section.contains(hoverLink)) stopHoverPreview();
  if (view === 'list' && activePlayer && section.contains(activePlayer.frame)) {
    activePlayer.frame.replaceWith(activePlayer.link);
    activePlayer = undefined;
  }
  section.dataset.videoView = view === 'list' ? 'list' : 'grid';
  for (const button of section.querySelectorAll('button[data-video-view]')) {
    button.setAttribute('aria-pressed', String(button.dataset.videoView === section.dataset.videoView));
  }
}

for (const link of document.querySelectorAll('a.video-preview[data-video-id]')) {
  link.addEventListener('pointerenter', () => startHoverPreview(link));
  link.addEventListener('pointerleave', () => {
    if (hoverLink === link) stopHoverPreview();
  });
}

document.addEventListener('visibilitychange', () => {
  if (document.hidden) stopHoverPreview();
});

for (const section of document.querySelectorAll('[data-video-section]')) {
  const storageKey = `video-view-${section.dataset.videoSection}`;
  try {
    setVideoView(section, localStorage.getItem(storageKey) || localStorage.getItem('video-view'));
  } catch {
    setVideoView(section, 'grid');
  }
  section.querySelector('.view-switch').hidden = false;
  for (const button of section.querySelectorAll('button[data-video-view]')) {
    button.addEventListener('click', () => {
      setVideoView(section, button.dataset.videoView);
      try { localStorage.setItem(storageKey, section.dataset.videoView); } catch { /* Private browsing can disable storage. */ }
    });
  }
}

// Load one YouTube player at a time, only after a visitor chooses a thumbnail.
document.addEventListener('click', (event) => {
  const link = event.target.closest('a.video-preview[data-video-id]');
  if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const videoId = link.dataset.videoId;
  if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return;
  event.preventDefault();
  stopHoverPreview();

  if (activePlayer) activePlayer.frame.replaceWith(activePlayer.link);

  const frame = document.createElement('iframe');
  frame.className = 'video-media video-player';
  frame.src = `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`;
  frame.title = link.getAttribute('aria-label').replace(/^Play /, '');
  frame.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
  frame.allowFullscreen = true;
  frame.referrerPolicy = 'strict-origin-when-cross-origin';
  link.replaceWith(frame);
  activePlayer = { frame, link };
  frame.focus();
});

// Prepare the API on desktop so the first hover does not need to download it.
const firstPreview = document.querySelector('a.video-preview[data-video-id]');
if (firstPreview && canPreview(firstPreview)) {
  loadYouTubeApi().catch(() => { /* Thumbnails remain available if YouTube is blocked. */ });
}
