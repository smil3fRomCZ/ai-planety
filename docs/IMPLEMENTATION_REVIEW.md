# Posouzení implementačního plánu: Vesmírná cesta

Datum: 30. 10. 2026. Podklady: `IMPLEMENTATION_PLAN.md`, celý `index.html`, kontrola HTML v Chrome a oficiální dokumentace Three.js.

**Verdikt: připraveno k zahájení stabilizace, nepřipraveno k dokončení celé přestavby bez doplnění specifikace.** Plán správně rozděluje práci, zachovává registr cílů, odděluje simulaci od navigace a počítá s měřením, fallbacky i licencemi. Chybí však závazné rozložení pro jednotlivá zařízení, přesný kontrakt ovládání, rozpočty grafiky a konkrétní obsahové podklady. Současné UI má prokazatelnou chybu dostupnosti katalogu na mobilu.

[Otevřít interaktivní HTML náhled](ui-preview.html). Obsahuje notebook, tablet a mobil, variantu na šířku i malé obrazovky. Po doplnění návrhu začíná animovaným přehledem celé Sluneční soustavy a umožňuje přejít na detail. Je to návrh budoucího rozhraní s vlastní schematickou SVG grafikou, nikoli hotová implementace nové 3D grafiky. Současná aplikace zůstává beze změny; implementační plán byl doplněn o povinné scénáře přehledu a detailu.

## 1. Co je připravené a co ještě chybí

| Oblast | Stav | Co doplnit před příslušnou implementací |
|---|---|---|
| Záměr a obsah | Dobrý základ | Zachovat 16 stávajících cílů; rozhodnout o samostatném Měsíci, který je nyní pouze součástí Země. |
| Architektura | Dostatečná pro start | Určit jediný stav výběru, časů, kvality a audia; události výběr / začátek letu / přerušení / přílet; oddělit bootstrap od modulů. |
| UI a vizuální systém | V původním plánu obecné | Konkrétní layouty, rozměry, délky textů, focus, aktivní a chybové stavy. Nový HTML prototyp je návrh těchto rozhodnutí. |
| Mobil a tablet | Nedostatečně specifikované | Obě orientace, nízká výška, safe areas, dynamická výška prohlížeče, dotyková gesta, skládání a scroll panelů. |
| Notebook | Částečně | Zahrnout 1366 × 768, trackpad, klávesnici, zoom prohlížeče a rozdílné DPR. |
| Three.js a efekty | Vhodný směr | Renderovací řetězec pro každý profil, kamera podle viditelné plochy, rozpočet pixelů a textur; měření před výběrem optimalizací. |
| Textury a grafické podklady | Nehotové | Seznam souborů, licence, barevný prostor, rozlišení a varianty; test noční Země a osvětlené strany. |
| Zvuk | Závislost na obsahu | Konkrétní české texty, nahrávky, formáty, délky a licence. Infrastrukturu lze udělat dříve. |
| Ověření | Postup existuje, baseline chybí | Referenční fyzická zařízení, prohlížeče, stejné kamery, dlouhodobý běh a měřitelné podmínky dokončení. |

## 2. Nálezy v současné implementaci

### P0 — katalog na mobilu není celý dostupný

V `index.html:60` je `#planetBar` umístěný přes `left: 50%` a transformaci, ale nemá explicitní šířku. Automatické zúžení absolutně/fixně umístěného prvku zde spolu s `flex-wrap: wrap` vytvoří výrazně užší panel, než naznačuje jeho `max-width`. Stránka má zároveň `overflow: hidden`; panel nemá vlastní scroll.

Bylo provedeno **izolované ověření původního CSS**: stejných 16 tlačítek, stejná struktura náhledu a názvu, stejný oddělovač, bez načítání 3D modulů. Výsledky jsou skutečné rozměry DOM v Chrome, nikoli odhad finálního WebGL obrazu:

