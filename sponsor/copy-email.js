const copyButton = document.querySelector('.copy-email');
const emailLink = document.querySelector('.contact');
const copyStatus = document.querySelector('.copy-status');

if (navigator.clipboard?.writeText) {
  copyButton.hidden = false;
  let clearFeedback;

  copyButton.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(emailLink.textContent.trim());
      copyStatus.textContent = 'Copied';
    } catch {
      copyStatus.textContent = 'Select the address to copy it.';
    }
    clearTimeout(clearFeedback);
    clearFeedback = setTimeout(() => { copyStatus.textContent = ''; }, 4000);
  });
}
