# Recolorea la fila de paleta de cada monstruo (Quaternius, CC0) con los colores del héroe de AMAGO
import sys,json;sys.path.insert(0,__file__.rsplit('/',1)[0])
from cells import *
SEL=__file__.rsplit('/',3)[0]+'/art/vendor/quat/sel/'
OUT=__file__.rsplit('/',1)[0]+'/'
H={
 'brasa':('Dino',{(2,6):'#e8622a',(3,6):'#f6d08e',(5,6):'#8a2a10'}),
 'ojo':('Birb',{(2,1):'#8a5428',(3,1):'#ecca9c',(4,1):'#f09a22'}),
 'bum':('PinkBlob',{(2,20):'#262a52',(3,20):'#3c4280'}),
 'mina':('Monkroose',{(3,9):'#e8b48e',(2,9):'#7a4a22',(4,9):'#4a3018'}),
 'salto':('Frog',{(2,8):'#36b84c',(3,8):'#12521f'}),
 'mira':('Cat',{(2,16):'#e0aa30',(3,16):'#8a5a14'}),
 'eco':('Goleling',{(2,27):'#5c40c8',(3,27):'#2a1a5a'}),
 'muro':('Yeti',{(2,14):'#8592ae',(3,14):'#56637f',(4,14):'#a6b2c8'}),
}
for hid,(f,m) in H.items():
  if len(sys.argv)>1 and hid not in sys.argv[1:]:continue
  o,im=cells(SEL+f+'.gltf');im=im.copy();C=im.shape[1]//32
  for (cx,cy),col in m.items():
    im[cy*C:(cy+1)*C,cx*C:(cx+1)*C]=[int(col[i:i+2],16) for i in (1,3,5)]
  Image.fromarray(im).resize((128,128),Image.NEAREST).save(OUT+hid+'_tex.png')
  print(hid,f)
