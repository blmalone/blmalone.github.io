const header = document.querySelector('.site-header');
const toggle = header.querySelector('.nav-toggle');
const nav = header.querySelector('.site-nav');

if (!('CSSViewTransitionRule' in window)) {
  document.documentElement.classList.add('fade-on-entry');
}

function closeMenu() {
  toggle.setAttribute('aria-expanded', 'false');
}

toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') === 'true';
  toggle.setAttribute('aria-expanded', String(!open));
});

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    toggle.focus();
  }
});

document.addEventListener('click', event => {
  if (!header.contains(event.target) || nav.contains(event.target)) closeMenu();
});
header.addEventListener('focusout', event => {
  if (!header.contains(event.relatedTarget)) closeMenu();
});
window.matchMedia('(max-width: 640px)').addEventListener('change', closeMenu);
window.addEventListener('pagehide', closeMenu);
toggle.hidden = false;