| Viewport v CSS px | Šířka lišty | Výška lišty | Horní hrana lišty | Důsledek |
|---|---:|---:|---:|---|
| 360 × 640 | 180 | 1740 | −1118 | Velká část katalogu nad obrazovkou. |
| 390 × 844 | 195 | 1740 | −914 | První objekty nelze z katalogu vybrat. |
| 844 × 390 | 422 | 444 | −72 | Katalog přesahuje i v orientaci na šířku. |
| 768 × 1024 | 384 | 552 | 454 | Panel zasahuje přes polovinu výšky obrazovky. |
| 1024 × 768 | 512 | 444 | 306 | Zakrývá značnou část scény a nápovědu. |
| 1366 × 768 | 683 | 336 | 414 | Tři řady ovládání a překrytá nápověda. |
| 1440 × 900 | 720 | 336 | 546 | Ani široký notebook nemá kompaktní katalog. |

Evidence: [layout-report.json](validation/layout-report.json), [mobil](validation/layout-mobile.png), [tablet](validation/layout-tablet.png), [notebook](validation/layout-notebook.png). Barvy náhledů v této reprodukci jsou zástupné; geometrie ovládacích prvků vychází z původního CSS. Pouhá kontrola horizontálního přetečení by chybu neodhalila.

### P0 — načítání nemá větev pro selhání startu

Kód skrývá overlay časovačem 400 ms po prvním renderu (`index.html:1411`), nikoli po dokončení načítání. Barevná náhrada hlavních planet již existuje, ale uživatel nedostane vysvětlení chyby. Statické importy z CDN při selhání zastaví celý modul ještě před inicializací aplikace.

V tomto prostředí vracely požadavky na Three.js a OrbitControls `net::ERR_NETWORK_ACCESS_DENIED`. Ve všech sedmi rozměrech zůstal loading a nevznikl canvas. **Tento výsledek dokládá chování při blokované síti; nedokládá závadu CDN ani nefunkčnost aplikace při běžném připojení.** Provozní render, FPS a kvalita textur tedy nebyly změřeny. Evidence: [current-report.json](validation/current-report.json).

Doplnit nezávislý bootstrap s ošetřeným dynamickým importem, stavy „načítání / připraveno / omezená grafika / chyba spuštění“, opakování a srozumitelný text. `LoadingManager` řeší načítání assetů, sám nezachytí selhání importu hlavního modulu. Pro distribuční verzi zvážit lokální kopie připnutých modulů i médií.

### P1 — kamera a gesta nejsou dostatečně definované

- `focusOn()` v `index.html:1236` počítá cílovou pozici jednou. Pohybující se planeta nebo kometa se za 1,8 sekundy přesune; sledování se připojí až po letu. Tento problém už původní plán správně zahrnuje.
- Chybí rušení přeletu při ručním ovládání. Změna výběru musí také rušit staré události zvuku a příletu.
- Vzdálenost kamery je jen násobek poloměru. Nerespektuje úzký horizontální FOV, panely ani celý Saturn s prstenci. Fit kamery musí vycházet z bounding sphere/box celého cíle a menšího z horizontálního a vertikálního FOV.
- Směr kamery se odvozuje od vektoru od Slunce ven. To geometricky vede k pohledu převážně na neosvětlenou stranu planety. Referenční detail Země má mít záměrně zvolený šikmý pohled na osvětlenou stranu s terminátorem. Jde o závěr z kódu, dosud nepotvrzený snímkem scény.
- Raycasting v `index.html:1290` sleduje jediný `mouseDown`; chybí rozlišení více pointerů a `pointercancel`. Pinch se nesmí změnit na výběr objektu při uvolnění posledního prstu.
- Po oddělení plochy scény počítat souřadnice raycasteru podle `canvas.getBoundingClientRect()`, nikoli podle celého okna. Stejný rozměr musí používat renderer, kamera i postprocessing.

### P1 — další funkční mezery

Měsíc je potomkem rotujícího mesh Země (`index.html:363`), takže dědí její rotaci; plán správně požaduje oddělení. Není samostatně registrovaným cílem. Není pauza, ovládání hlasitosti, mute ani volba kvality. `speak()` již ruší předchozí řeč, ale nemá jednotný stav zvuku. Neexistuje obsluha skryté záložky, omezeného pohybu nebo obnovy WebGL kontextu. Tlačítka jsou nativní, a proto mají základní klávesnicové ovládání; chybí však specifikace ovládání kamery, stavu výběru a návratu fokusu.

