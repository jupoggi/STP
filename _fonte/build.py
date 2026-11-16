import json, os, re, shutil, html
from urllib.parse import quote
SRC='/home/claude/stp/project/Proposta.dc.html'
OUT='/home/claude/export/site'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT+'/assets')
M=json.load(open('map.json'))
EXT={'image/jpeg':'jpg','image/png':'png','image/webp':'webp','image/avif':'avif','font/woff2':'woff2','font/woff':'woff','image/svg+xml':'svg'}
nome={}
for i,src in M['src'].items():
    ext=EXT.get(M['ct'].get(i),'') or os.path.splitext(src)[1].lstrip('.').lower() or 'bin'
    nome[i]=f'assets/{i}.{ext}'; shutil.copy(src, f'{OUT}/{nome[i]}')
s=open(SRC,encoding='utf-8').read()
s=re.sub(r'/_blob/([0-9a-f]{32})', lambda m: nome[m.group(1)], s)
css=re.search(r'<helmet>\s*<style>(.*?)</style>\s*</helmet>', s, re.S).group(1)
corpo=re.search(r'</helmet>(.*)</x-dc>', s, re.S).group(1)
js=re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S).group(1)
js=js.replace('sel: "", copiado: false,','sel: (function(){ try { var c = new URLSearchParams(location.search).get("c"); return c && /^\\d{3}$/.test(c) ? c : ""; } catch (e) { return ""; } })(), copiado: false,',1)
assert 'URLSearchParams' in js
SITE='https://www.salveotricolorpaulista.com.br'
GOATCOUNTER=os.environ.get('GOATCOUNTER','')  # código do site no GoatCounter, ex.: 'stp2026'
GC_TAG=(f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>' if GOATCOUNTER else '')
idx=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Salve o Tricolor Paulista · Candidatos ao Conselho Deliberativo do SPFC 2026</title>
<meta name="description" content="Sócios que querem mudar o jeito de administrar o São Paulo: democratização, transparência e responsabilidade financeira. Conheça os candidatos e monte sua cola.">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Salve o Tricolor Paulista">
<meta property="og:title" content="Salve o Tricolor Paulista · Escolha quem sempre escolheu o São Paulo">
<meta property="og:description" content="Conheça os candidatos do Salve o Tricolor Paulista ao Conselho Deliberativo e monte sua cola.">
<meta property="og:url" content="{SITE}/">
<link rel="icon" href="{nome['409e52b0f1732fe532d7f2b5d93b9605'] if '409e52b0f1732fe532d7f2b5d93b9605' in nome else ''}">
<style>{css}</style>
{GC_TAG}
</head>
<body>
<div id="stp-raiz"></div>
<template id="stp-modelo">{corpo}</template>
<script src="stp-runtime.js"></script>
<script>{js}</script>
</body>
</html>'''
open(f'{OUT}/index.html','w',encoding='utf-8').write(idx)
shutil.copy('stp-runtime.js', f'{OUT}/stp-runtime.js')
# páginas de compartilhamento
C=re.findall(r'\{num:"(\d{3})",[^\n]*', s)
os.makedirs(f'{OUT}/candidatos')
EB=re.search(r'var EBOOK = (\{.*?\n\});', s, re.S)
for linha in re.findall(r'\{num:"\d{3}",[^\n]*', s):
    n=re.search(r'num:"(\d{3})"',linha).group(1)
    ap=re.search(r'apelido:"([^"]*)"',linha).group(1)
    foto=re.search(r'foto:"([^"]*)"',linha); foto=foto.group(1) if foto else ''
    prof=re.search(r'"'+n+r'":\{"socio":"([^"]*)","prof":"([^"]*)"', s)
    fem = bool(prof and prof.group(1).startswith('Sócia'))
    cand='Candidata' if fem else 'Candidato'
    t=f'{n} · {ap} — {cand} ao Conselho Deliberativo do SPFC'
    d=(prof.group(1)+' · '+prof.group(2)) if prof else f'{cand} do Salve o Tricolor Paulista.'
    url=f'{SITE}/candidatos/{n}.html'; img=f'{SITE}/{foto}' if foto else ''
    E=lambda x: html.escape(x,quote=True)
    open(f'{OUT}/candidatos/{n}.html','w',encoding='utf-8').write(f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(t)} | Salve o Tricolor Paulista</title>
<meta name="description" content="{E(d)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="profile"><meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Salve o Tricolor Paulista">
<meta property="og:title" content="{E(t)}"><meta property="og:description" content="{E(d)}">
<meta property="og:url" content="{url}">
{f'<meta property="og:image" content="{img}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">' if img else ''}
<meta http-equiv="refresh" content="0; url=../?c={n}#candidatos">
<script>location.replace("../?c={n}#cand-{n}");</script>
</head><body><p><a href="../?c={n}">Ver o perfil de {E(ap)}</a></p></body></html>''')
print('ok', len(nome), 'assets', len(os.listdir(f'{OUT}/candidatos')),'perfis')
