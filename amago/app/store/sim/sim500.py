"""Simulación Monte Carlo del mes de lanzamiento de AMAGO (30 días).
Cada 'mundo' muestrea parámetros inciertos (lognormales con cola) de cada canal, basados en datos públicos:
- GameAnalytics 2025: D1 mediana ~22 %, top10 % ~40 %; D7 ~4 % / 12 %; D30 ~0,7 % / 4 %.
- VibeTopList (230 juegos web, oct-2025): la mitad tuvo <=11 visitas la 1.ª semana; el 10 % se llevó el 84 %.
- Apple Ads España 2025: CPA ~2,7 $ (todas las categorías), juegos ~4,6-6 $ (EE. UU.).
- Experiencia del propio usuario: otra app con ~1 descarga/día orgánica.
Salida: descargas iOS, jugadores web, activos día 30, ingresos, probabilidad de >=500 descargas."""
import numpy as np, json, sys
rng=np.random.default_rng(7)
N=20000
def ln(med,spread,size=N):  # lognormal por mediana y dispersión (sigma)
    return med*np.exp(rng.normal(0,spread,size))
def bern(p,size=N): return rng.random(size)<p

def world(strat):
    S=strat
    rng.bit_generator.state=np.random.default_rng(11).bit_generator.state  # mismos mundos para todas las estrategias
    dl=np.zeros(N); web=np.zeros(N)
    Q=ln(1,0.55)  # 'gancho' del juego en ese mundo: afecta a todos los canales a la vez (correlación)
    # 1) búsqueda orgánica App Store (ASO en 6 idiomas mejora ~x1.8 frente a no hacerlo)
    org=ln(1.3,0.6)*(1.8 if S["aso"] else 1)*30
    dl+=org
    # 2) nominación a 'destacados' de Apple (gratis): pocas veces sale, pero cuando sale es enorme
    if S["feat"]:
        f=bern(0.04); dl+=f*ln(1500,0.8)
    # 3) Reddit (r/WebGames, r/playmygame, r/IndieGaming, r/iosgaming, r/incremental... ) posts con juego jugable en web
    if S["reddit"]:
        visits=sum(ln(80,1.3) for _ in range(S["reddit"]))
        web+=visits*0.45; dl+=visits*0.025
    # 4) portales web: itch.io + CrazyGames (CrazyGames: solo jugadores, sin enlace a tienda)
    if S["portals"]:
        itch=ln(150,1.0); web+=itch; dl+=itch*0.03
        passed=bern(0.22)  # supera el 'basic launch' (tiempo de juego y retención buenos)
        cg=np.where(passed,ln(25000,0.9),ln(60,1.0)); web+=cg
    # 5) clips cortos diarios (TikTok/Shorts/Reels) con partidas reales
    if S["clips"]:
        n=S["clips"]; views=sum(ln(250,1.4) for _ in range(n))
        viral=bern(1-(1-0.005)**n)*ln(80000,0.9)
        views=views+viral; dl+=views*ln(0.0015,0.5); web+=views*0.0008
    # 6) foros / comunidades (Discord indie, Mediavida, Forocoches juegos, TouchArcade, HN Show, Product Hunt)
    if S["forums"]:
        v=sum(ln(60,1.2) for _ in range(S["forums"])); dl+=v*0.04; web+=v*0.3
    # 7) prensa/creadores: emails a 40 youtubers/periodistas pequeños de juegos móviles (5-10 % responden)
    if S["press"]:
        k=rng.binomial(S["press"],0.06,N); dl+=sum_cov(k)
    # 8) Apple Ads de pago
    if S["ads_eur"]:
        cpi=ln(3.2,0.35); dl+=S["ads_eur"]/cpi
    dl=dl*np.where(org>0,1,1)
    dl=org+(dl-org)*Q; web=web*Q
    # 9) viralidad del propio juego (retos por enlace): cada jugador trae k nuevos
    kf=ln(0.06,0.5)*(1.6 if S["challenge"] else 1)
    dl=dl/(1-np.minimum(kf,0.6))
    web=web/(1-np.minimum(kf,0.6))
    # retención (calidad del juego): D30 entre 2 % y 6 % con ritual diario
    d30=np.clip(ln(0.035,0.4),0.008,0.12)
    active30=(dl+web*0.25)*d30*0.55  # parte de los usuarios llega tarde en el mes
    # ingresos IAP éticos (sin anuncios en iOS): ARPU 30 días 0,02-0,12 €; web: anuncios del portal 0,002-0,006 €/partida
    rev=dl*ln(0.05,0.6)+web*ln(0.003,0.5)
    return dl,web,active30,rev,org
def sum_cov(k):
    out=np.zeros(N)
    for i in range(1,int(k.max())+1): out+=(k>=i)*ln(40,1.0)
    return out

S0=dict(aso=0,feat=0,reddit=0,portals=0,clips=0,forums=0,press=0,ads_eur=0,challenge=0)
STRATS={
 "A · No hacer nada (como tu otra app)":S0,
 "B · Gratis básico (ASO + nominación Apple)":{**S0,"aso":1,"feat":1,"challenge":1},
 "C · Gratis completo (B + web + Reddit + foros + clips)":{**S0,"aso":1,"feat":1,"challenge":1,"reddit":8,"portals":1,"clips":30,"forums":10},
 "D · C + prensa/creadores (40 emails)":{**S0,"aso":1,"feat":1,"challenge":1,"reddit":8,"portals":1,"clips":30,"forums":10,"press":40},
 "E · D + Apple Ads 150 €":{**S0,"aso":1,"feat":1,"challenge":1,"reddit":8,"portals":1,"clips":30,"forums":10,"press":40,"ads_eur":150},
 "F · D + Apple Ads 300 €":{**S0,"aso":1,"feat":1,"challenge":1,"reddit":8,"portals":1,"clips":30,"forums":10,"press":40,"ads_eur":300},
}
res={}
for name,s in STRATS.items():
    dl,web,a30,rev,org=world(s)
    q=lambda x:[float(np.percentile(x,p)) for p in (10,50,90)]
    res[name]=dict(dl=q(dl),web=q(web),players=q(dl+web),a30=q(a30),rev=q(rev),p500=float((dl>=500).mean()),p500pl=float((dl+web>=500).mean()),p250=float((dl>=250).mean()))
for k,v in res.items():
    print(f"{k}\n  descargas p10/p50/p90 {v['dl'][0]:.0f}/{v['dl'][1]:.0f}/{v['dl'][2]:.0f}  web {v['web'][1]:.0f}  activos d30 {v['a30'][1]:.0f}  ingresos {v['rev'][1]:.1f}€  P(>=500 desc) {v['p500']*100:.0f}%  P(>=500 jugadores) {v['p500pl']*100:.0f}%")
json.dump(res,open(sys.argv[1] if len(sys.argv)>1 else "sim500.json","w"),ensure_ascii=False,indent=1)
