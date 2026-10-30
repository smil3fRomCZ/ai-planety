"""Local Chrome viewport audit; Python standard library only. Not a device benchmark."""
import base64
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(__file__).resolve().parent
VIEWPORTS = [('mobile', 390, 844), ('mobile-small', 360, 640),
             ('mobile-landscape', 844, 390), ('tablet', 768, 1024),
             ('tablet-landscape', 1024, 768), ('notebook', 1440, 900),
             ('notebook-small', 1366, 768)]


class CDP:
    def __init__(self, url):
        parsed = urlparse(url)
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=30)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f'GET {parsed.path} HTTP/1.1\r\nHost: {parsed.netloc}\r\n'
                           f'Upgrade: websocket\r\nConnection: Upgrade\r\n'
                           f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        header = b''
        while not header.endswith(b'\r\n\r\n'):
            header += self.read(1)
        if not header.startswith(b'HTTP/1.1 101 '):
            raise RuntimeError(header.decode())
        self.counter = 0
        self.events = []

    def read(self, count):
        data = b''
        while len(data) < count:
            chunk = self.sock.recv(count - len(data))
            if not chunk:
                raise EOFError('Chrome disconnected')
            data += chunk
        return data

    def send(self, payload, opcode=1):
        mask = os.urandom(4)
        size = len(payload)
        prefix = bytes([128 | opcode])
        prefix += bytes([128 | size]) if size < 126 else (bytes([254]) + struct.pack('!H', size) if size < 65536 else bytes([255]) + struct.pack('!Q', size))
        self.sock.sendall(prefix + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def message(self):
        payload = b''
        while True:
            first, second = self.read(2)
            size = second & 127
            if size == 126:
                size = struct.unpack('!H', self.read(2))[0]
            elif size == 127:
                size = struct.unpack('!Q', self.read(8))[0]
            mask = self.read(4) if second & 128 else None
            part = self.read(size)
            if mask:
                part = bytes(b ^ mask[i % 4] for i, b in enumerate(part))
            if first & 15 == 9:
                self.send(part, 10)
                continue
            if first & 15 == 8:
                raise EOFError('WebSocket closed')
            payload += part
            if first & 128:
                return json.loads(payload)

    def call(self, method, **params):
        self.counter += 1
        self.send(json.dumps({'id': self.counter, 'method': method, 'params': params}).encode())
        while True:
            result = self.message()
            if result.get('id') == self.counter:
                if 'error' in result:
                    raise RuntimeError(result['error'])
                return result.get('result', {})
            self.events.append(result)

    def evaluate(self, expression):
        result = self.call('Runtime.evaluate', expression=expression, returnByValue=True, awaitPromise=True)
        if 'exceptionDetails' in result:
            raise RuntimeError(result['exceptionDetails'])
        return result['result'].get('value')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'current'
    if mode not in ['current', 'layout', 'preview']:
        raise SystemExit('Use: capture.py [current|layout|preview]')
    chrome = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    profile = tempfile.mkdtemp(prefix='space-audit-')
    process = subprocess.Popen([str(chrome), '--headless=new', '--no-sandbox', '--disable-gpu-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-first-run', '--no-default-browser-check',
                                '--remote-debugging-port=0', f'--user-data-dir={profile}', 'about:blank'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        active_port = Path(profile) / 'DevToolsActivePort'
        for _ in range(100):
            if active_port.exists():
                break
            time.sleep(.1)
        port = active_port.read_text().splitlines()[0]
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/json') as response:
            target = next(item for item in json.load(response) if item['type'] == 'page')
        cdp = CDP(target['webSocketDebuggerUrl'])
        cdp.call('Page.enable')
        cdp.call('Runtime.enable')
        cdp.call('Log.enable')
        cdp.call('Network.enable')
        report = {'mode': mode, 'browser': cdp.call('Browser.getVersion'), 'viewports': [],
                  'note': 'Headless Chrome viewport emulation at DPR 1 with software rendering; not real mobile hardware or GPU performance measurement. Layout mode reconstructs the 16 catalog buttons with original CSS, without loading Three.js.'}
        path = (ROOT / 'index.html').as_uri() if mode in ['current', 'layout'] else (ROOT / 'docs/ui-preview.html').as_uri() + '?screen=1'
        for name, width, height in VIEWPORTS:
            cdp.call('Emulation.setDeviceMetricsOverride', width=width, height=height, deviceScaleFactor=1, mobile=False)
            navigation = cdp.call('Page.navigate', url=path)
            time.sleep(4 if mode == 'current' else .5)
            if mode == 'layout':
                html = (ROOT / 'index.html').read_text(encoding='utf-8').split('<script type="importmap">')[0] + '</body></html>'
                cdp.call('Page.setDocumentContent', frameId=navigation['frameId'], html=html)
                cdp.evaluate("""(() => {
                  document.getElementById('loading').remove();
                  const names = ['Slunce','Merkur','Venuše','Země','Mars','Jupiter','Saturn','Uran','Neptun','Kometa','Kometa','Č. díra','M101','M81','M83','Červí díra'];
                  names.forEach((name, i) => {
                    if (i === 9) {
                      const sep = document.createElement('div');
                      sep.style.cssText = 'width: 2px; background: rgba(108, 182, 255, 0.3); margin: 6px 4px; border-radius: 2px;';
                      document.getElementById('planetBar').append(sep);
                    }
                    const button = document.createElement('button'); button.className = 'planet-btn';
                    const thumb = document.createElement('div'); thumb.className = 'planet-thumb'; thumb.style.background = '#345777';
                    const label = document.createElement('div'); label.className = 'planet-name'; label.textContent = name;
                    button.append(thumb, label); document.getElementById('planetBar').append(button);
                  });
                  document.getElementById('title').textContent = 'Země'; document.getElementById('title').classList.add('visible');
                  document.getElementById('subtitle').textContent = 'Náš domov'; document.getElementById('subtitle').classList.add('visible');
                })()""")
            if mode == 'current':
                cdp.evaluate("document.querySelector('[data-id=earth]')?.click()")
                time.sleep(2)
            metrics = cdp.evaluate("""(() => {
              const rect = el => { const r = el.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; };
              const selectors = ['#planetBar', '#title', '#hint', '.topbar', '.catalog', '.object-card', '.toolbar', '.scene-window'];
              return {url:location.href, ready:document.readyState, title:document.title, width: innerWidth, height: innerHeight, overflow: document.documentElement.scrollWidth > innerWidth,
                canvas: !!document.querySelector('canvas'), loadingHidden: document.querySelector('#loading')?.classList.contains('hidden'),
                buttons: document.querySelectorAll('#planetBar button').length,
                regions: Object.fromEntries(selectors.flatMap(s => document.querySelector(s) ? [[s,rect(document.querySelector(s))]]:[]))};
            })()""")
            data = cdp.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)
            filename = f'preview-system-{name}.png' if mode == 'preview' else f'{mode}-{name}.png'
            (OUTPUT / filename).write_bytes(base64.b64decode(data['data']))
            report['viewports'].append({'name': name, 'screenshot': filename, **metrics})
            if mode == 'preview':
                report['viewports'][-1]['systemChecks'] = cdp.evaluate("""(async () => {
                  const art = document.querySelector('.system-art');
                  const pause = document.getElementById('pause');
                  const speed = document.getElementById('speed');
                  const wait = () => new Promise(resolve => setTimeout(resolve, 140));
                  const t = () => Number(art.dataset.time);
                  const position = () => document.querySelector('[data-planet="Země"]').getAttribute('transform');
                  const initialPosition = position();
                  const start = t(); await wait(); const moving = t() > start && position() !== initialPosition;
                  pause.click(); const stopped = t(); const stoppedPosition = position(); await wait(); const frozen = t() === stopped && position() === stoppedPosition;
                  const before = document.querySelector('[data-planet="Země"]').getAttribute('transform');
                  document.querySelector('[data-planet="Země"]').dispatchEvent(new MouseEvent('click'));
                  const detail = document.getElementById('object-name').textContent === 'Země' && !document.querySelector('.scene-window').classList.contains('overview');
                  document.querySelector('.home').click();
                  const home = document.querySelector('.scene-window').classList.contains('overview') && document.getElementById('object-name').textContent === 'Sluneční soustava';
                  const retained = t() === stopped && document.querySelector('[data-planet="Země"]').getAttribute('transform') === before;
                  speed.value = '1'; speed.dispatchEvent(new Event('change')); pause.click();
                  const slowStart = t(); await wait(); const slow = t() - slowStart;
                  speed.value = '10'; speed.dispatchEvent(new Event('change'));
                  const fastStart = t(); await wait(); const fast = t() - fastStart;
                  pause.click(); speed.value = '1'; speed.dispatchEvent(new Event('change'));
                  const regions = ['.topbar','.catalog','.object-card','.toolbar','.scene-window'].map(s => document.querySelector(s).getBoundingClientRect());
                  const within = regions.every(r => r.x >= 0 && r.y >= 0 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1);
                  const overlap = regions.some((a,i) => regions.slice(i+1).some(b => Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1));
                  pause.click();
                  return {orbitCount:document.querySelectorAll('.system-orbit').length, bodyCount:document.querySelectorAll('.system-node').length, moving, frozen, detail, home, retained, speedChanged:fast>slow*4, speedRatio:fast/slow, panelsWithinViewport:within, panelsOverlap:overlap};
                })()""")
                report['viewports'][-1]['interactionChecks'] = cdp.evaluate("""(() => {
                  const checks = [];
                  for (const category of document.querySelectorAll('.category')) {
                    category.click();
                    for (const button of document.querySelectorAll('.object-button')) {
                      button.click(); checks.push(document.getElementById('object-name').textContent === button.dataset.name && button.getAttribute('aria-pressed') === 'true');
                    }
                  }
                  document.querySelector('[data-category=solar]').click();
                  [...document.querySelectorAll('.object-button')].find(b => b.dataset.name === 'Země').click();
                  const pause = document.getElementById('pause'); pause.click();
                  const paused = pause.getAttribute('aria-pressed') === 'true'; pause.click();
                  const sound = document.getElementById('sound'); sound.click();
                  const enabled = sound.getAttribute('aria-pressed') === 'true'; sound.click();
                  const details = document.querySelector('.details-toggle'); details.click();
                  const expanded = details.getAttribute('aria-expanded') === 'true';
                  const regions = ['.topbar','.catalog','.object-card','.toolbar','.scene-window'].map(s => document.querySelector(s).getBoundingClientRect());
                  const within = regions.every(r => r.x >= 0 && r.y >= 0 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1);
                  const overlaps = regions.some((a,i) => regions.slice(i+1).some(b => Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1));
                  details.click();
                  return {selectedObjects: checks.length, allSelectionsPass: checks.every(Boolean), pause:paused, sound:enabled, details:expanded, expandedPanelsWithinViewport:within, expandedPanelsOverlap:overlaps};
                })()""")
                cdp.evaluate("document.querySelector('.toast').textContent = ''")
                data = cdp.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)
                (OUTPUT / f'preview-{name}.png').write_bytes(base64.b64decode(data['data']))
            print(json.dumps(report['viewports'][-1]), flush=True)
        if mode == 'preview':
            cdp.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-reduced-motion', 'value': 'reduce'}])
            cdp.call('Page.navigate', url=path)
            time.sleep(.3)
            report['reducedMotion'] = cdp.evaluate("document.getElementById('pause').getAttribute('aria-pressed') === 'true'")
            cdp.call('Emulation.setEmulatedMedia', features=[])
            cdp.call('Emulation.setDeviceMetricsOverride', width=1440, height=1100, deviceScaleFactor=1, mobile=False)
            cdp.call('Page.navigate', url=(ROOT / 'docs/ui-preview.html').as_uri())
            time.sleep(1)
            report['overview'] = cdp.evaluate("""(() => {
              const results = [];
              for (const value of ['portrait','landscape','compact']) {
                const select = document.getElementById('orientation'); select.value = value; select.dispatchEvent(new Event('change'));
                results.push({value,frames:[...document.querySelectorAll('iframe')].map(f => ({width:f.style.width,height:f.style.height}))});
              }
              document.getElementById('orientation').value = 'portrait';
              document.getElementById('orientation').dispatchEvent(new Event('change'));
              return {variants:results, iframeCount:document.querySelectorAll('iframe').length, overflow:document.documentElement.scrollWidth>innerWidth};
            })()""")
            data = cdp.call('Page.captureScreenshot', format='png', captureBeyondViewport=False)
            (OUTPUT / 'preview-overview.png').write_bytes(base64.b64decode(data['data']))
        report['events'] = [event for event in cdp.events if event.get('method') in
                            ['Runtime.exceptionThrown', 'Log.entryAdded', 'Network.loadingFailed']]
        (OUTPUT / f'{mode}-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        cdp.sock.close()
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == '__main__':
    main()
