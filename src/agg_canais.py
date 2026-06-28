# -*- coding: utf-8 -*-
"""
agg_canais.py  (agente Psi, lane A)
Agrega o histórico unico do YouTube por CANAL para guiar a reclassificacao por IA.
Entrada : youtube_historico_unicos_2026.csv  (video_id,titulo,canal,tipo,n_visualizacoes,primeira_vez,ultima_vez)
Saidas  : canais_ranking.csv  (1 linha por canal, ordenado pelo "peso em Outros")
          agg_stats.txt        (cobertura: quantos canais cobrem X% dos unicos em Outros)
Sem mover/apagar nada. So leitura + CSV de saida.
"""
import csv, sys, os, collections

BASE = r"E:\ORGANIZACAO\_EM-ABERTO\youtube"
SRC  = os.path.join(BASE, "youtube_historico_unicos_2026.csv")
OUTR = os.path.join(BASE, "canais_ranking.csv")
OUTS = os.path.join(BASE, "agg_stats.txt")

rows = []
with open(SRC, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        rows.append(r)

def num(x):
    try: return int(x)
    except: return 0

canais = collections.defaultdict(lambda: {
    "views":0, "unicos":0, "outros_unicos":0, "outros_views":0,
    "tipos":collections.Counter(), "amostra":[]})

for r in rows:
    c = (r.get("canal") or "").strip() or "(sem canal)"
    v = num(r.get("n_visualizacoes"))
    t = (r.get("tipo") or "").strip()
    d = canais[c]
    d["views"] += v
    d["unicos"] += 1
    d["tipos"][t] += 1
    if t == "Outros":
        d["outros_unicos"] += 1
        d["outros_views"]  += v
        if len(d["amostra"]) < 8:
            d["amostra"].append((r.get("titulo") or "").strip())

# ordena pelo que mais ajuda a derrubar "Outros": unicos em Outros, depviews
ordem = sorted(canais.items(), key=lambda kv: (-kv[1]["outros_unicos"], -kv[1]["outros_views"]))

with open(OUTR, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank","canal","n_unicos","total_views","outros_unicos","outros_views",
                "tipo_dominante_atual","amostra_titulos"])
    for i,(c,d) in enumerate(ordem,1):
        dom = d["tipos"].most_common(1)[0][0] if d["tipos"] else ""
        amostra = " | ".join(d["amostra"][:8])
        w.writerow([i,c,d["unicos"],d["views"],d["outros_unicos"],d["outros_views"],dom,amostra])

# estatisticas de cobertura
tot_unicos = len(rows)
tot_outros_unicos = sum(d["outros_unicos"] for d in canais.values())
tot_canais = len(canais)
# cobertura acumulada por canais ordenados por outros_unicos
acc = 0
marcos = {50:None,100:None,200:None,300:None,500:None}
for i,(c,d) in enumerate(ordem,1):
    acc += d["outros_unicos"]
    if i in marcos:
        marcos[i] = acc

with open(OUTS,"w",encoding="utf-8") as f:
    f.write(f"Total unicos: {tot_unicos}\n")
    f.write(f"Total canais distintos: {tot_canais}\n")
    f.write(f"Total unicos em 'Outros': {tot_outros_unicos} ({100*tot_outros_unicos/tot_unicos:.1f}%)\n\n")
    f.write("Cobertura de 'Outros' pelos TOP-N canais (ordenados por outros_unicos):\n")
    for n in sorted(marcos):
        if marcos[n] is not None:
            f.write(f"  top {n:>4} canais cobrem {marcos[n]:>6} unicos-Outros "
                    f"({100*marcos[n]/tot_outros_unicos:.1f}% dos Outros)\n")
    # canais com >=5 unicos em Outros = candidatos de alto valor
    cand = [1 for c,d in ordem if d["outros_unicos"]>=5]
    f.write(f"\nCanais com >=5 unicos em 'Outros' (alvos de alto valor): {len(cand)}\n")
    cand3 = [1 for c,d in ordem if d["outros_unicos"]>=3]
    f.write(f"Canais com >=3 unicos em 'Outros': {len(cand3)}\n")

print("OK")
print(open(OUTS,encoding="utf-8").read())
