# Pinta el modelo con la ilustración proyectada de frente; la espalda toma los colores del contorno, difuminados
import sys,numpy as np,trimesh,cv2
from PIL import Image
src,img_path,out=sys.argv[1],sys.argv[2],sys.argv[3]
FLIP=len(sys.argv)>4 and sys.argv[4]=='flip'
m=trimesh.load(src,force='mesh')
im=np.array(Image.open(img_path).convert('RGBA')).astype(np.float32)
a=im[...,3]>20
# quita el contorno oscuro del dibujo: se queda con el interior y rellena hacia fuera
inner=cv2.erode(a.astype(np.uint8),np.ones((3,3),np.uint8),iterations=7).astype(bool)
rgb=im[...,:3].copy();rgb[~inner]=0
fill=cv2.inpaint(rgb.astype(np.uint8),(~inner).astype(np.uint8)*255,9,cv2.INPAINT_TELEA)
front=fill
# espalda: los colores del dibujo muy difuminados (sin cara)
back=cv2.GaussianBlur(fill,(0,0),28)
bh=cv2.cvtColor(back,cv2.COLOR_RGB2HSV).astype(np.float32);bh[...,1]=np.clip(bh[...,1]*1.6,0,255);bh[...,2]=np.clip(bh[...,2]*.92,0,255)
back=cv2.cvtColor(bh.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)
back=(back*.55+np.array([168,92,44],np.float32)*.45).clip(0,255).astype(np.uint8)
ys,xs=np.where(a);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
V=m.vertices.copy()
if FLIP:V[:,0]*=-1;V[:,2]*=-1
b0,b1=V.min(0),V.max(0)
u=(V[:,0]-b0[0])/(b1[0]-b0[0]);v=(V[:,1]-b0[1])/(b1[1]-b0[1])
H,W=a.shape
px=x0+u*(x1-x0);py=y1-v*(y1-y0)
fn=m.face_normals.copy()
if FLIP:fn[:,0]*=-1;fn[:,2]*=-1
def samp(img,x,y):
  return img[np.clip(y.astype(int),0,H-1),np.clip(x.astype(int),0,W-1)].astype(np.float32)
# textura: mitad izquierda = dibujo de frente, mitad derecha = espalda difuminada
F=m.faces;isf=fn[:,2]>-.08
atlas=np.concatenate([front,back],1)
uv=np.stack([px/(2*W),1-py/H],1)
nv=V[F].reshape(-1,3);uvc=uv[F].reshape(-1,3,2).copy()
uvc[~isf,:,0]+=.5
if FLIP:nv[:,0]*=-1;nv[:,2]*=-1
mesh=trimesh.Trimesh(vertices=nv,faces=np.arange(len(nv)).reshape(-1,3),process=False)
mat=trimesh.visual.material.PBRMaterial(baseColorTexture=Image.fromarray(atlas),metallicFactor=0,roughnessFactor=1)
mesh.visual=trimesh.visual.TextureVisuals(uv=uvc.reshape(-1,2),material=mat)
mesh.export(out);print('painted',len(F),isf.mean())
