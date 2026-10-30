# Ověření analýzy a návrhu UI

Datum: 30. 10. 2026. Výstupy patří k [analýze](../IMPLEMENTATION_REVIEW.md) a [HTML náhledu](../ui-preview.html).

Potvrzená cílová zařízení: Android tablet (model dosud neurčen), MacBook Air M4 a iPhone 14. Plánované fyzické kontroly: Chrome na tabletu, Safari a Chrome na MacBooku a Safari na iPhonu. Níže uložená evidence pochází pouze z desktopového Chrome na Windows; ověření na cílových zařízeních zatím neproběhlo.

## Otevření návrhu

`docs/ui-preview.html` lze otevřít přímo v prohlížeči; žádné CDN ani instalace nejsou potřeba. Nabízí mobil, tablet a notebook, variantu na šířku i menší obrazovky. Pro samostatné rozložení aktuálního okna otevřít `ui-preview.html?screen=1`.

Náhled je HTML/CSS/SVG prototyp. Začíná celkovým pohledem na Slunce, osm oběžných drah a osm planet v pohybu. Pauza a volba rychlosti ovládají skutečnou SVG animaci; oběžné doby, rozměry a vzdálenosti jsou ilustrativní. Planetu lze vybrat ze scény i katalogu a tlačítkem Přehled se vrátit. V galerii lze zvolit přehled nebo detail Země pro všechna zařízení najednou. Při omezeném pohybu je animace po načtení pozastavena.

Země je původní schematická ilustrace vytvořená v SVG; nejsou použita externí obrazová média. Skutečný komentář a Three.js v prototypu neběží. Detaily ostatních objektů mají zástupnou ilustraci. Volby zvuku a kvality předvádějí pouze stav rozhraní.

## Soubory evidence

- `facts-report.json` a `facts-card-*.png`: kontrola datových karet osmi planet a Slunce a rozbaleného Neptunu v sedmi viewports. Kontroluje také vyčištění obsahu při přepnutí na jiný typ objektu či přehled, retrográdní rotaci, teplotní metodiku a střední průměr Země. Karty se vykreslují skutečným modulem aplikace, ale 3D scéna při těchto kontrolách neběží. Spustit `python docs/validation/verify-implementation.py`; skript při regresi vrací chybu.

- `preview-system-*.png`: celkový pohled na Sluneční soustavu z Chrome v sedmi rozměrech.
- `preview-mobile*.png`, `preview-tablet*.png`, `preview-notebook*.png`: odpovídající detaily Země; `preview-overview.png` ukazuje začátek galerie.
- `preview-report.json`: rozměry panelů přehledu, kontroly pohybu, pauzy, rychlosti, přechodů a ostatních stavů UI, preference omezeného pohybu a zaznamenané chyby. `speedRatio` je poměr změn simulačního času ve dvou krátkých intervalech; kvůli časování snímků není přesným benchmarkem násobku rychlosti.
- `layout-*.png` a `layout-report.json`: izolovaná reprodukce původního CSS s původním počtem a strukturou tlačítek, bez 3D scény. Náhledy objektů mají zástupnou barvu. Tyto snímky dokládají problém rozložení, nikoli vzhled kompletní aplikace.
- `current-*.png` a `current-report.json`: pokus o běžný start původní aplikace. Požadavky na unpkg blokovalo prostředí (`ERR_NETWORK_ACCESS_DENIED`), zůstal loading a nevznikl canvas. Nejde o referenční render scény.

## Reprodukce

Skript `capture.py` používá standardní knihovnu Pythonu a lokální Chrome na Windows. Chrome se spouští s dočasným samostatným profilem a softwarovým rendererem; nejde o měření GPU výkonu. Skript nemění `index.html`. Režim `layout` nahrazuje pouze obsah dočasné stránky v prohlížeči.

```powershell
python docs/validation/capture.py preview
python docs/validation/capture.py layout
python docs/validation/capture.py current
```

Výstupy daného režimu se přepíší. Prohlížeč se na konci ukončí; dočasný profil `space-audit-*` zůstává v systémovém adresáři dočasných souborů. Cestu k Chrome lze upravit v `capture.py`.

Všechny snímky mají DPR 1 a emulované rozměry CSS viewportu. Skript neprovádí test reálných dotykových gest, přístupnosti se čtečkou, Safari, fyzického GPU, výdrže baterie, safe areas ani zvuku. Stavy ovládání ověřuje programovým kliknutím. Při skutečné implementaci doplnit ruční kontroly a fyzická zařízení podle analýzy.
