# Implementační plán: Vesmírná cesta

Datum: 29. 10. 2026  
Stav: návrh k projednání; implementace nezahájena.

## Cíl a výchozí stav

Vytvořit vizuálně působivé, přehledné české interaktivní planetárium s kvalitním zvukem. Zachovat průzkum planet, komet, galaxií, černé a červí díry. Výtvarný směr: tmavé prostředí, čitelné povrchy, jemná záře a klidné ovládání. Měřítka a vzdálenosti zůstávají ilustrativní; rozhraní to stručně vysvětlí.

Současná aplikace obsahuje 1 424 řádků v `index.html`, Three.js 0.160.0, externí textury a systémovou hlasovou syntézu. Rozbor vychází ze zdrojového kódu. Výkon a výsledný obraz dosud nebyly změřeny v prohlížeči.

## Pravidla postupu

### Povinné pohledy aplikace — doplněno 30. 10. 2026

Výchozí obrazovkou je **celkový pohled na Sluneční soustavu**, se Sluncem, všemi osmi planetami, viditelnými oběžnými drahami a planetami v pohybu. Výběr ve scéně nebo v katalogu otevře detail objektu; tlačítko Přehled vrátí celou soustavu. Návrat nerestartuje simulační čas ani nemění pauzu nebo rychlost. Přehled musí fungovat na mobilu, tabletu i notebooku v obou orientacích; kamera zabere i dráhu Neptunu a prstence Saturnu bez překrytí panely. Velikosti, vzdálenosti a rychlosti jsou ilustrativní.

Přehled a detail jsou dva samostatné povinné scénáře návrhu i ověření. [HTML návrh](docs/ui-preview.html) nyní předvádí oba: animovaný SVG přehled s funkční pauzou a rychlostí a detail Země. Produkční realizace zůstává v Three.js. Při omezení pohybu začít s pozastavenými oběhy a umožnit jejich výslovné spuštění.

### Cílová zařízení — upřesněno uživatelem

| Zařízení | Plánované prohlížeče pro ověření | Hlavní kontroly |
|---|---|---|
| Android tablet; model zatím neurčen | Chrome | Ovládání prsty, pinch zoom, posun dvěma prsty, obě orientace, scroll katalogu bez pohybu scény. Automatická kvalita musí zvládnout i slabší zařízení. |
| MacBook Air M4; velikost displeje zatím neurčena | Safari a Chrome | Trackpad i myš, plynulý zoom a otáčení, klávesnice, změna velikosti okna a škálování displeje. |
| iPhone 14 | Safari | Dotyková gesta, obě orientace, safe areas, změny výšky při zobrazení adresní lišty, přerušení a obnovení aplikace, aktivace zvuku po interakci. |

Zařízení jsou potvrzená; uvedené prohlížeče jsou výchozí testovací volba. Při prvním měření zaznamenat konkrétní verze OS a prohlížeče, skutečný viewport, DPR a model Android tabletu. Neurčený model tabletu neblokuje implementaci; blokuje pouze závěr o výkonu na tomto konkrétním zařízení. Existující screenshoty jsou emulace rozměrů v desktopovém Chrome, nikoli ověření na těchto fyzických zařízeních.

Kvalitu nevolit napevno podle názvu zařízení: používat automatický profil s ruční volbou a limitem renderovaných pixelů. Pro MacBook Air M4 cílit na 60 FPS; pro iPhone 14 a Android tablet na alespoň 30 FPS při odpovídající kvalitě, s možností 60 FPS podle měření. Ověřit také souvislý desetiminutový běh na mobilních zařízeních.

### Postup a technická pravidla

- Postupovat po dokončitelných fázích. Po každé zaznamenat změny, ověření, známé nedostatky a další krok.
- Před změnami zachovat výchozí soubory pro návrat a pořídit srovnávací záběry ze stejných pozic kamery.
- Zachovat Three.js a běžné JavaScriptové moduly. Zpočátku ponechat připnutou verzi; případný upgrade provést samostatně s kontrolou kompatibility.
- Soubory po rozdělení spouštět přes lokální HTTP server. Přímé otevření přes `file://` již nebude podporovanou cestou.
- U nových textur a audia evidovat zdroj, licenci a velikost. Upřednostnit lokální soubory; rozlišení volit podle kvality grafiky.
- Nejprve měřit, potom optimalizovat. Náročné efekty musí mít jednodušší variantu.

## Fáze 1 — Stabilní základ a srovnání

