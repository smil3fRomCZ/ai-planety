export const TEX = 'https://cdn.jsdelivr.net/gh/jeromeetienne/threex.planets@master/images/';

export const BODIES = [
  { id: 'sun',     name: 'Slunce',  radius: 11.0, distance: 0,    rotSpeed: 0.0008, orbSpeed: 0,       color: 0xffcc55, tex: TEX + 'sunmap.jpg',       emissive: true, info: 'Naše hvězda' },
  { id: 'mercury', name: 'Merkur',  radius: 1.2,  distance: 20,   rotSpeed: 0.003,  orbSpeed: 0.0045,  color: 0x9c8b7a, tex: TEX + 'mercurymap.jpg',   info: 'Nejmenší planeta' },
  { id: 'venus',   name: 'Venuše',  radius: 2.2,  distance: 28,   rotSpeed: 0.002,  orbSpeed: 0.0030,  color: 0xe6c478, tex: TEX + 'venusmap.jpg',     info: 'Nejteplejší planeta' },
  { id: 'earth',   name: 'Země',    radius: 2.4,  distance: 38,   rotSpeed: 0.010,  orbSpeed: 0.0022,  color: 0x2b75ff, tex: TEX + 'earthmap1k.jpg',   clouds: TEX + 'earthcloudmap.jpg', info: 'Náš domov', moon: true },
  { id: 'mars',    name: 'Mars',    radius: 1.8,  distance: 50,   rotSpeed: 0.009,  orbSpeed: 0.0017,  color: 0xc1440e, tex: TEX + 'marsmap1k.jpg',    info: 'Červená planeta' },
  { id: 'jupiter', name: 'Jupiter', radius: 6.0,  distance: 70,   rotSpeed: 0.020,  orbSpeed: 0.0009,  color: 0xd2a679, tex: TEX + 'jupitermap.jpg',   info: 'Největší planeta' },
  { id: 'saturn',  name: 'Saturn',  radius: 5.0,  distance: 95,   rotSpeed: 0.018,  orbSpeed: 0.0006,  color: 0xe6d8a8, tex: TEX + 'saturnmap.jpg',    ring: TEX + 'saturnringcolor.jpg', info: 'Planeta s prstenci' },
  { id: 'uranus',  name: 'Uran',    radius: 3.4,  distance: 115,  rotSpeed: 0.012,  orbSpeed: 0.0004,  color: 0x9fd6dc, tex: TEX + 'uranusmap.jpg',    info: 'Ledový obr' },
  { id: 'neptune', name: 'Neptun',  radius: 3.3,  distance: 135,  rotSpeed: 0.011,  orbSpeed: 0.0003,  color: 0x3d5af1, tex: TEX + 'neptunemap.jpg',   info: 'Nejvzdálenější planeta' },
];

export const MOON_TEX  = TEX + 'moonmap1k.jpg';
export const GALAXY_BG = TEX + 'galaxy_starfield.png';

