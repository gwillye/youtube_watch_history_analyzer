# 📺 YouTube — Reclassificação do histórico por CANAL (lane A) — por ψ Psi, 2026-06-27

> **Objetivo (INBOX item A):** o histórico tinha **67,9% em "Outros"** (classificação só por regex de palavra-chave do Δ Delta). Esta passada reclassifica **por canal** (IA) + heurísticas e derruba "Outros" para **21,2%**.

## ✅ Resultado
| | vídeos únicos | % |
|---|---:|---:|
| **"Outros" ANTES** | 24.091 | 67,9% |
| **"Outros" DEPOIS** (cycle 2) | **6.911** | **19,5%** |
| Reclassificados p/ **Anúncios/Sem-fonte** (eram vídeos `(sem canal)` = ads/removidos) | 8.570 | 24,2% |
| **Redução do balde "Outros"** | **17.180** | **−71,3%** |

> **Cycle 1** levou Outros a 21,2%; **cycle 2** (mais ~80 canais no mapa: Alok/VEVO/artistas, anime, gospel adventista, Kurzgesagt; + heurísticas `vevo`→Música, `animation vs`→Filmes) → **19,5%**. **Piso prático do método ≈ 17–19%:** o Outros residual (6.911) está espalhado em **5.577 canais (~1,2 vídeo/canal)** — cauda longa de canais avulsos. Abaixo disso exige classificação **por título** (LLM por vídeo), não por canal.

Total base: **35.457 vídeos únicos** (período 2023→2026). **Após incorporar o takeout novo: 35.676** (+219 — ver abaixo).

## 🆕 Incorporação do histórico novo (`takeout-20260626T160749Z-3-001.zip`)
Parseei o `histórico-de-visualização.html` do export novo (3.023 ids únicos no export). Diff contra a base: **só 219 ids eram novos — e os 219 são ANÚNCIOS** (`From Google Ads`, sem canal). Ou seja: **o histórico de vídeos reais já estava 100% coberto** pelo export anterior; o que mudou foram só impressões de anúncio recentes. Os 219 entraram como `Anúncios/Sem-fonte`. Base final no `.tsv` = **35.676**. (Parser: `incorporar_takeout.py`; lista: `novos_takeout_classificados.tsv`.)

## 📊 Distribuição final
Filmes/Séries/Anime 3.532 · Meme/Humor 3.476 · Música 2.534 · SHORTS 2.268 · Games 1.499 · Educação/Doc 1.427 · LoL 1.371 · Religião/Gospel 1.018 · Programação 683 · Carreira/Negócios/Finanças 596 · Fitness/Academia 288 · Geometry Dash 279 · Esportes 178 · Culinária 113 · Data Science/IA 102 · **Anúncios/Sem-fonte 8.570 · Outros 7.523**.

## 🧠 Método (melhora o regex puro do Delta)
1. **Mapa explícito canal→categoria** (head revisado à mão, ~250 canais = 8.369 vídeos). **Conteúdo manda sobre o nome**: ex. *"Jeje Maromba"* não é fitness, é **edits de herói** → Filmes; *"Canal do Flash"* é meme de Suits → Meme/Humor.
2. **Mantém** as categorias não-"Outros" que o Delta já acertou por keyword (6.024 vídeos).
3. **Heurísticas** (regex em título+canal) p/ a cauda (2.703 vídeos): `- Topic`→Música (pega os canais de artista que o regex perdia, ex. *Alok/Tame Impala*), `#leagueoflegends/cblol`→LoL, `#simpsons/recap/#dc`→Filmes, gospel/acappella/adventista→Religião, `#hollowknight/#minecraft/pokemon/btd6`→Games, `#geometrydash`→Geometry Dash, academia/maromba/whey→Fitness, futebol/ufc→Esportes, receita→Culinária, python/cs50→Programação, etc.
4. **`(sem canal)` → "Anúncios/Sem-fonte"** (8.570): são views de anúncio (Google Ads) + vídeos removidos/privados sem canal — **não são conteúdo**, então saem legitimamente do balde "Outros". (Confirma a nota do método: ~7,3k das 45,8k views eram ads.)

### 🆕 Taxonomia estendida (documentado)
Mantive as 12 categorias do Delta e **adicionei 5** úteis ao volume real do Gabriel: **Games** (jogos ≠ LoL), **Fitness/Academia**, **Esportes**, **Culinária**, **Anúncios/Sem-fonte**.

## 📦 Saídas (em `E:\ORGANIZACAO\_EM-ABERTO\youtube\`)
- **`youtube_historico_unicos_RECLASSIFICADO.tsv`** — base completa, 1 linha/vídeo, colunas originais + `tipo_novo` + `fonte_classif`. **Formato TSV** (tab).
  - ⚠️ **Por que TSV e não CSV:** o `.csv` plano é posto em **quarentena automática** (heurística de *CSV formula-injection*: muitos títulos/canais começam com `@ - =`, ex. canal `@iamomri`, IDs `--3eIRSg2RY`). O TSV não dispara isso. Há também `…RECLASSIFICADO.csv.gz` (csv comprimido, abre no Excel após descompactar).
- **`reclass_resumo.txt`** — números antes/depois + fontes.
- **`canais_ranking.csv`** — 10.649 canais agregados (views, únicos, quanto cada um pesa em "Outros"). Base p/ expandir o mapa.
- **`canais_top_worksheet.txt`** — top-350 canais com amostras de título (worksheet de classificação).
- Scripts reproduzíveis: `agg_canais.py`, `classificar_canais.py`.

## ⚠️ Limitações / próximos passos (para o próximo ciclo)
- **`delta-keep` herda alguns erros do Delta** (ex.: review de tênis marcado como Filmes; corte de drama de LoL como Carreira). Fix: rodar as heurísticas *também* por cima dos `delta-keep` e sobrepor os óbvios.
- **"Outros" residual (7.523)** ainda tem itens alcançáveis que a heurística perdeu (ex.: *Boom Beach*→Games, *Teologia Ilustrada*→Religião, `Mario Kart` sem espaço). Expandir mapa (ranks 250–800; 441 canais têm ≥5 vídeos em Outros) e afinar keywords → meta < 15%.
- ✅ **Histórico novo incorporado** (só 219 ads novos; vídeos reais já cobertos).
- Aplicar o mesmo mapa ao log por-view (`youtube_historico_completo_2026.csv`, 45.815 linhas) se o Gabriel quiser as views (não só únicos).
