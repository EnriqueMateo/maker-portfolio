# Convierte un modelo TRELLIS.2 (art/t2/id.glb) al formato del juego: malla ligera en coordenadas de carta + textura rehecha (webp)
import sys,os,numpy as np,trimesh,pymeshlab,xatlas,cv2
from scipy.spatial import cKDTree
from PIL import Image
i=sys.argv[1];D=os.path.dirname(os.path.abspath(__file__));NF=int(os.environ.get('NF','14000'));R=int(os.environ.get('TEX','1024'));G=sys.argv[2]
src=trimesh.load(f'{D}/{i}.glb',force='mesh',process=False);tex=np.asarray(src.visual.material.baseColorTexture.convert('RGB'),np.float32);TH,TW=tex.shape[:2]
# nube de puntos de color del original
pts,fi=trimesh.sample.sample_surface(src,int(os.environ.get('NS','5000000')))
tri=src.vertices[src.faces[fi]];v0,v1,v2=tri[:,0],tri[:,1],tri[:,2]
def bary(p,a,b,c):
    e0,e1,e2=b-a,c-a,p-a;d00=(e0*e0).sum(1);d01=(e0*e1).sum(1);d11=(e1*e1).sum(1);d20=(e2*e0).sum(1);d21=(e2*e1).sum(1);dn=np.maximum(d00*d11-d01*d01,1e-20)
    v=(d11*d20-d01*d21)/dn;w=(d00*d21-d01*d20)/dn;return np.stack([1-v-w,v,w],1)
bc=bary(pts,v0,v1,v2);uvs=(np.asarray(src.visual.uv)[src.faces[fi]]*bc[:,:,None]).sum(1)
cx=np.clip(uvs[:,0]*TW,0,TW-1).astype(int);cy=np.clip((1-uvs[:,1])*TH,0,TH-1).astype(int);pc=tex[cy,cx]
tree=cKDTree(pts)
# malla ligera
g0=trimesh.Trimesh(src.vertices,src.faces,process=True);g0.merge_vertices()
ms=pymeshlab.MeshSet();ms.add_mesh(pymeshlab.Mesh(g0.vertices,g0.faces))
SM=int(os.environ.get('SM','6'))
if SM:ms.apply_coord_taubin_smoothing(stepsmoothnum=SM,lambda_=.5,mu=-.53)
ms.meshing_decimation_quadric_edge_collapse(targetfacenum=NF,preservenormal=True,preservetopology=True,qualitythr=.5)
ms.apply_coord_taubin_smoothing(stepsmoothnum=2,lambda_=.5,mu=-.53)
q=ms.current_mesh();m=trimesh.Trimesh(q.vertex_matrix(),q.face_matrix(),process=False)
# normales de una copia muy suavizada (misma topología): la luz cae en bandas limpias y la silueta conserva el detalle
ms.apply_coord_laplacian_smoothing(stepsmoothnum=int(os.environ.get('NSM','6')),cotangentweight=False)
qs=ms.current_mesh();msm=trimesh.Trimesh(qs.vertex_matrix(),qs.face_matrix(),process=False)
V=m.vertices
at=xatlas.Atlas();at.add_mesh(V,m.faces);co=xatlas.ChartOptions();co.max_cost=float(os.environ.get('MC','10'));co.normal_deviation_weight=1.0;co.max_iterations=2
po=xatlas.PackOptions();po.padding=6;po.resolution=R;po.bilinear=True;at.generate(co,po);vm,F2,uv=at[0];print('charts',at.chart_count,flush=True)
P=V[vm];Nn=np.asarray(msm.vertex_normals)[vm]
tp=np.zeros((R,R,3),np.float32);cov=np.zeros((R,R),bool);U=uv*R
for f in F2:
    t=U[f];mn=np.clip(np.floor(t.min(0)).astype(int)-1,0,R-1);mx=np.clip(np.ceil(t.max(0)).astype(int)+1,0,R-1)
    gx,gy=np.meshgrid(np.arange(mn[0],mx[0]+1)+.5,np.arange(mn[1],mx[1]+1)+.5)
    d=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
    if abs(d)<1e-12:continue
    w0=((t[1,1]-t[2,1])*(gx-t[2,0])+(t[2,0]-t[1,0])*(gy-t[2,1]))/d;w1=((t[2,1]-t[0,1])*(gx-t[2,0])+(t[0,0]-t[2,0])*(gy-t[2,1]))/d;w2=1-w0-w1
    ok=(w0>=-.02)&(w1>=-.02)&(w2>=-.02)
    if not ok.any():continue
    iy=(gy[ok]-.5).astype(int);ix=(gx[ok]-.5).astype(int);tp[iy,ix]=np.stack([w0[ok],w1[ok],w2[ok]],1)@P[f];cov[iy,ix]=True
