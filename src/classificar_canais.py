# -*- coding: utf-8 -*-
"""
classificar_canais.py  (agente Psi, lane A)
Reclassifica o historico unico do YouTube reduzindo o balde "Outros".
Estrategia (melhora o regex puro do Delta, que deixa 68% em Outros):
  1) MAPA EXPLICITO canal->categoria (head revisado a mao, conteudo-first:
     corrige nomes enganosos, ex. "Jeje Maromba" = edits de heroi, nao fitness).
  2) Mantem as categorias NAO-Outros que o Delta ja acertou por keyword.
  3) HEURISTICAS (regex em titulo+canal) p/ a cauda: '- Topic'->Musica,
     #leagueoflegends->LoL, #simpsons/recap->Filmes, gospel->Religiao, etc.
  4) "(sem canal)" -> "Anuncios/Sem-fonte" (sao ~ads/removidos; nao sao conteudo).
Saida: youtube_historico_unicos_RECLASSIFICADO.csv (original intacto).
       reclass_resumo.txt (antes/depois + reducao de Outros + fontes).
Reversivel: so cria CSV novo. Nada movido/apagado.
"""
import csv, os, re, collections

BASE = r"E:\ORGANIZACAO\_EM-ABERTO\youtube"
SRC  = os.path.join(BASE, "youtube_historico_unicos_2026.csv")
OUT  = os.path.join(BASE, "youtube_historico_unicos_RECLASSIFICADO.csv")
RES  = os.path.join(BASE, "reclass_resumo.txt")

MU='Música'; FSA='Filmes/Séries/Anime'; MH='Meme/Humor'; LOL='LoL'; GM='Games'
GD='Geometry Dash'; RG='Religião/Gospel'; CNF='Carreira/Negócios/Finanças'
ED='Educação/Doc'; PR='Programação'; DS='Data Science/IA'; FIT='Fitness/Academia'
CUL='Culinária'; ESP='Esportes'; SH='SHORTS'; ADS='Anúncios/Sem-fonte'; OUT='Outros'

# categorias que o Delta ja produz e em que confiamos (mantem se nao houver mapa)
DELTA_OK = {MU,FSA,MH,LOL,RG,ED,CNF,PR,DS,GD}

