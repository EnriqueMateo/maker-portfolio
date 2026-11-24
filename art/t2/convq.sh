#!/bin/bash
# Convierte en cola los modelos que va dejando gen1.py: comprueba volumen y convierte de uno en uno.
cd /Users/enriquemateo/Developer/AMAGO
for id in "$@"; do
  for i in $(seq 1 240); do [ -f art/t2/$id.glb ] && break; [ -f art/t2/.gen_done ] && break; perl -e 'select(undef,undef,undef,15)'; done
  [ -f art/t2/$id.glb ] || { echo "$id no generado"; continue; }
  r=$(~/h3d/venv/bin/python -c "
import trimesh,numpy as np
s=trimesh.load('art/t2/$id.glb');m=s.to_geometry()
p=np.ptp(m.vertices,axis=0);print('flat' if (p/p.max()).min()<.1 else 'ok',(p/p.max()).round(2))")
  echo "$(date +%H:%M) $id volumen $r"
  case "$r" in flat*) mkdir -p art/t2/bad/flat2; mv art/t2/$id.glb art/t2/bad/flat2/; continue;; esac
  [ $id = truco ] && mkdir -p art/t2/bak && cp amago/h3d/truco.glb amago/h3d/truco.webp art/t2/bak/ 2>/dev/null
  ~/h3d/venv/bin/python art/t2/conv3.py $id amago/h3d 2>&1 | tail -1
done
echo "conversiones terminadas"