## 3. Návrh UI a ovládání pro zařízení

Uživatel následně upřesnil cílová zařízení: **Android tablet, MacBook Air M4 a iPhone 14**. Testovací matice je doplněna v [implementačním plánu](../IMPLEMENTATION_PLAN.md): Chrome na Android tabletu, Safari a Chrome na MacBooku, Safari na iPhonu. Prohlížeče jsou plánovaná výchozí volba; přesné verze a model tabletu zatím nejsou známé. Tyto fyzické testy dosud neproběhly. Model tabletu lze dodat později; pro implementaci zůstává rozhodující automatická kvalita a funkční úsporný profil.

Náhled zavádí tmavé pozadí, klidnou zelenou barvu aktivního prvku, čitelný text a minimum dekorací nad scénou. Plochy katalogu, scény a karty se nepřekrývají. Produkční canvas se má umístit do stejné plochy scény. Běžný text může být označitelný; zákaz výběru patří pouze na interaktivní scénu.

| Režim | Navržené chování |
|---|---|
| Mobil 360–699 px | Horní značka a přehled; scéna; skládací karta; kategorie a vodorovně posuvný katalog; trvale dostupná pauza, rychlost, zvuk, kvalita. |
| Tablet 700–1099 px | Úzký katalog vlevo, scéna vpravo, karta pod scénou, společné spodní ovládání. Obojí funguje dotykem. |
| Notebook od 1100 px | Katalog vlevo, scéna uprostřed, detail vpravo; panely mají vlastní scroll při malé výšce. |
| Telefon na šířku, výška do 500 px | Nízká horní/spodní lišta, katalog vlevo a stručná karta vpravo. Oba panely samostatně posuvné. |

Tyto breakpointy jsou výchozí návrh podle dostupného prostoru, nikoli rozpoznávání modelu zařízení. Tablet s klávesnicí i notebook s dotykem musí podporovat oba vstupy. Pod 700 px při nízké výšce použít další kompaktní režim nebo otevření katalogu na vyžádání; tuto krajní kombinaci sedm náhledů nepokrývá.

**Kontrakt ovládání pro doplnění plánu:**

- Jeden prst nebo levé tlačítko otáčí kamerou; dvěma prsty/gestem přiblížit; scroll katalogu nikdy neovládá scénu. Malý pohyb jednoho pointeru se vyhodnotí jako tap. Dvouprsté gesto zruší kandidáta na tap.
- Při sledování cíle vypnout nebo jasně vymezit panování, aby sledování nebojovalo s posunem uživatele. Trackpad musí mít ověřené přiblížení a rotaci.
- `Tab` prochází ovladače, `Enter`/mezerník aktivují tlačítka, `Escape` zavře panel a vrátí fokus. Ovládání kamery šipkami a `+`/`−` pouze při fokusu scény; neodchytávat je ve formulářích.
- Dotykové cíle alespoň 44 × 44 CSS px, zřetelný focus, textové jméno ikon, aktivní výběr přes ARIA. U finálního UI ověřit kontrast a 200% zoom.
- Použít `100dvh`, safe-area insety a přepočet při změně orientace. Respektovat `prefers-reduced-motion`: vynechat dlouhé přelety a pulzování, zachovat výběr a dostupnost obsahu.
- Karta obsahuje název, krátkou zajímavost, komentář a údaj o ilustrativním měřítku. Celé příběhy patří do rozbalené části. Při nedostupném audiu zůstane text komentáře.
- „Pauza“ zastaví simulační čas; kamera a UI fungují dál. Po návratu ze skryté záložky neprovádět velký skok simulace.

V prototypu je **17 položek**, protože navrhuji přidat samostatný Měsíc. Produkční minimum zůstává 16 stávajících cílů; pro Měsíc navíc použít `registerTarget()`, doplnit popis a záběr. Detaily ostatních objektů než Země jsou v náhledu výslovně zástupné. Načítání, chyba a nastavení audia ještě potřebují vlastní finální obrazovky.

