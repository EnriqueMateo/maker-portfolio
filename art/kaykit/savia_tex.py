# Savia (hada): la pícara de KayKit con vestido rosa y hojas verdes
from PIL import Image
import numpy as np
SRC='art/vendor/kaykit/adv/KayKit_Adventurers_2.0_FREE/Textures/rogue_texture.png'
im=np.array(Image.open(SRC).convert('RGB')).astype(float)
CW,CH=128,256
def tint(cx,cy,hexc,k=1.0):
  t=np.array([int(hexc[i:i+2],16) for i in (1,3,5)],float)
  c=im[cy*CH:(cy+1)*CH,cx*CW:(cx+1)*CW];l=c@[.299,.587,.114];l=l/max(1,l.mean())
  im[cy*CH:(cy+1)*CH,cx*CW:(cx+1)*CW]=np.clip(t[None,None,:]*(1+(l[...,None]-1)*k),0,255)
for c in [(0,1)]:tint(*c,'#b0307e')
for c in [(1,1),(1,2)]:tint(*c,'#f070b8')
tint(1,0,'#5fae3a')            # pelo verde hoja
for c in [(5,0),(6,0),(5,1),(6,1),(3,2),(4,2),(5,2),(7,2)]:tint(*c,'#3a6e2a')
Image.fromarray(im.astype(np.uint8)).save('art/kaykit/savia_texture.png')
