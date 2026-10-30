# Vesmírná cesta

Český interaktivní průzkumník vesmíru v Three.js 0.160.0. První implementační etapa propojuje původní 3D obsah s responzivním katalogem a ovládáním simulace.

## Spuštění

Z kořene projektu spusťte:

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

Otevřete `http://localhost:8000`. Soubory jsou nyní rozdělené do modulů, proto používejte HTTP server. Three.js a textury vyžadují internet. Při nedostupnosti modulů se zobrazí informace a možnost opakování; při selhání textur zůstávají barevné povrchy. Náhled návrhu je v `docs/ui-preview.html`.

## Ovládání

- Tažení myší nebo jedním prstem otáčí pohled; kolečko a gesto dvěma prsty přibližují.
- Pravé tlačítko nebo gesto dvěma prsty posouvá přehled. V detailu je panování vypnuté kvůli sledování cíle.
- Katalog a kliknutí na objekt zahájí přelet. Ruční ovládání přelet a sledování přeruší.
- Tlačítko domu vrací celou soustavu; zachová pauzu a rychlost.
- Pauza zastavuje simulaci, kamera funguje dál. Rychlosti: 0,5×, 1×, 5× a 10×.
- Na zaměřeném canvasu šipky otáčejí a `+`/`−` přibližují. Ovladače jsou dostupné klávesou Tab.
- Hlas je po načtení vypnutý; lze zapnout vyslovování názvů nebo explicitně přehrát název objektu.
- Volba kvality zatím mění rozlišení renderu a limit počtu pixelů; Auto používá konzervativní střední limit. Adaptivní měření výkonu přijde v další etapě.

## Struktura a stav

Karty osmi planet a Slunce obsahují skutečné údaje v českém formátu: poloměr a průměr, srovnání se Zemí, vzdálenosti, teploty, oběh, rotaci, sklon osy, hmotnost, gravitaci, atmosféru a prstence. Základní čtveřici údajů doplňují nativní rozbalovací sekce. Na mobilu je obsah pod tlačítkem Více a má omezenou výšku s vlastním posouváním. Po přepnutí na jiný typ objektu nebo na přehled se planetární údaje odstraní.

Data jsou v `src/planet-facts.js`, společné vykreslování v `src/facts-card.js`. Poloměry jsou objemové střední, průměry jsou jejich dvojnásobkem; nejde o rovníkové průměry. Doba oběhu je v této datové sadě tropický rok. Rotace vůči hvězdám a sluneční den jsou uvedeny odděleně. Teploty obrů odpovídají hladině atmosféry při tlaku 1 bar. Srovnání průměru se Zemí a AU se počítají ze skutečných dat, nezávisle na scéně.

Každá karta odkazuje na příslušný NASA Fact Sheet, přehledovou tabulku a vysvětlení veličin. Použita zaokrouhlená planetární tabulka verze 18. 3. 2025 a střední poloměry z jednotlivých fact sheets; ověřeno 30. 10. 2026. Počty měsíců jsou výslovně označené jako snímek tabulky z roku 2025, nikoli aktuální živé počty. Slunce má vlastní údaje a zdroje. Nejnovější rozšířená kontrola zapisuje `docs/validation/facts-report.json` a snímky rozbalené karty `facts-card-*.png`.

`index.html` obsahuje rozhraní a import map; `styles/` vzhled a rozložení; `src/bodies.js` konfiguraci planet; `src/state.js` čas simulace; `src/ui.js` ovládání; `src/main.js` původní objekty, jejich animaci a řízení scény. Další dělení scény bude pokračovat s grafickými etapami. `src/bootstrap.js` ošetřuje start a chyby importu.

Záloha původní verze je v `docs/validation/baseline/`. Historické analýzy a screenshoty v `docs/validation/` popisují konkrétní fázi, nikoli automaticky současnou aplikaci.

Ověření první implementace: `python docs/validation/verify-implementation.py`. Kontroluje syntaxi modulů, čas simulace, chování startu bez CDN a rozložení skutečného HTML/CSS v sedmi viewports. Screenshoty `implementation-shell-*` ukazují pouze rozhraní s reprodukovanými tlačítky, bez 3D renderu. Výsledky jsou v `implementation-report.json`.

V pracovním prostředí je síť CDN blokovaná, proto dosud nebyl ověřen úspěšný WebGL běh upravené aplikace. Před označením fáze 1 za hotovou zbývá projít všechny cíle a gesta v běžném prohlížeči s internetem. Fyzické testy na Android tabletu, MacBooku Air M4 a iPhonu 14 dosud neproběhly. Grafické fáze, ambient, jednotné české nahrávky a adaptivní kvalita zůstávají v implementačním plánu.

## Externí zdroje

- Three.js a OrbitControls: připnutá verze 0.160.0 z unpkg, projekt Three.js, licence MIT: https://github.com/mrdoob/three.js/blob/r160/LICENSE.
- Původní textury: https://github.com/jeromeetienne/threex.planets/tree/master/images, načítané z jsDelivr. URL zůstávají převzaté z výchozí aplikace; rozměry, velikosti a licence jednotlivých obrazových podkladů je potřeba ověřit před jejich lokálním distribuováním.
- Procedurální efekty jsou generované původním kódem aplikace. Nové obrazové ani zvukové soubory zatím nebyly přidány.