**Doplnění po připomínce k chybějícímu přehledu:** první návrh chybně předváděl pouze detail Země. Nyní je výchozím pohledem Slunce s osmi planetami a osmi oběžnými drahami. Planety v SVG skutečně obíhají; pauza zastaví pohyb a rychlosti 0,5× / 1× / 5× / 10× mění animaci. Kliknutí nebo aktivace planety klávesnicí otevře detail, Přehled vrací soustavu se zachovaným časem a nastavením. Při `prefers-reduced-motion` začíná pohyb pozastavený. Galerie má přepínač „Celá soustava / Detail Země“. Měsíc není devátou planetou v přehledu; zůstává v katalogu. Výchozí pohled a návrat do něj jsou nyní explicitním požadavkem implementačního plánu.

## 4. Jak účelně využít Three.js

Maximalizovat vizuální přínos při stabilním ovládání a rozumné spotřebě. Vysoké vytížení GPU samo o sobě není cíl.

**Co už aplikace využívá:** `BufferGeometry`, `Points`, `MeshStandardMaterial`, procedurální `CanvasTexture`, sprity, hierarchii objektů, raycaster, OrbitControls a tone mapping. Staticky z konfigurace vychází přibližně 24 570 bodových částic: 6 000 hvězd pozadí, třikrát 4 500 hvězd a 1 500 prachových bodů galaxií, dva ohony po 160 a 250 částic červí díry. To je inventura, nikoli důkaz výkonového problému. Stejně tak absence `dispose()` v jednorázově postavené scéně sama neprokazuje únik.

| Priorita | Využití Three.js | Konkrétní přínos a hranice |
|---|---|---|
| P0 | Renderer a kamera podle skutečné plochy | `ResizeObserver`, synchronizace canvas/composer, omezení počtu renderovaných pixelů, fit celého objektu. |
| P1 | PBR povrch + atmosférický shader | Země: albedo, normal/bump, roughness, mraky, noční světla podle směru Slunce. Samostatná data pro průhlednost mraků. |
| P1 | Postprocessing | `RenderPass → volitelný UnrealBloomPass → OutputPass`; konkrétní vyhlazování zvolit po porovnání. Nízký profil může renderovat přímo. |
| P1 | Materiály a barvy | Barevné mapy sRGB, normal/roughness/alpha mapy jako data bez barevné konverze. Kontrolovat shaderové výstupy a nedělat tone mapping dvakrát. |
| P1 | LOD a cílené načítání | Detailní geometrii a textury potřebuje hlavně vybraný objekt; náročné speciální efekty aktivovat v jeho okolí. |
| P2 | Částicový shader | Měkké body, odlišné velikosti a jasy. Pohyb přes uniform času může omezit CPU aktualizace; u současných 570 pohybovaných bodů nejprve změřit přínos. |
| P2 | Render target pro černou díru | Omezená deformace obrazu scény a akreční disk; HTML UI zůstane mimo efekt. Úsporná varianta bez deformace. |
| P2 | Perspektivní červí díra | Skutečná geometrie tunelu s animovaným materiálem; jednodušší varianta pro slabší hardware. |
| Podle měření | Instancing, komprese, preload shaderů | Instancing pro mnoho stejných objektů se stejným materiálem, např. případné asteroidy. Devět různých planet není samo o sobě důvod. KTX2 až s asset pipeline a kompatibilními transkodéry. |