- [ ] Spustit současnou aplikaci, zaznamenat chyby konzole a projít všechny cíle navigace.
- [ ] Zachytit přehled soustavy, detail Země, galaxii a černou díru. Uložit prohlížeč, zařízení, rozlišení, dobu načtení a časy snímků.
- [ ] Rozdělit HTML, CSS, data a logiku do modulů podle níže uvedené struktury; zachovat registr cílů a existující vzhled.
- [ ] Oddělit stav výběru, simulace a nastavení od ovládání DOM, kamery a zvuku.
- [ ] Opravit přelet k pohybujícímu se cíli a přerušení přeletu při ručním ovládání či novém výběru.
- [ ] Napojit načítací obrazovku na skutečné načítání, včetně chyb a barevné náhrady při selhání textur.
- [ ] Ošetřit návrat ze skryté záložky a velký časový skok animace.

Výstup: funkčně srovnatelná aplikace s přehlednější strukturou a spolehlivou navigací.

Hotovo, když: fungují všechny původní cíle, návrat domů, přiblížení a otáčení; rychlé přepínání nezpůsobuje skoky ani výjimky. Postup lokálního spuštění je zdokumentovaný.

## Fáze 2 — Referenční grafika Země a světla

- [ ] Připravit kvalitnější barevnou mapu Země, reliéf, odlišnou drsnost oceánu a pevniny, mraky a noční světla.
- [ ] Přidat atmosférický shader se září závislou na pohledu a směru Slunce; noční světla omezit na neosvětlenou stranu.
- [ ] Oddělit rotaci povrchu Země od oběhu Měsíce.
- [ ] Zavést vykreslování přes `EffectComposer`, mírný bloom a správnou výstupní konverzi barev. Ověřit vyhlazování po zavedení postprocessingu.
- [ ] Sjednotit expozici, světlo a hvězdné pozadí. Zabránit přepalům a záření běžných povrchů.
- [ ] Zavést základní profily nízké, střední a vysoké kvality pro rozlišení renderu, textury a efekty.

Výstup: detail Země jako vzor kvality pro zbytek aplikace.

Hotovo, když: atmosféra, oceány, mraky a noční strana mají čitelně odlišný vzhled, přechody jsou stabilní při pohybu kamery a existuje porovnání před/po včetně výkonu. Tady proběhne první posouzení výtvarného směru.

## Fáze 3 — Rozhraní a ovládání

- [ ] Sjednotit barvy, typografii, rozestupy, tlačítka a stavy zaměření.
- [ ] Rozdělit katalog na Sluneční soustavu, Galaxie a Zvláštní objekty.
- [ ] Dokončit výchozí přehled celé soustavy: osm drah a obíhajících planet, výběr ve scéně, přechod na detail a návrat při zachování času, pauzy a rychlosti. Ověřit záběr celé soustavy ve všech podporovaných rozměrech.
- [ ] Doplnit kartu objektu: název, stručná zajímavost a ovládání komentáře.
- [ ] Na mobilu vytvořit posuvnou navigaci a skládací kartu; zachovat prostor pro scénu.
- [ ] Přidat pauzu, rychlost simulace a volbu kvality. Čas simulace oddělit od času přeletu a animace rozhraní.
- [ ] Doplnit ovládání klávesnicí, popisky ovládacích prvků a respektování omezení pohybu.

Výstup: jednotné rozhraní pro počítač i telefon.

Hotovo, když: všechny objekty a ovládací prvky jsou dostupné při šířkách 360, 768 a 1440 px; rozhraní se nepřekrývá. Pozastavení simulace neblokuje navigaci.

## Fáze 4 — Zvuk a český průvodce

- [ ] Vytvořit správce zvuku s oddělenou hlasitostí atmosféry, efektů a komentáře.
- [ ] Aktivovat audio po uživatelské interakci; doplnit vypnutí a ukládání nastavení.
- [ ] Připravit klidný ambient a krátké zvuky výběru, přeletu a příletu. Navázat je na skutečný stav navigace.
- [ ] Při komentáři plynule ztišit pozadí. Při změně cíle zastavit starý komentář i neplatné zvukové události.
- [ ] Připravit české texty a systém přehrávání předem vytvořených nahrávek; systémový hlas použít jako zálohu.
- [ ] Vytvořit nebo získat jednotné české nahrávky a poslechem ověřit srozumitelnost i výslovnost.
- [ ] Ošetřit skrytou záložku, nedostupné audio a chybějící český systémový hlas.

Výstup: ovladatelný zvukový doprovod a konzistentní komentáře.

Hotovo, když: zvuk se bez interakce nespustí, mute umlčí i řeč, hlasitosti se obnoví po načtení a rychlé změny výběru nevrství komentáře. Nahrávky jsou samostatná obsahová závislost: bez jejich dodání bude zvuková infrastruktura funkční, ale část s jednotným hlasem zůstane nedokončená. Případnou placenou tvorbu je nutné předem dohodnout.

## Fáze 5 — Sluneční soustava

