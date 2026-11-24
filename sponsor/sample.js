const sample = document.querySelector('.sample');
const player = sample.querySelector('.sample-player');
const template = sample.querySelector('template');

sample.addEventListener('toggle', () => {
  if (sample.open) {
    player.replaceChildren(template.content.cloneNode(true));
  } else {
    player.replaceChildren();
  }
});
