import sys
from PIL import Image, ImageDraw
fs=sys.argv[2:]; cols=2
ims=[Image.open(f).resize((640,360)) for f in fs]
rows=(len(ims)+cols-1)//cols
sh=Image.new("RGB",(640*cols,360*rows))
d=ImageDraw.Draw(sh)
for i,(f,im) in enumerate(zip(fs,ims)):
    sh.paste(im,((i%cols)*640,(i//cols)*360)); d.text(((i%cols)*640+8,(i//cols)*360+8),f.split('_')[-1],fill=(0,255,0))
sh.save(sys.argv[1])
