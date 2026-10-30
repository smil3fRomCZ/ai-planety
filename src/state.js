// Simulační čas je nezávislý na času navigace a rozhraní.
export function createSimulation(reducedMotion = false) {
  return {
    paused: reducedMotion,
    speed: 1,
    elapsed: 0,
    advance(delta) {
      const step = this.paused ? 0 : Math.min(Math.max(delta, 0), 0.05) * this.speed;
      this.elapsed += step;
      return step;
    },
  };
}
