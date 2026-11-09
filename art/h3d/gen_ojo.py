import os,sys,time,torch
os.environ.setdefault('HY3DGEN_MODELS',os.path.expanduser('~/h3d/models'))
sys.path.insert(0,os.path.expanduser('~/h3d/src'))
from PIL import Image
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline,FloaterRemover,DegenerateFaceRemover,FaceReducer
img=Image.open(sys.argv[1]).convert('RGBA')
p=Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('tencent/Hunyuan3D-2mini',subfolder='hunyuan3d-dit-v2-mini',variant='fp16',device='mps',dtype=torch.float16)
t=time.time()
mesh=p(image=img,num_inference_steps=int(sys.argv[3]) if len(sys.argv)>3 else 30,octree_resolution=256,num_chunks=4000,generator=torch.manual_seed(12345),output_type='trimesh')[0]
print('gen',time.time()-t,flush=True)
mesh=FloaterRemover()(mesh);mesh=DegenerateFaceRemover()(mesh);mesh=FaceReducer()(mesh,max_facenum=30000)
mesh.export(sys.argv[2]);print('ok',len(mesh.faces))
