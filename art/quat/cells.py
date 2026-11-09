import json,base64,io,sys,struct
from PIL import Image
import numpy as np
def load(f):
  g=json.load(open(f));b=base64.b64decode(g['buffers'][0]['uri'].split(',')[1]);return g,b
def acc(g,b,i):
  a=g['accessors'][i];bv=g['bufferViews'][a['bufferView']];o=bv.get('byteOffset',0)+a.get('byteOffset',0)
  n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt={5126:np.float32,5123:np.uint16,5125:np.uint32,5121:np.uint8}[a['componentType']]
  st=bv.get('byteStride',0);
  arr=np.frombuffer(b,dtype=dt,count=a['count']*n,offset=o) if not st else None
  return arr.reshape(-1,n)
def cells(f):
  g,b=load(f);bv=g['bufferViews'][g['images'][0]['bufferView']];im=np.array(Image.open(io.BytesIO(b[bv.get('byteOffset',0):bv.get('byteOffset',0)+bv['byteLength']])).convert('RGB'))
  H,W=im.shape[:2];C=W//32;cnt={}
  for m in g['meshes']:
    for p in m['primitives']:
      uv=acc(g,b,p['attributes']['TEXCOORD_0']);idx=acc(g,b,p['indices']).ravel() if 'indices' in p else np.arange(len(uv))
      for u,v in uv[idx]:
        x=int(min(W-1,max(0,u*W)));y=int(min(H-1,max(0,v*H)));k=(x//C,y//C);cnt[k]=cnt.get(k,0)+1
  out=[]
  for k,n in sorted(cnt.items(),key=lambda x:-x[1]):
    c=im[k[1]*C+C//2,k[0]*C+C//2];out.append((k,n,'#%02x%02x%02x'%tuple(c)))
  return out,im
if __name__=='__main__':
  for f in sys.argv[1:]:
    o,_=cells(f);print(f,o)
