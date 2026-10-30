const loading = document.getElementById('loading');
const label = loading.querySelector('.label');
const retry = document.getElementById('retry');
retry.addEventListener('click', () => location.reload());
const timeout = setTimeout(() => {
  label.textContent = 'Načítání trvá déle. Zkontrolujte připojení k internetu.';
  retry.hidden = false;
}, 15000);
window.addEventListener('space-ready', () => clearTimeout(timeout), { once: true });
import('./main.js').catch(error => {
  clearTimeout(timeout);
  console.error('Spuštění aplikace selhalo:', error);
  loading.classList.remove('hidden');
  loading.querySelector('.spinner').hidden = true;
  label.textContent = '3D scénu se nepodařilo spustit. Zkontrolujte připojení a podporu WebGL v prohlížeči.';
  retry.hidden = false;
});
