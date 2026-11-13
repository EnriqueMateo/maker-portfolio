// Simula rondas jugador-guion contra el bot para medir cuánto aporta cada ULTI
const fs=require("fs");const html=fs.readFileSync(process.argv[2],"utf8");
const m=html.match(/\/\* ENGINE-START \*\/([\s\S]*?)\/\* ENGINE-END \*\//);
globalThis.window={AMAGO_DEV_HEROES:true};
const E=new Function("window",m[1]+"\nreturn AMAGO;")(globalThis.window);
const ids=Object.keys(E.HEROES),N=+process.argv[3]||300,BOT={react:.35,perc:.35,eps:.18,passive:3,think:.2,dodge:.75};
function round(tp,tb,pu,bu){
  const R=E.newRound(tp,tb,{bot:BOT});R.paused=false;let w;const hk={roundOver:x=>{w=x;}};
  const me=R.heroes.p,H=E.HEROES[tp];if(!pu)me.ultiUsed=true;if(!bu)R.heroes.b.ultiUsed=true;
  let next=0,uAt=15+Math.random()*20,bel=null;
  while(!R.over){E.tick(R,.05,hk);if(R.over)break;if(R.now<next)continue;next=R.now+.25+Math.random()*.2;
    const dang=R.projs.filter(p=>p.d==="p"&&p.warn&&R.now-p.launched>.3),inD=(x,y)=>dang.some(p=>E.inArea(p.cells,x,y))||(R.fires||[]).some(f=>f.d==="p"&&!f.hit&&E.inArea(f.cells,x,y));
    const thr=inD(me.x,me.y);
    if(!me.ultiUsed&&R.now>=uAt){const def=["muro","salto","truco"].includes(tp);if(!def||thr){E.ulti(R,"p",hk);if(def)continue;}}
    if(thr&&!me.path.length&&Math.random()<.75){const o=E.allCells().filter(([x,y])=>!inD(x,y)).sort((a,b)=>Math.abs(a[0]-me.x)+Math.abs(a[1]-me.y)-Math.abs(b[0]-me.x)-Math.abs(b[1]-me.y))[0];if(o)E.moveTo(R,"p",o[0],o[1]);continue;}
    // dispara a la última pista del rival; si no hay, al azar con menos frecuencia
    const ms=R.marks.b.filter(q=>!q.dud),clue=ms.find(q=>q.t==="hit"||q.t==="ping"||q.t==="pick")||ms.find(q=>q.t==="huella"&&!q.fake);
    const vis=me.visionUntil>R.now;
    if(R.elx.p>=H.cost&&R.now>=me.cdUntil){
      if(vis){E.fire(R,"p",R.heroes.b.x,R.heroes.b.y,hk);if(Math.random()<.6){const c=E.pick(E.allCells());E.moveTo(R,"p",c[0],c[1]);}}
      else if(clue){E.fire(R,"p",clue.x,clue.y,hk);if(Math.random()<.6){const c=E.pick(E.allCells());E.moveTo(R,"p",c[0],c[1]);}}
      else if(R.elx.p>=H.cost+3&&Math.random()<.3){E.fire(R,"p",E.rnd(5),E.rnd(5),hk);if(Math.random()<.6){const c=E.pick(E.allCells());E.moveTo(R,"p",c[0],c[1]);}}
    }
  }
  return w;
}
const res={};
for(const a of ids){let r=[0,0,0];
  for(const b of ids){if(a===b)continue;for(let i=0;i<N;i++){if(round(a,b,false,false)==="p")r[0]++;if(round(a,b,true,false)==="p")r[1]++;if(round(b,a,false,true)==="b")r[2]++;}}
  const T=N*(ids.length-1);let base=0;for(const b of ids){if(a===b)continue;for(let i=0;i<N;i++)if(round(b,a,false,false)==="b")base++;}
  console.log(a.padEnd(7),"jugador sin ULTI",(r[0]/T*100).toFixed(1).padStart(5),"% con",(r[1]/T*100).toFixed(1).padStart(5),"%  | bot sin",(base/T*100).toFixed(1).padStart(5),"% con",(r[2]/T*100).toFixed(1).padStart(5),"%");}
