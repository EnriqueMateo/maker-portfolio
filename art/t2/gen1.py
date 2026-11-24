# TRELLIS v1 (trellis-community/TRELLIS, MIT) fallback: TRELLIS.2 Space returns flat meshes since ~2026-11-18
import shutil,time,sys,os
from gradio_client import Client,handle_file
TOK=open(os.path.expanduser('~/.hf_token')).read().strip()
for i in sys.argv[1].split(','):
  out='art/t2/'+i+'.glb'
  if os.path.exists(out):continue
  t=time.time()
  try:
    c=Client('trellis-community/TRELLIS',token=TOK,verbose=False)
    c.predict(api_name='/start_session')
    im=c.predict(handle_file('art/h3d/in/'+i+'.png'),api_name='/preprocess_image')
    p=im if isinstance(im,str) else im['path']
    r=c.predict(handle_file(p),[],int(os.environ.get('SEED','12345')),7.5,int(os.environ.get('STEPS','12')),3.0,int(os.environ.get('STEPS','12')),'stochastic',0.9,2048,api_name='/generate_and_extract_glb')
    f=[x for x in r if isinstance(x,str) and x.endswith('.glb')]
    f=f[-1] if f else r[-1]
    shutil.copy(f,out);print(i,'saved',round(time.time()-t),flush=True)
  except Exception as e:
    print(i,'ERR',str(e)[:300].replace(TOK,'***'),flush=True);break