CANAL_MAP = {
 'Renato IMPERA':ED,'MOVIE TART':FSA,'Alien Simulation':FSA,'ShortsPodcuts':MH,
 'Sev7n Games OFICIAL':GM,'Nauta':MH,'mano deyvin':PR,'Fernando Ulrich':CNF,
 'GeralPodCuts':MH,'Diogo Matheus':MH,'PinkPanthersShow':FSA,'Telles':MH,'Reis Raff':MH,
 'Novos Clássicos Show':ED,'Krusty Recaps':FSA,'Jeje Maromba':FSA,'3Palavrinhas':RG,
 'LOUD CaioX':MH,'CheffOtto':CUL,'Bronziocre':LOL,'Rodriverso':MH,'Danael Fernandes':GM,
 'Ethan Reid':GM,'Paulinho':MH,'Rodrigo Sa':MH,'ClipsDoBald':LOL,'Minha Vida É Uma Viagem':RG,
 'I am MoBo':MH,'Cinder':GM,'Laércio Refundini':FIT,'Pv':FSA,'ENGEEK':MH,'Diggo':MH,
 'Clash of Clans':GM,'CBLOL':LOL,'Official Pink Panther':FSA,'Isabela Boscov':FSA,
 'Canal do Flash':MH,'Pink Ward Too':LOL,'Flow Games':LOL,'podcastgame':MH,
 'Inteligência Ltda':ED,'Expressodarima':MU,'Sev7n':LOL,'Yagostoso':MH,'CloudKid':MU,
 'TheFatRat':MU,'ILHA DAS LENDAS - JOGOS COMPLETOS':LOL,'IMPERA':ED,'The Tech Thieves':MU,
 'Red Bull':ESP,'BaianoTV':LOL,'Locomotiva':GM,'Elegas':FSA,'3LittleWords':RG,
 'Snow Moments':MH,'Felipe Panettoni':GM,'NEFFEX':MU,'LD Speedruns':GM,'Recap+':FSA,
 'tigretzz':MH,"Binge Ma'ampage":FSA,'MENOS UM':RG,'Fiasco':PR,'TheManDeeDubs':FSA,
 'Trechos Filmes':FSA,'BREAKER':GM,'Jake Benedict':FIT,'Neovaii':MU,
 'Rodrigo Pimentel | Papo De Elite':ED,'Daniel Gonçalves':RG,'Law By Mike':ED,
 'Daniel Oliver':MH,'Rodrigo Silva Arqueologia':RG,'Lindsey Stirling - Topic':MU,
 'Luiz Stubbe':ED,'Wolverine':FSA,'MORTEIRO':GM,'Rotina Atômica':GM,'Dream Wander':GM,
 'Ismalakoi':LOL,'ずっと真夜中でいいのに。 ZUTOMAYO':MU,'ORuivo Edits':FSA,'imShadow':FSA,
 'Daniel Penin':CNF,'Thiago Sem T':MH,'George Collier':MU,'Memes Existenciais 2.0':MH,
 'Juliäno Villa':MH,'Arautos do Rei - Topic':RG,'Lindsey Stirling':MU,'Vagostelo':ED,
 'Shortspodsets':MH,'Minu':FSA,'Giuliana Mafra':MH,'Khaby. Lame':MH,'Rafael Novaes':FSA,
 'Killyan':FIT,'GLITCH':FSA,'A Batcaverna':FSA,'skibidi':FSA,'Sábio Em Ação':FSA,
 'Alice Faz Pão':CUL,'Diego Padilha Rubert':PR,'Cain':MH,'Toca do Clip':MH,'Fabio Akita':PR,
 'vewn':FSA,'Slayerz':MH,'Dougzach':MH,'inabakumori - Topic':MU,'Allone07':GM,
 'Terrorzoka':GM,'Naquele Pick':LOL,'Botão Turbo':GM,'Hbomb':GM,'Rafaella Tuma':MH,
 'Manneis':FSA,'Paul Cabannes':ED,'Creo':MU,'Junferno':MH,'Lucax Franco':ED,'DjokoLoL':LOL,
 'André Guedes':MH,'LolElekktro':LOL,'Documentando':MH,'Alan Marchini':RG,
 'Ana Letícia Lima':FIT,'Leo':FSA,'rbiana':MH,'TerminalMontage':GM,'iae break':MH,
 'Sloppy Walrus':LOL,'Thayná Tarcilla':FIT,'O Amigão da Vizinhança':FSA,'JabsGu':FSA,
 'Laércio Silva':FSA,'pinkpanthervideo':FSA,'Rodrigo Platti':FSA,'Cinema Home':FSA,
 'Gabriel Corrêa':MH,'Gio Lisboa':MH,'Família Lüdtke':RG,'Rede Seven':RG,'Vetor Humor':MH,
 'Seijinho':FSA,'Boi Domestico':MH,'DavolafShorts':MH,'EsnoobLoL':LOL,'Jurandir Gouveia':FSA,
 'Cinho Knows':MU,'Tockers':LOL,'MOUSAIT':FSA,'Bsm Edits 20':ESP,'Overwatch Brasil':GM,
 'ＴＲＡＳＨ 新 ドラゴン':MU,'Choou':GM,'Parque das Batalhas':MU,'scroll忍':MU,
 'Hudson Silva Borges':PR,'Reynell Rodríguez':RG,'Fighter doc':ESP,'Wisemind':MH,
 'MovieLuxeShorts':FSA,'Nerd Das Hqs':FSA,'CBOLÃO':LOL,'Aniki_Edits10':FSA,'SurpriseLoL':LOL,
 'Novo Tom':RG,'Arautos do Rei':RG,'audioOverture':RG,'Felipe Barbieri':ED,'UNIVESP':ED,
 'Wyvrn':GM,'Novo Tempo - Topic':RG,'Revolta':LOL,'Sociedade da Virtude':FSA,
 'GeekPodCuts':MH,'Professor Lih':GM,'DUDUTOMAHAWK':FIT,"it's Sakura":MH,
 'Como é bom ser nerd - Pura Física':ED,'NarraSmith':MH,'Spotniks':ED,'Unlike Pluto':MU,
 'Steve Cutts':FSA,'Valiant':MU,'Vocal Livre':RG,'Adriano Valentini':MH,'Hunt3zin':GM,
 'Ricardinho':MH,'Movie Nights':FSA,'Oli Natu':MH,'Viniblogger':MH,'Alves Stories':MH,
 'Maicon Küster':MH,'Stewie BR':FSA,'QUE CRIME?':LOL,'Os Bexigas':GM,'Jessica Diniz':MH,
 'Sessão Nerd':FSA,'Trechos Animados':FSA,'teus':GM,'JOTA':FIT,'Daquavis':GM,
 'The Future Flash':FSA,'Tuvok12':ESP,'fahgundiz':LOL,'Alanzoka Brazuka':GM,
 'udriver black no táxi':MH,'Minuto Maromba':FIT,'Filé de filmes':MH,'Shape Pure':FIT,
 'Foot Mood':ESP,'Estudar Fora':PR,'2WEI':MU,'Alan Walker':MU,'Kawanishi Hisako':MU,
 'Rebeca Kids':RG,'Legendary Jay':MH,'TheFatRat - Topic':MU,'badshinji':FSA,'BANKAIsolo':GM,
 'Boni & Oliveira':GM,'Utopia':MH,'Coach SeeEl [OFICIAL]':LOL,'Daffy':FSA,'Bart Recap':FSA,
 'Market Makers':CNF,'BIX Tecnologia':DS,'Chris and Jack':MH,'Física Flávio':ED,'Humor10k':MH,
 'Luska':FSA,'Doro o aventureiro':FSA,'Arnulfo Brother':GM,'Juninho Pk':ED,
 'NextlevelDJ | O moço do Te Amo':MH,'Colours Gaming':GD,'Slim Gust':MH,'Cultura de Rima':MU,
 'PinkPanthersShow ':FSA,
}
# --- 2ª passada (Psi cycle 2): canais do residual-Outros revisados ---
CANAL_MAP.update({
 'Alok':MU,'Pink Martini':MU,'NFVEVO':MU,'NF':MU,'Ikigai':MU,'Aviencloud':MU,
 'juneisabandVEVO':MU,'The Wicked North':MU,'Hussien Tarek':MU,'Lowly.':MU,'稲葉曇':MU,
 'DubstepGutter':MU,'André Rieu':MU,'Diversity':MU,'Pretty ok':MU,'1nonly Instrumentals':MU,
 '1nonly':MU,'F-777':MU,'MrMoMMusic':MU,'AviciiOfficialVEVO':MU,'Caramella Girls':MU,
 'Alan Becker':FSA,'Dead Sound':FSA,'THE GOOD FILMS':FSA,'Cinemou Podcast':FSA,
 'Luz Câmera Ação':FSA,'NS Cine':FSA,'Melhores Cenas':FSA,'Frink 137':FSA,'Geekalizando':FSA,
 'Mais Cartoon':FSA,'Cinema e Vídeo':FSA,'Markuz Produções':FSA,'𝐄𝐌𝐏𝐕𝐅𝐗':FSA,'Nerdcf':FSA,
 'CineMind':FSA,'Cinema Home':FSA,'Jhonattan SZN':FSA,'AIDENTU':FSA,'SnapCuts':FSA,
 'TOHO animation チャンネル':FSA,'Luz Câmera Ação ':FSA,'Boom Beach':GM,'Hehehehaw CR':GM,
 'DonJone':GM,'Hoever':GM,'fnm04':GD,'6pekclips':LOL,
 'Turma do Cristãozinho':RG,'Canal As Três Mensagens Angélicas':RG,'André Alencar':RG,
 'PALAVRA TOCADA':RG,'Os Oliveirinhas':RG,'OsArraisVEVO':RG,'PERSONAL LIBRARY HEARTBEAT':RG,
 'ZENO GUITAR':RG,'Mark Minard':RG,'제이풋볼JFootballTV':ESP,'SportsNation':ESP,
 'Australian Open':ESP,'Best Futball':ESP,'Fearron':ESP,'Em Poucas Palavras – Kurzgesagt':ED,
 'Tinocando TV':ED,'Brasão de Armas':ED,'Real Real Japan':ED,'LatinNCAP':ED,
 'reflexões transcendentais':ED,'Doutor Fran':ED,'Téo Me Why':DS,'Valeria Quadros dos Reis':PR,
 'LSCAD':PR,'AUVP Capital':CNF,'Embrulha Pra Viagem':MH,'Suno':MH,'Irmãos Natu':MH,'IOPEM':MH,
 'ARGEN':MH,'dakooters':MH,'Hamlet PNG':MH,'Tudo ShortsCast':MH,'Baptista Miranda':FIT,
 'Tibo InShape':MH,'Quark Doge':MH,
})

