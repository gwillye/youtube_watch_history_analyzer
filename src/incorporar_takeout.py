# -*- coding: utf-8 -*-
"""
incorporar_takeout.py  (agente Psi, lane A)
Incorpora o historico NOVO (E:\\takeout-20260626T160749Z-3-001.zip) ao base ja
reclassificado. Parseia o HTML de visualizacao (gotchas do doc de referencia:
\\xa0, verbo 'Watched', ads 'Google Ads', data pt-BR, canal apos o titulo),
pega so os video_ids NOVOS (nao presentes no unicos), classifica com a MESMA
logica (importa classificar_canais) e ANEXA ao RECLASSIFICADO.tsv.
Reversivel: nao mexe nos inputs; gera novos_takeout_classificados.tsv e
reescreve o RECLASSIFICADO.tsv (base intacta em _2026.csv).
"""
import zipfile, re, csv, os, html, collections
import classificar_canais as cc   # reusa constantes + CANAL_MAP + heur + DELTA_OK (idempotente)

BASE = cc.BASE
ZIP  = r"E:\takeout-20260626T160749Z-3-001.zip"
TSV  = os.path.join(BASE, "youtube_historico_unicos_RECLASSIFICADO.tsv")
NOV  = os.path.join(BASE, "novos_takeout_classificados.tsv")

MESES = {'jan':'01','fev':'02','mar':'03','abr':'04','mai':'05','jun':'06',
         'jul':'07','ago':'08','set':'09','out':'10','nov':'11','dez':'12'}

def classify(canal, titulo, old='Outros'):
    c=(canal or '').strip()
    if not c or c=='(sem canal)': return cc.ADS,'sem-canal'
    if c in cc.CANAL_MAP: return cc.CANAL_MAP[c],'canal-map'
    if old in cc.DELTA_OK: return old,'delta-keep'
    h=cc.heur(titulo,c)
    if h: return h,'heuristica'
    if old==cc.SH: return cc.SH,'shorts-keep'
    return cc.OUT,'outros'

# --- ids ja existentes ---
ex=set()
for r in csv.DictReader(open(os.path.join(BASE,'youtube_historico_unicos_2026.csv'),encoding='utf-8-sig')):
    ex.add(r['video_id'])

# --- parse takeout novo ---
z=zipfile.ZipFile(ZIP)
name=[e for e in z.namelist() if e.lower().endswith('.html')][0]
doc=z.read(name).decode('utf-8','replace').replace('\xa0',' ')
segs=re.split(r'<div class="content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1">', doc)
acc={}   # id -> dict(titulo,canal,views,datas[])
for seg in segs[1:]:
    m=re.search(r'watch\?v=([A-Za-z0-9_-]{11})">(.*?)</a>', seg, re.S)
    if not m: continue
    vid=m.group(1); titulo=html.unescape(m.group(2)).strip()
    cm=re.search(r'youtube\.com/(?:channel/[^"]+|@[^"]+|user/[^"]+)">(.*?)</a>', seg, re.S)
    canal=html.unescape(cm.group(1)).strip() if cm else '(sem canal)'
    if 'Google Ads' in seg: canal='(sem canal)'
    dm=re.search(r'(\d{1,2}) de ([a-zç]+)\.? de (\d{4})', seg)
    data=''
    if dm:
        mes=MESES.get(dm.group(2)[:3].lower(),'01')
        data=f"{dm.group(3)}-{mes}-{int(dm.group(1)):02d}"
    d=acc.setdefault(vid,{'titulo':titulo,'canal':canal,'views':0,'datas':[]})
    d['views']+=1
    if data: d['datas'].append(data)

novos={vid:d for vid,d in acc.items() if vid not in ex}
print(f"takeout novo: {len(acc)} ids unicos | NOVOS (nao no base): {len(novos)}")

# --- classifica novos + escreve relatorio + anexa ao RECLASSIFICADO.tsv ---
hdr=['video_id','titulo','canal','tipo','n_visualizacoes','primeira_vez','ultima_vez','tipo_novo','fonte_classif']
fonte=collections.Counter(); cat=collections.Counter()
newrows=[]
for vid,d in novos.items():
    datas=sorted(d['datas']); pv=datas[0] if datas else ''; uv=datas[-1] if datas else ''
    new,src=classify(d['canal'], d['titulo'], 'Outros')
    fonte[src]+=1; cat[new]+=1
    newrows.append([vid,d['titulo'],d['canal'],'Outros',d['views'],pv,uv,new,src])

with open(NOV,'w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerow(hdr); w.writerows(newrows)

# anexa ao TSV base (que cc acabou de (re)gerar)
existing=list(csv.reader(open(TSV,encoding='utf-8'),delimiter='\t'))
base_n=len(existing)-1
with open(TSV,'w',encoding='utf-8',newline='') as f:
    w=csv.writer(f,delimiter='\t'); w.writerows(existing); w.writerows(newrows)

print(f"base {base_n} + novos {len(newrows)} = {base_n+len(newrows)} no RECLASSIFICADO.tsv")
print("categorias dos novos:", dict(cat.most_common()))
print("fontes dos novos:", dict(fonte.most_common()))
