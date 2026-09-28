"""Renderiza o conteúdo Mermaid com posições fixas seguindo a referência do grupo."""
from pathlib import Path
import html
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
source = (ROOT / 'c4-containers.mmd').read_text(encoding='utf-8-sig')
nodes = {m[0]: (m[1], m[2]) for m in re.findall(r'^\s*(\w+)\[\(?"(.*?)"\)?\]:::(\w+)', source, re.M)}
edges = {(a, b): label for a, label, b in re.findall(r'^(\w+) -->\|(.*?)\| (\w+)', source, re.M)}
positions = {
    'api_gateway': (840,90,170,170),
    'srv_recarga_a': (555,355,155,170),
    'srv_validacao_a': (735,355,155,170),
    'srv_recarga_b': (915,355,155,170),
    'srv_validacao_b': (1095,355,155,170),
    'srv_telemetria': (1100,610,170,170),
    'db_cartoes_a': (555,610,150,160),
    'db_cartoes_b': (915,610,150,160),
    'db_event_log': (735,650,155,170),
    'event_bus': (930,850,170,150),
    'srv_repasse': (840,965,170,170),
    'db_events': (905,1180,170,165),
    'validador': (315,1570,170,185),
    'passageiro': (560,1600,170,170),
    'banco': (815,1570,170,185),
    'db_local': (190,410,170,180),
    'agente_sync': (190,745,170,170),
}
# Cada relação conserva o texto do Mermaid; apenas seu trajeto é fixado aqui.
routes = [
 ('passageiro','api_gateway',[(645,1600),(645,1820),(20,1820),(20,8),(945,8),(945,90)],(115,1450,200)),
 ('validador','api_gateway',[(400,1755),(400,1800),(55,1800),(55,28),(900,28),(900,90)],(310,1410,250)),
 ('api_gateway','srv_recarga_a',[(880,260),(880,300),(630,300),(630,355)],(630,325,95)),
 ('api_gateway','srv_validacao_a',[(900,260),(900,315),(810,315),(810,355)],(810,325,95)),
 ('api_gateway','srv_recarga_b',[(940,260),(940,300),(990,300),(990,355)],(990,325,95)),
 ('api_gateway','srv_validacao_b',[(960,260),(960,315),(1170,315),(1170,355)],(1170,325,95)),
 ('api_gateway','srv_telemetria',[(970,260),(970,550),(1185,550),(1185,610)],(1185,570,95)),
 ('srv_recarga_a','db_cartoes_a',[(630,525),(630,610)],(630,565,65)),
 ('srv_recarga_b','db_cartoes_b',[(990,525),(990,610)],(990,565,65)),
 ('srv_validacao_a','db_event_log',[(810,525),(810,650)],(840,585,90)),
 ('srv_validacao_b','db_event_log',[(1170,525),(1170,590),(890,590),(890,650)],(1040,570,100)),
 ('db_event_log','event_bus',[(815,820),(815,825),(1015,825),(1015,850)],(915,810,165)),
 ('srv_recarga_a','event_bus',[(710,525),(710,800),(970,800),(970,850)],(780,790,110)),
 ('srv_recarga_b','event_bus',[(990,525),(990,850)],(1030,690,80)),
 ('srv_telemetria','event_bus',[(1185,790),(1185,825),(1100,825),(1100,850)],(1150,810,100)),
 ('event_bus','srv_repasse',[(1015,1000),(1015,1020),(925,1020),(925,965)],(965,1015,120)),
 ('srv_repasse','db_events',[(955,1135),(955,1155),(990,1155),(990,1180)],(1050,1155,110)),
 ('srv_repasse','banco',[(885,1135),(885,1440),(900,1440),(900,1570)],(900,1465,125)),
 ('validador','db_local',[(315,1630),(85,1630),(85,500),(190,500)],(195,1100,200)),
 ('validador','agente_sync',[(375,1570),(375,850),(360,850)],(380,1200,165)),
 ('agente_sync','db_local',[(275,745),(275,590)],(275,665,200)),
 ('agente_sync','api_gateway',[(360,790),(485,790),(485,65),(880,65),(880,90)],(390,230,220)),
 ('event_bus','srv_recarga_a',[(930,850),(530,850),(530,550),(630,550),(630,525)],(560,810,120)),
 ('event_bus','srv_validacao_a',[(950,850),(700,850),(700,550),(810,550),(810,525)],(760,810,120)),
 ('event_bus','srv_recarga_b',[(1050,850),(1050,550),(990,550),(990,525)],(1030,810,120)),
 ('event_bus','srv_validacao_b',[(1070,850),(1270,850),(1270,550),(1170,550),(1170,525)],(1190,810,120)),
]
assert set(nodes) == set(positions), 'Há caixas sem posição definida.'
assert set(edges) == {(a,b) for a,b,_,_ in routes}, 'Há relações sem trajeto definido.'
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="1840" viewBox="0 0 1320 1840">',
 '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#222"/></marker></defs>',
 '<rect width="1320" height="1840" fill="white"/>']