Barevná a výstupní pipeline vychází z [Three.js Color Management](https://threejs.org/manual/pages/color-management.html) a [Post Processing](https://threejs.org/manual/pages/post-processing.html). Existence `OutputPass` byla ověřena přímo ve [zdroji r160](https://github.com/mrdoob/three.js/blob/r160/examples/jsm/postprocessing/OutputPass.js). Pro první fáze zachovat **0.160.0** a všechny addony ze stejné verze; obecná současná dokumentace není zárukou kompatibility všech nových API.

Oficiální [průvodce responzivním renderem](https://threejs.org/manual/pages/responsive.html) popisuje omezení fyzického rozlišení, důležité zvlášť při vysokém DPR. [InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html) je určen pro opakování stejné geometrie a materiálu. Volba těchto optimalizací pro tuto aplikaci je doporučení z analýzy její struktury, nikoli již změřený zisk.

### Výchozí rozpočty k ověření ve fázi 1–2

| Parametr | Úsporná | Vyvážená | Vysoká |
|---|---|---|---|
| Maximální renderované pixely | 1,0 milionu | 2,0 milionu | 3,0 milionu |
| Horní mez DPR | 1 | 1,5 | 2 |
| Textury povrchu | Do 1K | Do 2K pro detail | Do 4K pouze pro vybraný detail |
| Geometrie koule | Přibližně 32 segmentů | 48 | 64 |
| Částice | Základní hustota | Střední hustota | Vyšší hustota dle měření |
| Atmosféra | Jednoduchá | Osvětlený shader | Stejný shader s vyšší kvalitou |
| Bloom / deformace | Vypnuto | Jemný bloom; deformace volitelná | Omezené efekty podle cíle |
| Cílová plynulost | 30 FPS na referenčním mobilu | 30–60 FPS dle zařízení | 60 FPS na referenčním notebooku |

**Jde o navržené startovní limity, ne výsledky benchmarku.** Auto nesmí odvozovat kvalitu jen ze šířky okna. Začít konzervativně, sledovat stabilní časy snímků a měnit kvalitu s hysterezí, nikoli každý snímek. Ruční volbu uložit; nereagovat na jednotlivý dlouhý snímek při načítání snížením celé scény.

Pro představu: jedna rozbalená 4096² RGBA8 textura s mipmapami spotřebuje přibližně 85 MiB; JPEG na disku může být mnohem menší. Počítat také render targets, depth a další mapy. `renderer.info` pomůže sledovat počty a draw calls, ale neposkytuje přesný celkový GPU rozpočet v bajtech. Při více passech kontrolovat reset statistik; viz [WebGLRenderer.info](https://threejs.org/docs/pages/WebGLRenderer.html#info).

Navržená měřicí brána: po zahřátí zaznamenat alespoň 30 sekund stejného pohledu, medián a p95 intervalu snímků, dlouhé záseky, draw calls, trojúhelníky a počty prostředků. Výchozí cíl p95 přibližně do 33,3 ms na mobilu a 16,7 ms na notebooku následně potvrdit na referenčním hardware. Interval `requestAnimationFrame` není přímé měření GPU času. Přidat alespoň desetiminutový běh na reálném mobilu kvůli zahřívání a opakované změny kvality kvůli uvolňování prostředků.

## 5. Doporučené doplnění pořadí implementace

Není potřeba zahodit sedm původních fází. Doplnit krátkou specifikaci před první fází a přenést minimální responzivní kostru před referenční grafiku, aby se Země ladila ve skutečné ploše scény.

1. **Doplnění specifikace:** přijmout/upravit layouty z náhledu, určit referenční zařízení, stavy načítání a chyb, ovládání a manifest médií. Výstup: konkrétní rozsah včetně rozhodnutí o Měsíci.
2. **Fáze 1:** baseline, oprava navigace, bootstrap, načítání a časů. Nejprve záloha, následně rozdělení modulů. Základní dostupný katalog vyřešit již zde.
3. **Fáze 2 + základ fáze 3:** responzivní plocha scény a profily kvality, potom referenční Země a postprocessing. Kontrola obrazu i na úsporném profilu.
4. **Dokončení fáze 3:** plné UI, gesta, fokus, omezený pohyb, přehled soustavy a chybové obrazovky.
5. **Fáze 4:** zvukový správce a integrace komentářů. Dodání nahrávek vést jako samostatnou obsahovou podmínku dokončení.
6. **Fáze 5–6:** rozšíření grafiky na ostatní cíle v rámci již ověřených rozpočtů.
7. **Fáze 7:** porovnání s baseline, dlouhodobý běh, reálná zařízení a dokumentace. Základní kontroly probíhají průběžně.

### Akceptační podmínky, které doplnit do původního plánu

- [ ] Všechny původní cíle jsou dostupné na všech sedmi referenčních viewports; dlouhé názvy nepřekrývají ovládání.
- [ ] Výchozí přehled zabírá Slunce i všech osm drah a obíhajících planet. Návrat z detailu zachová simulační čas, pauzu a rychlost. Ověřit přehled i detail odděleně na všech zařízeních.
- [ ] Výběr → přelet → ruční přerušení → jiný výběr → přehled nevyvolá skok ani starý příletový zvuk.
- [ ] Pinch, `pointercancel`, scroll katalogu a rotace zařízení nevyvolají náhodný výběr.
- [ ] Pauza zastaví simulaci, ale kamera zůstane ovladatelná.
- [ ] Selhání importu, textury, audia i WebGL má srozumitelný výsledek; loading nezůstane bez vysvětlení navždy.
- [ ] Ověřit obnovení kontextu, návrat ze skryté záložky a opakované přepínání kvality.
- [ ] Primárně Safari a Chrome na MacBooku Air M4, Safari na iPhonu 14 a Chrome na uživatelově Android tabletu. Uvést přesný model tabletu a verze OS/prohlížečů; emulaci evidovat odděleně. Další platformy jsou rozšíření testovací matice.
- [ ] Ověřit safe areas, adresní lištu mobilního prohlížeče, 200% zoom, klávesnici, čtečku a omezený pohyb.
- [ ] Výkonové cíle jsou potvrzené na konkrétních zařízeních; asset manifest má licence a rozpočty.

## 6. Co bylo skutečně ověřeno v tomto výstupu

**Prohlížeč:** headless Chrome 156.0.8078.74, Windows, DPR 1, softwarové vykreslování. Rozměry viewportů jsou emulované; nešlo o test telefonu nebo tabletu.

- HTML návrh se načetl bez síťových závislostí a bez zaznamenaných chyb konzole/sítě.
- Sedm rozměrů: 360 × 640, 390 × 844, 844 × 390, 768 × 1024, 1024 × 768, 1366 × 768 a 1440 × 900.
- V každém rozměru ověřeno přepnutí všech 17 navržených položek, změna stavu zvuku a rozbalení karty. Panely přehledu i detailu zůstaly v okně a nepřekrývaly se; bez horizontálního přetečení stránky.
- Doplněný přehled ověřen na osm drah a devět těles včetně Slunce, skutečnou změnu poloh, zastavení poloh při pauze, zrychlení animace a přechod planeta → detail → přehled bez resetu pozastaveného času. Ověřeno pozastavení při preferenci omezeného pohybu. Jde o animaci SVG prototypu; fyzikální simulace, produkční Three.js a audio tím ověřené nejsou.
- Ověřeno přepínání rozměrů v galerii; vizuálně zkontrolovány hlavní náhledy a telefon na šířku.
- Původní CSS ověřeno izolovaně se 16 položkami. Úplný start původní aplikace zablokovala síťová politika prostředí; screenshoty `current-*` zachycují pouze loading.

Evidence: [preview-report.json](validation/preview-report.json), [postup kontroly](validation/README.md). Skutečné FPS, dotykový hardware, Safari, kvalita rendereru, zvuk, reálné safe areas a úplná přístupnost zůstávají k ověření v implementaci.

| Náhled | Soubor |
|---|---|
| Přehled soustavy — mobil | [390 × 844](validation/preview-system-mobile.png) · [360 × 640](validation/preview-system-mobile-small.png) · [844 × 390](validation/preview-system-mobile-landscape.png) |
| Přehled soustavy — tablet | [768 × 1024](validation/preview-system-tablet.png) · [1024 × 768](validation/preview-system-tablet-landscape.png) |
| Přehled soustavy — notebook | [1440 × 900](validation/preview-system-notebook.png) · [1366 × 768](validation/preview-system-notebook-small.png) |
| Mobil | [390 × 844](validation/preview-mobile.png) · [360 × 640](validation/preview-mobile-small.png) · [844 × 390](validation/preview-mobile-landscape.png) |
| Tablet | [768 × 1024](validation/preview-tablet.png) · [1024 × 768](validation/preview-tablet-landscape.png) |
| Notebook | [1440 × 900](validation/preview-notebook.png) · [1366 × 768](validation/preview-notebook-small.png) |

Prvním dalším implementačním krokem má být stabilní start, dostupný katalog a opravená navigace. Potom lze bezpečně hodnotit vizuální přínos nové Země a náročnějších efektů.
