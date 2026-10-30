export function bindUi({ targets, bodies, renderer, camera, controls, homePosition, simulation, reducedMotion, focusOn, goHome, speak, cancelFlight, resetClock, THREE }) {
  const categoryFor = id => bodies.some(body => body.id === id) ? 'solar' : ['m101', 'm81', 'm83'].includes(id) ? 'galaxies' : 'special';
  function selectCategory(category) {
    document.querySelectorAll('.planet-btn').forEach(button => { button.hidden = categoryFor(button.dataset.id) !== category; });
    document.querySelectorAll('[data-category]').forEach(button => button.setAttribute('aria-pressed', button.dataset.category === category));
  }
  document.querySelectorAll('[data-category]').forEach(button => button.addEventListener('click', () => selectCategory(button.dataset.category)));
  const bar = document.getElementById('planetBar');
  [...bar.children].filter(element => !element.classList.contains('planet-btn')).forEach(element => element.remove());
  bar.querySelectorAll('.planet-btn').forEach(button => { button.setAttribute('aria-label', targets[button.dataset.id].name); });
  const pause = document.getElementById('pauseBtn');
  const updatePause = () => {
    pause.setAttribute('aria-pressed', simulation.paused);
    pause.textContent = simulation.paused ? '▷ Spustit' : 'Ⅱ Pauza';
  };
  pause.addEventListener('click', () => { simulation.paused = !simulation.paused; updatePause(); });
  updatePause();
  document.getElementById('speed').addEventListener('change', event => { simulation.speed = Number(event.target.value); });
  document.getElementById('detailsBtn').addEventListener('click', event => {
    const expanded = document.getElementById('objectCard').classList.toggle('expanded');
    event.currentTarget.setAttribute('aria-expanded', expanded);
    event.currentTarget.textContent = expanded ? 'Méně ↑' : 'Více ↓';
  });
  document.getElementById('speakBtn').addEventListener('click', () => speak(document.getElementById('title').textContent, true));
  function updateHomePosition() {
    const halfFov = Math.min(THREE.MathUtils.degToRad(camera.fov / 2), Math.atan(Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * camera.aspect));
    homePosition.set(0, .8, 1).normalize().multiplyScalar(145 / Math.sin(halfFov) * 1.1);
  }
  const resizeScene = () => {
    const area = document.getElementById('app');
    if (!area.clientWidth || !area.clientHeight) return;
    camera.aspect = area.clientWidth / area.clientHeight;
    camera.updateProjectionMatrix();
    const profiles = { low: [1, 1000000], medium: [1.5, 2000000], high: [2, 3000000], auto: [1.5, 2000000] };
    const [maxDpr, pixels] = profiles[document.getElementById('quality').value];
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, maxDpr, Math.sqrt(pixels / (area.clientWidth * area.clientHeight))));
    renderer.setSize(area.clientWidth, area.clientHeight);
    updateHomePosition();
  };
  new ResizeObserver(resizeScene).observe(document.getElementById('app'));
  window.addEventListener('resize', () => {
    resizeScene();
    const selected = document.querySelector('.planet-btn.active');
    if (selected) focusOn(selected.dataset.id);
    else goHome();
  });
  document.getElementById('quality').addEventListener('change', resizeScene);
  renderer.domElement.tabIndex = 0;
  renderer.domElement.setAttribute('aria-label', '3D vesmír. Šipky otáčejí pohled, plus a mínus přibližují.');
  renderer.domElement.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '=', '-'].includes(event.key)) return;
    event.preventDefault(); cancelFlight();
    const offset = camera.position.clone().sub(controls.target);
    if (['+', '=', '-'].includes(event.key)) {
      offset.multiplyScalar(event.key === '-' ? 1.15 : 1 / 1.15);
      offset.setLength(THREE.MathUtils.clamp(offset.length(), controls.minDistance, controls.maxDistance));
    } else {
      const spherical = new THREE.Spherical().setFromVector3(offset);
      spherical.theta += event.key === 'ArrowLeft' ? .08 : event.key === 'ArrowRight' ? -.08 : 0;
      spherical.phi += event.key === 'ArrowUp' ? -.08 : event.key === 'ArrowDown' ? .08 : 0;
      spherical.makeSafe(); offset.setFromSpherical(spherical);
    }
    camera.position.copy(controls.target).add(offset); controls.update();
  });
  document.addEventListener('visibilitychange', () => { resetClock(); if (document.hidden) window.speechSynthesis?.cancel(); });
  reducedMotion.addEventListener('change', event => { if (event.matches) { simulation.paused = true; updatePause(); } });
  resizeScene(); selectCategory('solar');
  return { selectCategory, categoryFor, updateHomePosition };
}
