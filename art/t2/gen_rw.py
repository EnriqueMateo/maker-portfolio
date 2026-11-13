# Genera el modelo 3D de cada héroe desde su ilustración con TRELLIS.2 en Runware (clave en ~/.runware_key)
import sys,os,json,uuid,time,base64,urllib.request
KEY=open(os.path.expanduser('~/.runware_key')).read().strip()
def call(tasks):
  rq=urllib.request.Request('https://api.runware.ai/v1',json.dumps(tasks).encode(),{'Authorization':'Bearer '+KEY,'Content-Type':'application/json','User-Agent':'amago-art/1.0'})
  try:return json.load(urllib.request.urlopen(rq,timeout=300))
  except urllib.error.HTTPError as e:return {'errors':[e.read().decode()[:600].replace(KEY,'***')]}
def find(o):
  if isinstance(o,dict):
    for k,v in o.items():
      if isinstance(v,str) and v.startswith('http') and '.glb' in v:return v
      r=find(v)
      if r:return r
  if isinstance(o,list):
    for v in o:
      r=find(v)
      if r:return r
SEED=int(os.environ.get('SEED','12345'));SUF=os.environ.get('SUF','')
for i in sys.argv[1].split(','):
  out=f'art/t2/{i}{SUF}.glb'
  if os.path.exists(out):continue
  t=time.time();u=str(uuid.uuid4())
  img='data:image/png;base64,'+base64.b64encode(open(f'art/h3d/in/{i}.png','rb').read()).decode()
  r=call([{'taskType':'3dInference','taskUUID':u,'model':'microsoft:trellis-2@4b','inputs':{'image':img},'seed':SEED,
    'settings':{'resolution':1024,'textureSize':2048,'remesh':True,'decimationTarget':200000},'deliveryMethod':'sync','includeCost':True}])
  while not find(r) and not r.get('errors') and time.time()-t<600:
    time.sleep(4);r=call([{'taskType':'getResponse','taskUUID':u}])
  url=find(r)
  if not url:print(i,'ERR',json.dumps(r)[:600],flush=True);break
  urllib.request.urlretrieve(url,out)
  print(i,'saved',round(time.time()-t),'s cost',json.dumps(r)[json.dumps(r).find('"cost"'):][:20],os.path.getsize(out),flush=True)
