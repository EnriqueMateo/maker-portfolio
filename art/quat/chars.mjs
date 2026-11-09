import {NodeIO} from '@gltf-transform/core';
import {prune,dedup} from '@gltf-transform/functions';
import fs from 'fs';
const A=process.env.HOME+"/Developer/AMAGO/",K=A+"art/vendor/kaykit/adv/KayKit_Adventurers_2.0_FREE/",OUT=A+"amago/kk/";
const HEROES={
  rayo:{c:"Mage",tex:A+"art/kaykit/rayo_texture.png",item:"wand"},
  flecha:{c:"Rogue_Hooded",tex:null,item:"bow_withString"},
  sombra:{c:"Rogue_Hooded",tex:A+"art/kaykit/sombra_texture.png",item:"dagger"},
  savia:{c:"Rogue",tex:A+"art/kaykit/savia_texture.png",item:"wand"},
};
const io=new NodeIO();const only=process.argv.slice(2);
for(const [id,h] of Object.entries(HEROES)){if(only.length&&!only.includes(id))continue;
  const d=await io.read(`${K}Characters/gltf/${h.c}.glb`);
  if(h.tex)for(const t of d.getRoot().listTextures())t.setImage(fs.readFileSync(h.tex));
  await d.transform(dedup(),prune());await io.write(`${OUT}${id}.glb`,d);
  if(h.item){const it=await io.read(`${K}Assets/gltf/${h.item}.gltf`);
    if(h.tex)for(const t of it.getRoot().listTextures())t.setImage(fs.readFileSync(h.tex));
    for(const b of it.getRoot().listBuffers().slice(1))b.dispose();
    await io.write(`${OUT}${id}_item.glb`,it);}
  console.log(id,fs.statSync(`${OUT}${id}.glb`).size);
}
