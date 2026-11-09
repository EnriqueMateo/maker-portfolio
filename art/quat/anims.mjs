import {NodeIO} from '@gltf-transform/core';
import {prune,dedup,resample} from '@gltf-transform/functions';
const [,,dir,out]=process.argv;
const WANT={General:["Idle_A","Idle_B","Hit_A","Death_A","Throw","Spawn_Ground"],MovementBasic:["Walking_A","Running_A","Jump_Full_Short"],
 CombatRanged:["Ranged_Magic_Shoot","Ranged_Bow_Release","Ranged_Bow_Draw","Ranged_1H_Shoot"],CombatMelee:["Melee_2H_Attack_Chop","Melee_1H_Attack_Stab","Melee_1H_Attack_Chop"],Simulation:["Cheering"]};
const io=new NodeIO();
const base=await io.read(`${dir}/Rig_Medium_General.glb`);const root=base.getRoot(),buf=root.listBuffers()[0];
const byName=new Map(root.listNodes().map(n=>[n.getName(),n]));
for(const a of root.listAnimations())if(!WANT.General.includes(a.getName()))a.dispose();
for(const [f,names] of Object.entries(WANT)){if(f==="General")continue;
  const d=await io.read(`${dir}/Rig_Medium_${f}.glb`);
  for(const a of d.getRoot().listAnimations()){if(!names.includes(a.getName()))continue;
    const na=base.createAnimation(a.getName());const sm=new Map();
    for(const ch of a.listChannels()){const s=ch.getSampler(),tn=byName.get(ch.getTargetNode().getName());if(!tn)continue;
      let ns=sm.get(s);if(!ns){const cp=acc=>base.createAccessor().setType(acc.getType()).setArray(acc.getArray().slice()).setBuffer(buf);
        ns=base.createAnimationSampler().setInput(cp(s.getInput())).setOutput(cp(s.getOutput())).setInterpolation(s.getInterpolation());sm.set(s,ns);na.addSampler(ns);}
      na.addChannel(base.createAnimationChannel().setSampler(ns).setTargetNode(tn).setTargetPath(ch.getTargetPath()));}
  }}
/* fuera el maniquí: solo huesos y animaciones */
for(const n of root.listNodes()){if(n.getMesh()){n.setMesh(null);n.setSkin(null);}}
for(const m of root.listMeshes())m.dispose();for(const s of root.listSkins())s.dispose();
await base.transform(resample(),dedup(),prune({keepLeaves:true}));
await io.write(out,base);
console.log(root.listAnimations().map(a=>a.getName()).join(","));
