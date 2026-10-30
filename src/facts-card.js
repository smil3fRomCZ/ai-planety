import { PLANET_FACTS, SUN_FACTS, FACT_SOURCES } from './planet-facts.js';

const number = (value, digits = 1) => new Intl.NumberFormat('cs-CZ', { maximumFractionDigits: digits }).format(value);
const km = value => `${number(value)} km`;
const hours = value => `${number(Math.abs(value))} h`;
const distance = value => `${number(value)} mil. km`;
const days = value => `${number(value)} pozemských dní`;
const temperature = value => `${number(value, 0)} °C`;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function rows(items, className = 'facts-list') {
  const list = element('dl', undefined, className);
  items.forEach(([label, value]) => {
    const row = element('div');
    row.append(element('dt', label), element('dd', value));
    list.append(row);
  });
  return list;
}
function section(title, items, note) {
  const details = element('details', undefined, 'facts-section');
  details.append(element('summary', title), rows(items));
  if (note) details.append(element('p', note, 'facts-note'));
  return details;
}
function sourceLink(label, url) {
  const link = element('a', label);
  link.href = url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  return link;
}

export function renderFacts(id) {
  const host = document.getElementById('objectFacts');
  host.replaceChildren();
  host.hidden = true;
  delete host.dataset.objectId;
  document.getElementById('objectCard').scrollTop = 0;
  const facts = PLANET_FACTS[id];
  if (!facts && id !== 'sun') return;
  host.hidden = false;
  host.dataset.objectId = id;
  const description = id === 'sun' ? SUN_FACTS.description : facts.description;
  document.getElementById('objectCopy').textContent = description;
  if (facts) {
    host.append(element('p', facts.type, 'facts-type'));
    host.append(rows([
      ['Střední průměr', km(facts.meanRadiusKm * 2)],
      ['Od Slunce · průměr', distance(facts.distanceMillionKm)],
      [facts.giant ? 'Teplota · hladina 1 bar' : 'Průměrná teplota', temperature(facts.temperatureC)],
      ['Rok · pozemské dny', `${number(facts.orbitalDays)} dní`],
    ], 'facts-highlights'));
    host.append(section('Velikost a gravitace', [
      ['Střední poloměr', km(facts.meanRadiusKm)],
      ['Střední průměr', km(facts.meanRadiusKm * 2)],
      ['Průměr vůči Zemi', `${number(facts.meanRadiusKm / PLANET_FACTS.earth.meanRadiusKm, 3)}×`],
      ['Hmotnost', `${number(facts.mass24Kg, 3)} × 10²⁴ kg`],
      ['Průměrná hustota', `${number(facts.density, 0)} kg/m³`],
      ['Tíhové zrychlení · rovník', `${number(facts.gravity)} m/s²`],
    ], 'Střední poloměr odpovídá kouli se stejným objemem. Střední průměr je jeho dvojnásobek; rovníkový průměr se může lišit. U obrů je zrychlení uvedeno v atmosféře při tlaku 1 bar.'));
    host.append(section('Oběh, rotace a osa', [
      ['Průměrná vzdálenost', distance(facts.distanceMillionKm)],
      ['Vzdálenost v AU', `${number(facts.distanceMillionKm / 149.5978707, 3)} AU`],
      ['Nejblíže Slunci', distance(facts.perihelionMillionKm)],
      ['Nejdále od Slunce', distance(facts.aphelionMillionKm)],
      ['Doba oběhu · tropický rok', days(facts.orbitalDays)],
      ['Otočení vůči hvězdám', hours(facts.rotationHours)],
      ['Sluneční den', hours(facts.solarDayHours)],
      ['Směr rotace', facts.rotationHours < 0 ? 'Retrográdní · opačný než Země' : 'Přímý · jako Země'],
      ['Sklon rotační osy', `${number(facts.tiltDeg, 3)}°`],
      ['Sklon dráhy k ekliptice', `${number(facts.inclinationDeg)}°`],
      ['Výstřednost dráhy', number(facts.eccentricity, 3)],
    ], 'AU je astronomická jednotka. Uvedená vzdálenost je hlavní poloosa dráhy, nikoli aktuální poloha v animaci. Sluneční den je interval mezi dvěma poledni; otočení vůči hvězdám je jiná veličina. Sklon osy se měří od kolmice k oběžné rovině.'));
    host.append(section('Atmosféra a teploty', [
      ['Průměrná teplota', temperature(facts.temperatureC)],
      ['Prostředí', facts.atmosphere],
    ], facts.giant ? 'Teplota odpovídá hladině atmosféry při tlaku 1 bar. Není to teplota pevného povrchu.' : 'Jde o zaokrouhlený globální průměr, nikoli aktuální počasí. Teploty se liší podle místa, denní doby a ročního období.'));
    host.append(section('Měsíce a prstence', [
      ['Potvrzené měsíce · tabulka 2025', number(facts.moons, 0)],
      ['Prstence', facts.rings ? 'Ano' : 'Ne'],
    ], 'Počty měsíců jsou snímkem tabulky NASA z 18. 3. 2025. Nové objevy je mohou změnit; nejde o živý počet.'));
  } else {
    const sun = SUN_FACTS;
    host.append(element('p', 'Hvězda · G2 V', 'facts-type'));
    host.append(rows([
      ['Střední průměr', km(sun.meanRadiusKm * 2)],
      ['Teplota fotosféry', `≈ ${temperature(sun.temperatureC)}`],
      ['Rotace na rovníku', '≈ 25 pozemských dní'],
      ['Od Země · průměr', '149,6 mil. km'],
    ], 'facts-highlights'));
    host.append(section('Velikost a vlastnosti', [
      ['Střední poloměr', km(sun.meanRadiusKm)],
      ['Střední průměr', km(sun.meanRadiusKm * 2)],
      ['Průměr vůči Zemi', `${number(sun.meanRadiusKm / PLANET_FACTS.earth.meanRadiusKm)}×`],
      ['Hmotnost', `${number(sun.massKg / 1e30, 4)} × 10³⁰ kg`],
      ['Tíhové zrychlení · rovník', `${sun.gravity} m/s²`],
      ['Složení', 'Především vodík a helium'],
    ]));
    host.append(section('Rotace a pohyb', [
      ['Rotace na rovníku', 'Přibližně 25 pozemských dní'],
      ['Rotace u pólů', 'Přibližně 36 pozemských dní'],
      ['Sklon osy vůči ekliptice', '7,25°'],
      ['Oběh kolem centra Galaxie', 'Přibližně 230 milionů let'],
    ], 'Slunce nerotuje jako tuhé těleso: rychlost závisí na zeměpisné šířce. Nemá planetární rok ani vzdálenost od Slunce; vzdálenost v přehledu je od Země.'));
    host.append(section('Teploty a atmosféra', [
      ['Fotosféra', 'Přibližně 5 500 °C'],
      ['Jádro', 'Přibližně 15 milionů °C'],
      ['Koróna', 'Až přibližně 2 miliony °C'],
    ], 'Slunce nemá pevný povrch. Viditelnou vrstvou je fotosféra; jednotlivé vrstvy mají velmi rozdílné teploty.'));
  }
  const sources = element('p', undefined, 'facts-note facts-sources');
  sources.append('Zdroje: ', sourceLink('NASA · údaje objektu', facts ? facts.source : SUN_FACTS.source), ' · ', sourceLink('NASA · ' + (facts ? 'tabulka' : 'Slunce'), facts ? FACT_SOURCES.table : FACT_SOURCES.sun), ' · ', sourceLink('význam veličin', FACT_SOURCES.notes), '. Ověřeno 30. 10. 2026.');
  host.append(sources);
}