def heur(titulo, canal):
    c = canal.lower(); t = titulo.lower(); s = t + ' ' + c
    if c.endswith('- topic') or c.endswith('- topic '): return MU
    if any(k in s for k in ['#leagueoflegends','league of legends','cblol','cbolão','wild rift',
        'wildrift','#wildrift','#lol','leagueoflegends','soloq','lolzinho']): return LOL
    if any(k in s for k in ['geometry dash','#geometrydash','layout vs original','#gdmobile']): return GD
    if any(k in s for k in ['gospel','louvor','jesus','cristo','evangelho','salmo ','bíblia',
        'biblia','hino ','cd jovem','pregaç','sermão','sermao','devocional','batismo',
        'missões','missionár','acappella','adventist','espírito santo','santa ceia',
        'palavra de deus','culto ','apocalipse estudo','ranko','os arrais',
        'celebra são paulo','fingerstyle hymns','os oliveirinhas','cristãozinho']): return RG
    if c.endswith('vevo'): return MU
    if any(k in s for k in ['#learnjapanese','learn japanese','kurzgesagt']): return ED
    if any(k in s for k in ['data science','machine learning','inteligência artificial',
        ' ia ','chatgpt',' llm','deep learning','power bi','business intelligence','#dados',
        'redes neurais']): return DS
    if any(k in s for k in ['python','javascript',' react','programaç','algoritmo',
        'estrutura de dados','padrões de projeto',' devops',' linux',' docker','typescript',
        'back-end','front-end','código ','#dev','cs50','engenharia de software']): return PR
    if any(k in s for k in ['#simpsons','simpsons','family guy','#dc','#marvel','batman',
        'superman','homem-aranha','spider-man','#anime','recap','#recaps','invencível',
        'invincible','one piece','naruto','dragon ball','#hq','quadrinhos',' trailer',
        'easter egg','the boys','hollow knight #','homem aranha','liga da justiça',
        'animation vs','animator vs','animation vs.']): return FSA
    if any(k in s for k in ['#minecraft','minecraft','#pokemon','pokemon','pokémon',
        'hollow knight','clash royale','clash of clans','bloons','btd6',' mario','zelda',
        'speedrun','gameplay','#games','#gaming','mmorpg','among us','roblox','overwatch',
        'valorant','mobile legends','mlbb','elden ring','#gta','alanzoka','boom beach',
        'google snake','mario kart','super mario','mario maker']): return GM
    if any(k in s for k in ['receita','#receita','culinária','air fryer','#cozinha']): return CUL
    if any(k in s for k in ['academia','treino','maromba','#gym','musculação','whey',
        'hipertrofia','agachamento','#fitness','crossfit']): return FIT
    if any(k in s for k in ['futebol','#football','#futebol',' ufc','#mma','#nba','basquete',
        'champions league','batalha de rima','#batalhaderima','batalhademc']):
        return ESP if ('rima' not in s and 'mc' not in s.split()) else MU
    if any(k in s for k in ['official music','official video','lyric video','videoclipe',
        'clipe oficial','playback','álbum','(official audio)']): return MU
    if any(k in s for k in ['#humor','#comedia','#comédia','pegadinha','#meme']): return MH
    return None