def group(x,y,w,h,title,fill,stroke):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
    svg.append(f'<text x="{x+w/2}" y="{y+17}" text-anchor="middle" font-family="Arial" font-size="14">{html.escape(title)}</text>')
group(535,50,760,1320,'Nuvem Pública (Consórcio)','#f0fbfa','#70d7cd')
group(290,1510,735,285,'Sistemas e Atores Externos','#fcf4ff','#dda7ee')
group(105,355,345,600,'Borda (Dentro do Ônibus)','#fffaf0','#dbbb7a')
for a,b,points,label in routes:
    path = 'M' + ' L'.join(f'{x},{y}' for x,y in points)
    svg.append(f'<path d="{path}" fill="none" stroke="#222" stroke-width="1.5" stroke-linejoin="round" marker-end="url(#arrow)"/>')
colors={'person':('#08427B','#073B6F'),'external':('#999999','#666666'),'container':('#438DD5','#3C7FC0'),'database':('#2B72B5','#25639E')}
for key,(x,y,w,h) in positions.items():
    label,kind=nodes[key]
    fill,stroke=colors[kind]
    if kind=='database':
        svg.append(f'<path d="M{x},{y+12} A{w/2},12 0 0 1 {x+w},{y+12} L{x+w},{y+h-12} A{w/2},12 0 0 1 {x},{y+h-12} Z" fill="{fill}" stroke="{stroke}"/>')
        svg.append(f'<ellipse cx="{x+w/2}" cy="{y+12}" rx="{w/2}" ry="12" fill="{fill}" stroke="{stroke}"/>')
        ty,th=y+25,h-38
    else:
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>')
        ty,th=y,h
    svg.append(f'<foreignObject x="{x+10}" y="{ty}" width="{w-20}" height="{th}"><div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;display:flex;align-items:center;justify-content:center;text-align:center;color:white;font:14px/1.5 Arial"><div>{label}</div></div></foreignObject>')
for a,b,points,(x,y,w) in routes:
    # A posição dos rótulos é independente para mantê-los fora das caixas.
    if (a,b)==('event_bus','srv_recarga_a'):
        x,y,w=780,565,105
    label=html.escape(edges[a,b])
    svg.append(f'<foreignObject x="{x-w/2}" y="{y-22}" width="{w}" height="90"><div xmlns="http://www.w3.org/1999/xhtml" style="text-align:center;font:13px/1.3 Arial"><span style="background:#e5e5e5;padding:2px">{label}</span></div></foreignObject>')
svg.append('</svg>')
target=ROOT/'c4-containers.svg'
target.write_text('\n'.join(svg),encoding='utf-8')
with sync_playwright() as p:
    chrome_candidates = sorted((Path.home()/'.cache/puppeteer/chrome').glob('*/chrome-win64/chrome.exe'))
    chrome_candidates += sorted((Path.home()/'AppData/Local/ms-playwright').glob('chromium-*/chrome-win*/chrome.exe'))
    if not chrome_candidates:
        raise FileNotFoundError('Chromium não encontrado; execute: python -m playwright install chromium')
    browser=p.chromium.launch(executable_path=str(chrome_candidates[-1]),headless=True)
    page=browser.new_page(viewport={'width':1320,'height':1840},device_scale_factor=2)
    page.set_content('<html><body style="margin:0">'+''.join(svg)+'</body></html>')
    page.screenshot(path=str(ROOT/'c4-containers-layout.png'),full_page=True)
    browser.close()
print(f'SVG e PNG gerados; {len(nodes)} caixas e {len(routes)} relações preservadas.')
