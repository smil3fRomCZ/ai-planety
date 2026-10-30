// Skutečné údaje, nezávislé na ilustrativních jednotkách a rychlostech scény.
// NASA NSSDCA Metric Fact Sheet, verze 18. 3. 2025; ověřeno 30. 10. 2026.
export const FACT_SOURCES = {
  table: 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/',
  notes: 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/planetfact_notes.html',
  sun: 'https://science.nasa.gov/sun/facts/',
};

// Poloměr je objemový střední; průměr a srovnání se Zemí se z něj odvozují.
// Rok je tropický oběh, den je sluneční den. Záporná rotace značí retrográdní směr.
const rows = {
  mercury: [2439.7, 57.9, 46, 69.8, 88, 1407.6, 4222.6, .034, 7, .206, 167, .330, 3.7, 5429, 0, false],
  venus: [6051.8, 108.2, 107.5, 108.9, 224.7, -5832.5, 2802, 177.4, 3.4, .007, 464, 4.87, 8.9, 5243, 0, false],
  earth: [6371, 149.6, 147.1, 152.1, 365.2, 23.9, 24, 23.4, 0, .017, 15, 5.97, 9.8, 5514, 1, false],
  mars: [3389.5, 228, 206.7, 249.3, 687, 24.6, 24.7, 25.2, 1.8, .094, -65, .642, 3.7, 3934, 2, false],
  jupiter: [69911, 778.5, 740.6, 816.4, 4331, 9.9, 9.9, 3.1, 1.3, .049, -110, 1898, 23.1, 1326, 95, true],
  saturn: [58232, 1432, 1357.6, 1506.5, 10747, 10.7, 10.7, 26.7, 2.5, .052, -140, 568, 9, 687, 274, true],
  uranus: [25362, 2867, 2732.7, 3001.4, 30589, -17.2, 17.2, 97.8, .8, .047, -195, 86.8, 8.7, 1270, 28, true],
  neptune: [24622, 4515, 4471.1, 4558.9, 59800, 16.1, 16.1, 28.3, 1.8, .010, -200, 102, 11, 1638, 16, true],
};
const descriptions = {
  mercury: ['Kamenná planeta', 'Řídká exosféra, nikoli hustá atmosféra.', 'Nejmenší planeta soustavy. Sluneční den zde trvá déle než jeden oběh kolem Slunce.'],
  venus: ['Kamenná planeta', 'Hustá atmosféra s převahou oxidu uhličitého.', 'Venuše se otáčí opačným směrem než Země. Její vysoká teplota souvisí se silným skleníkovým efektem.'],
  earth: ['Kamenná planeta', 'Převážně dusík a kyslík.', 'Náš domov s oceány kapalné vody. Otočení vzhledem ke hvězdám je o něco kratší než sluneční den.'],
  mars: ['Kamenná planeta', 'Řídká atmosféra s převahou oxidu uhličitého.', 'Načervenalá planeta se dvěma malými měsíci. Délka jejího dne se podobá pozemské.'],
  jupiter: ['Plynný obr', 'Převážně vodík a helium; bez pevného povrchu.', 'Největší planeta soustavy. I přes svou velikost se velmi rychle otáčí kolem osy.'],
  saturn: ['Plynný obr', 'Převážně vodík a helium; bez pevného povrchu.', 'Výrazné prstence obklopují planetu s nízkou průměrnou hustotou.'],
  uranus: ['Ledový obr', 'Vodík, helium a metan; bez pevného povrchu.', 'Rotační osa je výrazně nakloněná: Uran se při oběhu téměř převaluje na boku.'],
  neptune: ['Ledový obr', 'Vodík, helium a metan; bez pevného povrchu.', 'Nejvzdálenější z osmi planet. Jeden oběh kolem Slunce zde zabere mnoho pozemských let.'],
};
export const PLANET_FACTS = Object.fromEntries(Object.entries(rows).map(([id, row]) => {
  const [meanRadiusKm, distanceMillionKm, perihelionMillionKm, aphelionMillionKm, orbitalDays, rotationHours, solarDayHours, tiltDeg, inclinationDeg, eccentricity, temperatureC, mass24Kg, gravity, density, moons, rings] = row;
  const [type, atmosphere, description] = descriptions[id];
  return [id, { meanRadiusKm, distanceMillionKm, perihelionMillionKm, aphelionMillionKm, orbitalDays, rotationHours, solarDayHours, tiltDeg, inclinationDeg, eccentricity, temperatureC, mass24Kg, gravity, density, moons, rings, type, atmosphere, description, giant: ['jupiter', 'saturn', 'uranus', 'neptune'].includes(id), source: `https://nssdc.gsfc.nasa.gov/planetary/factsheet/${id}fact.html` }];
}));

export const SUN_FACTS = {
  meanRadiusKm: 695700,
  massKg: 1.9884e30,
  temperatureC: 5500,
  gravity: 274,
  description: 'Hvězda ve středu naší soustavy. Její energie vzniká jadernou fúzí; Slunce není planeta a nemá pevný povrch.',
  source: 'https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html',
};
