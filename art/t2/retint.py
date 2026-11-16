# Aclara una gama de color de la textura de un héroe (p. ej. el verde oscuro de Salto -> verde lima), sin tocar el resto.
# uso: retint.py <textura.webp> <h_min> <h_max> <h_destino> <v_mult> [s_min] [v_max: solo píxeles más oscuros que esto]   (tonos en grados 0-360)
import sys,numpy as np,cv2
from PIL import Image
f=sys.argv[1];h0,h1,ht,vm=[float(x) for x in sys.argv[2:6]];smin=float(sys.argv[6]) if len(sys.argv)>6 else .7;vmax=float(sys.argv[7]) if len(sys.argv)>7 else 1.01
im=np.asarray(Image.open(f).convert('RGB'));hsv=cv2.cvtColor(im,cv2.COLOR_RGB2HSV_FULL).astype(np.float32)
H=hsv[...,0]*360/255;S=hsv[...,1]/255;V=hsv[...,2]/255
m=((H>=h0)&(H<=h1)&(S>.25)&(V>.08)&(V<vmax)).astype(np.float32)
m=cv2.GaussianBlur(m,(0,0),2.5)
H2=H*(1-.75*m)+ht*.75*m;V2=np.clip(V*(1+(vm-1)*m),0,1);S2=np.where(m>.5,np.maximum(S,smin),S)
out=np.stack([H2*255/360,S2*255,V2*255],-1).clip(0,255).astype(np.uint8)
Image.fromarray(cv2.cvtColor(out,cv2.COLOR_HSV2RGB_FULL)).save(f,quality=90,method=6)
print('retocado',round(float(m.mean()),2))
