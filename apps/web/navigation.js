const menuToggle = document.querySelector('#menu-toggle');
const globalNavigation = document.querySelector('#global-navigation');
function closeGlobalMenu() {
  globalNavigation.hidden = true;
  menuToggle.setAttribute('aria-expanded', 'false');
}
menuToggle.addEventListener('click', () => {
  const open = globalNavigation.hidden;
  globalNavigation.hidden = !open;
  menuToggle.setAttribute('aria-expanded', String(open));
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !globalNavigation.hidden) { closeGlobalMenu(); menuToggle.focus(); }
});
document.addEventListener('click', event => {
  if (!event.target.closest('.global-menu')) closeGlobalMenu();
});