- [ ] Přenést kvalitu materiálů na ostatní planety a Měsíc; rozlišit kamenné povrchy a plynné obry.
- [ ] Doplnit atmosféry tam, kde odpovídají objektu, a upravit mraky Venuše.
- [ ] Přepracovat Slunce: animovaný povrch, koróna a kontrolovaný bloom.
- [ ] Vylepšit Saturnovy prstence průhledností a zastíněním; nákladnější stíny omezit podle profilu kvality.
- [ ] Zjemnit kometární částice a odlišit prachový a iontový ohon.
- [ ] Doladit výchozí pohled a vzdálenost kamery pro každý objekt.

Výstup: celá soustava odpovídá kvalitě referenční Země.

Hotovo, když: každý objekt má rozpoznatelný charakter, detail i celkový přehled jsou čitelné a žádný povrch není nechtěně přepálený nebo průhledný.

## Fáze 6 — Galaxie a prostorové efekty

- [ ] Nahradit tvrdé částice měkkými hvězdami s různou velikostí a jasem; vytvořit výraznější jádra a prachové pásy galaxií.
- [ ] Mlhovinám dodat hloubku více vrstvami a jemným pohybem.
- [ ] Černé díře přidat animovaný akreční disk a shaderovou deformaci okolního obrazu. Efekt bude výtvarnou aproximací, nikoli fyzikální simulací.
- [ ] Červí díře vytvořit tunel s perspektivou a prouděním; zachovat možnost prohlížení z různých stran.
- [ ] Složitější varianty načítat nebo aktivovat podle vybraného cíle a profilu kvality.

Výstup: galaxie a zvláštní objekty působí prostorově při pohybu kamery.

Hotovo, když: efekty fungují z více úhlů, nedeformují HTML rozhraní a nezanechávají obrazové artefakty při změně cíle či velikosti okna. Slabší profil má ověřenou jednodušší variantu.

## Fáze 7 — Výkon, integrace a dokončení

- [ ] Změřit stejné pohledy a zařízení jako ve fázi 1; porovnat časy snímků, načítání a spotřebu prostředků.
- [ ] Doladit rozlišení, hustotu částic, úrovně detailu a načítání textur. Uvolňovat nahrazované GPU prostředky.
- [ ] Prověřit opakované změny cíle a kvality, návrat ze skryté záložky, selhání síťových požadavků a obnovení WebGL kontextu.
- [ ] Ověřit MacBook Air M4 (Safari a Chrome), iPhone 14 (Safari) a uživatelův Android tablet (Chrome); odlišit skutečné testování od emulace a zapsat chybějící fyzické testy.
- [ ] Ověřit klávesnici, omezený pohyb, zvuk, české texty a všechny původní interakce.
- [ ] Doplnit README se spuštěním, nastavením, známými omezeními a přehled zdrojů médií.

Výkonový cíl: přibližně 60 FPS na MacBooku Air M4 a nejméně 30 FPS na iPhonu 14 a cílovém Android tabletu při odpovídající kvalitě. Model tabletu a podmínky testu doplnit při prvním měření; cíle dosud nejsou potvrzené benchmarkem. Hodnotit také nepravidelné dlouhé snímky, ne pouze průměr.

Hotovo, když: všechny kontrolní scénáře projdou, výsledky měření jsou zaznamenané a zbývající omezení výslovně uvedená.

## Navržená struktura

```text
index.html                  vstupní HTML a import map
styles/app.css              rozhraní a responzivní pravidla
src/main.js                 inicializace a propojení modulů
src/data/                   katalog objektů a české texty
src/scene/                  renderer, světla, načítání a kvalita
src/objects/                planety, komety, galaxie, zvláštní objekty
src/shaders/                atmosféra a další vlastní efekty
src/navigation/             registr cílů a řízení kamery
src/audio/                  přehrávání, mix a komentáře
src/ui/                     katalog, karta objektu a nastavení
assets/textures/             lokální textury
assets/audio/                ambient, efekty a komentáře
docs/validation/             srovnávací záběry a výsledky kontrol
```

Adresáře vytvářet až s jejich skutečným obsahem. `AGENTS.md` ponechat beze změny; aktuální strukturu a příkazy popsat v README.

## Kontrolní body a testování

Pořadí: **1 → 2 → 3 → 4 → 5 → 6 → 7**. Základní kontrola funkčnosti a výkonu probíhá v každé fázi; poslední fáze je celková kontrola, nikoli první testování.

Vizuální změny ověřovat srovnávacími záběry při stejném nastavení. Automatické testy přidávat jen pro logiku s přínosem: přerušování navigace, škálování času a přepínání komentářů. Volbu testovacího nástroje provést při zavedení prvního takového testu.

První hmatatelný milník je dokončení fáze 2. Kompletní nový zážitek ze vzhledu rozhraní a zvuku vznikne po fázi 4. Další dvě fáze rozšíří stejnou kvalitu na celý obsah.
