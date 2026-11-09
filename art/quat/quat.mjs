import {NodeIO} from '@gltf-transform/core';
import {prune,dedup,resample} from '@gltf-transform/functions';
import fs from 'fs';
const A=process.env.HOME+"/Developer/AMAGO/",S=A+"art/vendor/quat/sel/",OUT=A+"amago/kk/",TX=A+"art/quat/";
const H={brasa:"Dino",ojo:"Birb",bum:"PinkBlob",mina:"Monkroose",salto:"Frog",mira:"Cat",eco:"Goleling",muro:"Yeti",truco:"Fox"};
const only=process.argv.slice(2);
const io=new NodeIO();
for(const [id,f] of Object.entries(H)){
  if(only.length&&!only.includes(id))continue;
  const d=await io.read(S+f+".gltf");
  const tx=TX+id+"_tex.png";
  if(fs.existsSync(tx))for(const t of d.getRoot().listTextures()){t.setImage(fs.readFileSync(tx));t.setMimeType("image/png");}
  if(id==="truco"){const C={Main:[1,.32,.03,1],Main_Light:[.95,.92,.86,1],Black:[.03,.025,.03,1],Grey:[.25,.2,.2,1]};
    for(const m of d.getRoot().listMaterials()){if(C[m.getName()])m.setBaseColorFactor(C[m.getName()]);}}
  for(const m of d.getRoot().listMaterials()){m.setMetallicFactor(0);m.setRoughnessFactor(1);}
  await d.transform(resample(),dedup(),prune());
  await io.write(OUT+id+".glb",d);
  console.log(id,f,fs.statSync(OUT+id+".glb").size);
}