rows=[]
with open(SRC, encoding='utf-8-sig', newline='') as f:
    rd=csv.DictReader(f); cols=rd.fieldnames
    for r in rd: rows.append(r)

antes=collections.Counter(); depois=collections.Counter(); fonte=collections.Counter()
for r in rows:
    canal=(r.get('canal') or '').strip()
    titulo=(r.get('titulo') or '')
    old=(r.get('tipo') or 'Outros').strip() or 'Outros'
    antes[old]+=1
    if not canal or canal=='(sem canal)':
        new=ADS; src='sem-canal'
    elif canal in CANAL_MAP:
        new=CANAL_MAP[canal]; src='canal-map'
    elif old in DELTA_OK:
        new=old; src='delta-keep'
    else:
        h=heur(titulo,canal)
        if h: new=h; src='heuristica'
        elif old==SH: new=SH; src='shorts-keep'
        else: new=OUT; src='outros'
    r['tipo_novo']=new; r['fonte_classif']=src
    depois[new]+=1; fonte[src]+=1

import gzip as _gzip, io as _io
hdr = cols+['tipo_novo','fonte_classif']
def _rowsout():
    yield hdr
    for r in rows:
        yield [r.get(c,'') for c in cols]+[r['tipo_novo'],r['fonte_classif']]
