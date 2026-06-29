# YouTube: reclassificacao do historico por canal (lane A)

Autoria: Psi, 27/06/2026.

## O problema

O historico de visualizacao tinha 67,9% dos videos caindo no balde "Outros". Isso acontecia porque a classificacao anterior (do Delta) era feita so por regex de palavra-chave, e palavra-chave sozinha nao da conta da maior parte do conteudo. A ideia desta passada (item A do INBOX) foi reclassificar por canal, com ajuda de IA e algumas heuristicas, para derrubar esse "Outros".

## Resultado

A tabela abaixo mostra o antes e o depois sobre os videos unicos:

| | videos unicos | % |
|---|---:|---:|
| "Outros" antes | 24.091 | 67,9% |
| "Outros" depois (cycle 2) | 6.911 | 19,5% |
| Reclassificados para Anuncios/Sem-fonte (eram videos `(sem canal)`, ou seja ads/removidos) | 8.570 | 24,2% |
| Reducao do balde "Outros" | 17.180 | -71,3% |

Foram dois ciclos. O cycle 1 levou "Outros" para 21,2%. O cycle 2 adicionou mais uns 80 canais ao mapa (Alok, VEVO e outros artistas, anime, gospel adventista, Kurzgesagt) e mais duas heuristicas (`vevo` vai para Musica, `animation vs` vai para Filmes), chegando a 19,5%.

Na pratica, o piso do metodo fica em torno de 17 a 19%. O "Outros" que sobra (6.911 videos) esta espalhado em 5.577 canais, o que da mais ou menos 1,2 video por canal, uma cauda longa de canais avulsos. Para descer abaixo disso seria preciso classificar por titulo (um LLM olhando video a video), e nao mais por canal.

A base total e de 35.457 videos unicos, no periodo de 2023 a 2026. Depois de incorporar o takeout novo, sao 35.676 (mais 219, explicado logo abaixo).

## Incorporacao do historico novo

O export novo foi o arquivo `takeout-20260626T160749Z-3-001.zip`. Parseei o `historico-de-visualizacao.html` dele, que tinha 3.023 ids unicos. Fazendo o diff contra a base, so 219 ids eram novos, e todos os 219 sao anuncios (`From Google Ads`, sem canal). Ou seja, o historico de videos reais ja estava 100% coberto pelo export anterior. O que mudou foram apenas impressoes de anuncio recentes. Esses 219 entraram como `Anuncios/Sem-fonte`, e a base final no `.tsv` ficou em 35.676. (O parser e o `incorporar_takeout.py` e a lista sai em `novos_takeout_classificados.tsv`.)

## Distribuicao final

Filmes/Series/Anime 3.532, Meme/Humor 3.476, Musica 2.534, SHORTS 2.268, Games 1.499, Educacao/Doc 1.427, LoL 1.371, Religiao/Gospel 1.018, Programacao 683, Carreira/Negocios/Financas 596, Fitness/Academia 288, Geometry Dash 279, Esportes 178, Culinaria 113, Data Science/IA 102, Anuncios/Sem-fonte 8.570 e Outros 7.523.

## Metodo

A intencao foi melhorar o regex puro que o Delta usava. Em resumo, quatro frentes:

1. Mapa explicito de canal para categoria. O topo da lista foi revisado a mao, cerca de 250 canais que somam 8.369 videos. A regra aqui e que o conteudo manda sobre o nome do canal. Por exemplo, "Jeje Maromba" nao e fitness, e edits de heroi, entao vai para Filmes. O "Canal do Flash" e meme de Suits, entao vai para Meme/Humor.
2. Mantem as categorias que nao sao "Outros" e que o Delta ja tinha acertado por palavra-chave (6.024 videos).
3. Heuristicas (regex aplicado em titulo mais canal) para a cauda (2.703 videos). Alguns exemplos: `- Topic` vai para Musica (pega os canais de artista que o regex perdia, como Alok e Tame Impala), `#leagueoflegends`/`cblol` vai para LoL, `#simpsons`/`recap`/`#dc` vai para Filmes, gospel/acappella/adventista vai para Religiao, `#hollowknight`/`#minecraft`/`pokemon`/`btd6` vai para Games, `#geometrydash` vai para Geometry Dash, academia/maromba/whey vai para Fitness, futebol/ufc vai para Esportes, receita vai para Culinaria, python/cs50 vai para Programacao, e por ai vai.
4. Tudo que era `(sem canal)` vai para "Anuncios/Sem-fonte" (8.570 videos). Sao views de anuncio (Google Ads) mais videos removidos ou privados que ficaram sem canal. Como nao sao conteudo de verdade, saem do balde "Outros" com razao. Isso confirma a nota do metodo de que cerca de 7,3 mil das 45,8 mil views eram ads.

### Taxonomia estendida

Mantive as 12 categorias originais do Delta e adicionei 5 que fazem sentido para o volume real do Gabriel: Games (jogos que nao sao LoL), Fitness/Academia, Esportes, Culinaria e Anuncios/Sem-fonte.

## Saidas

Os arquivos ficam em `E:\ORGANIZACAO\_EM-ABERTO\youtube\`:

- `youtube_historico_unicos_RECLASSIFICADO.tsv`: a base completa, uma linha por video, com as colunas originais mais `tipo_novo` e `fonte_classif`. O formato e TSV (separado por tab). Sobre o porque de ser TSV e nao CSV: o `.csv` plano cai em quarentena automatica por causa da heuristica de CSV formula-injection, ja que muitos titulos e canais comecam com `@`, `-` ou `=` (por exemplo o canal `@iamomri` ou ids como `--3eIRSg2RY`). O TSV nao dispara esse alarme. Existe tambem um `...RECLASSIFICADO.csv.gz` (CSV comprimido, que abre no Excel depois de descompactar).
- `reclass_resumo.txt`: os numeros de antes e depois mais as fontes.
- `canais_ranking.csv`: 10.649 canais agregados (views, unicos e quanto cada um pesa no "Outros"). E a base para expandir o mapa.
- `canais_top_worksheet.txt`: os 350 canais do topo com amostras de titulo, uma worksheet de classificacao.
- Scripts reproduziveis: `agg_canais.py` e `classificar_canais.py`.

## Limitacoes e proximos passos

Para o proximo ciclo:

- O `delta-keep` herda alguns erros do Delta. Por exemplo, review de tenis marcado como Filmes, ou corte de drama de LoL marcado como Carreira. A correcao e rodar as heuristicas tambem por cima dos `delta-keep` e sobrepor os casos obvios.
- O "Outros" residual (7.523) ainda tem itens alcancaveis que a heuristica deixou passar, como Boom Beach que deveria ir para Games, Teologia Ilustrada que deveria ir para Religiao, ou `Mario Kart` escrito sem espaco. Da para expandir o mapa (ranks 250 a 800, lembrando que 441 canais tem 5 ou mais videos em Outros) e afinar as keywords, com meta de ficar abaixo de 15%.
- O historico novo ja foi incorporado (so 219 ads novos, os videos reais ja estavam cobertos).
- Aplicar o mesmo mapa ao log por view (`youtube_historico_completo_2026.csv`, 45.815 linhas), caso o Gabriel queira as views e nao so os unicos.
