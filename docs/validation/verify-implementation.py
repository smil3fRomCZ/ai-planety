"""Syntax, simulation, startup failure and real CSS layout checks in Chrome."""
import base64
import functools
import http.server
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import urllib.request
from capture import CDP, ROOT, OUTPUT, VIEWPORTS

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=server.serve_forever, daemon=True).start()
profile = Path(tempfile.mkdtemp(prefix='space-implementation-'))
process = subprocess.Popen([r'C:\Program Files\Google\Chrome\Application\chrome.exe', '--headless=new', '--no-sandbox', '--disable-gpu-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--remote-debugging-port=0', f'--user-data-dir={profile}', 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        if (profile / 'DevToolsActivePort').exists():
            break
        time.sleep(.1)
    port = (profile / 'DevToolsActivePort').read_text().splitlines()[0]
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as response:
        target = next(item for item in json.load(response) if item['type'] == 'page')
    cdp = CDP(target['webSocketDebuggerUrl'])
    cdp.call('Page.enable')
    cdp.call('Runtime.enable')
    cdp.call('Page.navigate', url=f'http://127.0.0.1:{server.server_port}/index.html')
    time.sleep(17)
    report = {'browser': cdp.call('Browser.getVersion'), 'note': 'CSS shell and pure simulation verified. CDN blocked here; no successful Three.js runtime or physical device performance measurement.'}
    report['syntax'] = {}
    for path in (ROOT / 'src').glob('*.js'):
        source = path.read_text(encoding='utf-8')
        source = '\n'.join(line for line in source.splitlines() if not line.startswith('import ')).replace('export ', '')
        report['syntax'][path.name] = cdp.evaluate(f'(() => {{ new Function({json.dumps(source)}); return true; }})()')
    state = (ROOT / 'src/state.js').read_text(encoding='utf-8').replace('export ', '')
    report['simulation'] = cdp.evaluate('(() => {' + state + '''
      const s = createSimulation();
      const normal = s.advance(.02) === .02;
      s.paused = true; const t = s.elapsed;
      const paused = s.advance(1) === 0 && s.elapsed === t;
      s.paused = false; s.speed = 5;
      const speed = s.advance(.02) === .1;
      const clamped = s.advance(100) === .25;
      return {normal, paused, speed, clamped, reducedMotion:createSimulation(true).paused};
    })()''')
    report['startup'] = cdp.evaluate("({message:document.querySelector('#loading .label').textContent, retryVisible:!document.getElementById('retry').hidden, canvas:!!document.querySelector('canvas')})")
    # Facts UI and data run independently of the network-dependent 3D module.
    fact_source = (ROOT / 'src/planet-facts.js').read_text(encoding='utf-8').replace('export ', '')
    card_source = '\n'.join(line for line in (ROOT / 'src/facts-card.js').read_text(encoding='utf-8').splitlines() if not line.startswith('import ')).replace('export ', '')
    cdp.evaluate(f'window.renderTestFacts = (() => {{ const {{ PLANET_FACTS, SUN_FACTS, FACT_SOURCES }} = (() => {{ {fact_source}\nreturn {{ PLANET_FACTS, SUN_FACTS, FACT_SOURCES }}; }})();\n{card_source}\nreturn renderFacts; }})()')
    report['facts'] = cdp.evaluate('''(() => {
      const checks = {};
      for (const id of ['mercury','venus','earth','mars','jupiter','saturn','uranus','neptune','sun']) {
        renderTestFacts(id);
        const host = document.getElementById('objectFacts');
        checks[id] = !host.hidden && host.dataset.objectId === id && host.querySelectorAll('.facts-highlights div').length === 4 && host.querySelectorAll('a').length === 3 && !/undefined|NaN|Infinity/.test(host.textContent);
      }
      renderTestFacts('venus'); checks.retrograde = document.getElementById('objectFacts').textContent.includes('Retrográdní');
      renderTestFacts('jupiter'); checks.atmosphericTemperature = document.getElementById('objectFacts').textContent.includes('hladina 1 bar');
      renderTestFacts('earth'); checks.meanDiameter = document.getElementById('objectFacts').textContent.replace(/\\s/g,'').includes('12742km');
      renderTestFacts('sun'); checks.sunDistinct = !document.getElementById('objectFacts').textContent.includes('Délka roku');
      renderTestFacts('blackhole'); checks.noStalePlanet = document.getElementById('objectFacts').hidden && document.getElementById('objectFacts').childElementCount === 0;
      renderTestFacts(null); checks.homeCleared = !document.getElementById('objectFacts').dataset.objectId;
      renderTestFacts('neptune');
      document.querySelectorAll('#objectFacts details').forEach(d => { d.open = true; });
      document.getElementById('objectCard').classList.add('expanded');
      document.getElementById('title').textContent = 'Neptun';
      document.getElementById('subtitle').textContent = 'Nejvzdálenější planeta';
      return checks;
    })()''')
    report['layouts'] = []
    # Reproduce the actual application's shell without external module execution.
    cdp.evaluate("document.getElementById('loading').remove()")
    cdp.evaluate("""(() => {
      for (const name of ['Slunce','Merkur','Venuše','Země','Mars','Jupiter','Saturn','Uran','Neptun']) {
        const b=document.createElement('button'); b.className='planet-btn';
        const t=document.createElement('div'); t.className='planet-thumb'; t.style.background='#588eae';
        const n=document.createElement('div'); n.className='planet-name'; n.textContent=name; b.append(t,n);
        document.getElementById('planetBar').append(b);
      }
    })()""")
    for name, width, height in VIEWPORTS:
        cdp.call('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=False)
        result = cdp.evaluate("""(() => {
          const regions=['#app','#catalog','#objectCard','#toolbar','#topbar'].map(s=>document.querySelector(s).getBoundingClientRect());
          return {within:regions.every(r=>r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1), overlap:regions.some((a,i)=>regions.slice(i+1).some(b=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)),overflow:document.documentElement.scrollWidth>innerWidth};
        })()""")
        result['name'] = name
        report['layouts'].append(result)
        data = cdp.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)
        (OUTPUT / f'facts-card-{name}.png').write_bytes(base64.b64decode(data['data']))
    (OUTPUT / 'facts-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    assert all(report['facts'].values()), 'Facts regression'
    assert all(v['within'] and not v['overlap'] and not v['overflow'] for v in report['layouts']), 'Layout regression'
finally:
    process.terminate()
    process.wait(timeout=10)
    server.shutdown()