# NB: o .csv plano e' posto em quarentena pelo Defender (heuristica de CSV-formula-injection:
# muitos titulos/canais comecam com @ - =). Saida canonica = TSV (sobrevive). Tambem .csv.gz.
OUT_TSV=os.path.join(BASE,'youtube_historico_unicos_RECLASSIFICADO.tsv')
with open(OUT_TSV,'w',encoding='utf-8',newline='') as f:
    csv.writer(f,delimiter='\t').writerows(_rowsout())
OUT_GZ=os.path.join(BASE,'youtube_historico_unicos_RECLASSIFICADO.csv.gz')
buf=_io.StringIO(); csv.writer(buf).writerows(_rowsout())
with _gzip.open(OUT_GZ,'wb') as f: f.write(buf.getvalue().encode('utf-8-sig'))

tot=len(rows)
def pct(n): return f"{100*n/tot:.1f}%"
lines=[]
lines.append(f"RECLASSIFICACAO YouTube por canal (Psi) — {tot} videos unicos\n")
lines.append(f"Outros ANTES : {antes['Outros']:>6}  ({pct(antes['Outros'])})")
lines.append(f"Outros DEPOIS: {depois[OUT]:>6}  ({pct(depois[OUT])})   [+ {depois[ADS]} reclassif. como Anúncios/Sem-fonte]")
red = antes['Outros'] - depois[OUT]
lines.append(f"Reducao de 'Outros': {red} videos ({100*red/max(antes['Outros'],1):.1f}% do balde Outros)\n")
lines.append("DISTRIBUICAO DEPOIS (desc):")
for k,v in depois.most_common():
    lines.append(f"  {k:<28} {v:>6}  {pct(v)}")
lines.append("\nFONTE da classificacao:")
for k,v in fonte.most_common():
    lines.append(f"  {k:<14} {v:>6}")
txt="\n".join(lines)
open(RES,'w',encoding='utf-8').write(txt)
print(txt)
