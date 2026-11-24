#!/bin/bash
# Revisa candidatos: art/t2/cand/<id>_<seed>.glb -> captura 4 ángulos (0, 90, 180, 270) sin giro previo
cd /Users/enriquemateo/Developer/AMAGO
OUT=/private/tmp/claude-501/-Users-enriquemateo-Developer-AMAGO/2ed0ba6e-ee01-4b9e-b6d2-b30ac0bc2a5a/scratchpad/cand
mkdir -p $OUT
id=$1; shift
for seed in "$@"; do
  f=art/t2/cand/${id}_$seed.glb; [ -f $f ] || continue
  cp $f art/t2/$id.glb; ROT=0 ~/h3d/venv/bin/python art/t2/conv3.py $id amago/h3d >/dev/null 2>&1
  (cd ~/Developer/amago-shorts/scripts && perl -e 'alarm 200; exec @ARGV' node orient2.mjs $OUT/${id}_$seed $id >/dev/null 2>&1)
done
rm -f art/t2/$id.glb
~/h3d/venv/bin/python - "$OUT" "$id" "$@" <<'PY'
import sys
from PIL import Image
out,id_,seeds=sys.argv[1],sys.argv[2],sys.argv[3:]
rows=[]
for s in seeds:
  try: ims=[Image.open(f'{out}/{id_}_{s}_{id_}_{k}.png') for k in range(4)]
  except FileNotFoundError: continue
  w,h=ims[0].size;O=Image.new('RGB',(w*4,h));[O.paste(im,(k*w,0)) for k,im in enumerate(ims)];rows.append(O)
O=Image.new('RGB',(rows[0].width,rows[0].height*len(rows)));[O.paste(r,(0,k*r.height)) for k,r in enumerate(rows)];O.thumbnail((1800,1800));O.save(f'{out}/{id_}_rev.jpg',quality=85)
PY