iy,ix=np.where(cov);_,nn=tree.query(tp[iy,ix],k=4,workers=-1)
out=np.zeros((R,R,3),np.uint8);out[iy,ix]=pc[nn].mean(1).clip(0,255)
out=cv2.inpaint(out,(~cov).astype(np.uint8)*255,3,cv2.INPAINT_TELEA)
# limpieza: colores planos sin ruido (filtro que respeta bordes), bordes nítidos y oscuros más profundos (ojos, líneas)
o=cv2.bilateralFilter(out,9,28,7).astype(np.float32);bl=cv2.GaussianBlur(o,(0,0),R/400)
o=np.clip(o+(o-bl)*float(os.environ.get('SH','.9')),0,255)/255
l=o.mean(2,keepdims=True);o=np.clip(o*(.86+.14*np.clip(l*2.2,0,1)),0,1)
out=(o*255).astype(np.uint8)
# color: se lleva la textura a los colores de la ilustración original (media y contraste en Lab)
if os.environ.get('CT','1')=='1':
    spi=np.asarray(Image.open(f'{D}/../../amago/sprites/{i}.webp').convert('RGBA'));mk=spi[...,3]>250;mk=cv2.erode(mk.astype(np.uint8),np.ones((9,9),np.uint8))>0
    ref=cv2.cvtColor(spi[...,:3][mk][None],cv2.COLOR_RGB2LAB).astype(np.float32)[0];lab=cv2.cvtColor(out,cv2.COLOR_RGB2LAB).astype(np.float32);cur=lab[cov]
    K=float(os.environ.get('CTK','.8'))
    chroma=np.hypot(lab[...,1]-128,lab[...,2]-128);wch=np.clip((chroma-18)/30,0,1)
    for ch in range(3):
        sc_=np.clip(ref[:,ch].std()/max(cur[:,ch].std(),1e-3),.8,1.35);t=(lab[...,ch]-cur[:,ch].mean())*sc_+ref[:,ch].mean();kk=K*(wch if ch else .6+.4*wch);lab[...,ch]=lab[...,ch]*(1-kk)+t*kk
    out=cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8),cv2.COLOR_LAB2RGB)
out=out[::-1]
b0,b1=P.min(0),P.max(0)
sp=Image.open(f'{D}/../../amago/sprites/{i}.webp').convert('RGBA');bx=sp.getbbox();Ws,Hs=sp.size
# el modelo ocupa la misma caja que la ilustración en la carta (alto de la imagen = 1)
sx=(bx[2]-bx[0])/(b1[0]-b0[0]);sy=(bx[3]-bx[1])/(b1[1]-b0[1])
px=bx[0]+(P[:,0]-b0[0])*sx;py=bx[3]-(P[:,1]-b0[1])*sy
C=np.stack([(px/Ws-.5)*Ws/Hs,1-py/Hs,(P[:,2]-np.median(P[:,2]))*(sx+sy)/2/Hs],1)
T=Image.fromarray(out)
g=trimesh.Trimesh(vertices=C,faces=F2,vertex_normals=Nn,process=False);g.visual=trimesh.visual.TextureVisuals(uv=uv)
os.makedirs(G,exist_ok=True);g.export(f'{G}/{i}.glb');T.save(f'{G}/{i}.webp',quality=90,method=6)
o=trimesh.Trimesh(vertices=C,faces=F2,vertex_normals=Nn,process=False);o.visual=trimesh.visual.TextureVisuals(uv=uv,material=trimesh.visual.material.PBRMaterial(baseColorTexture=T,metallicFactor=0,roughnessFactor=1))
os.makedirs(f'{D}/../h3d/out',exist_ok=True);o.export(f'{D}/../h3d/out/t2_{i}.glb')
print('ok',i,len(F2),len(C),'ratio xy',round(sx/sy,3),C.min(0).round(2),C.max(0).round(2))
