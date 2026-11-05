import sys
from PIL import Image, ImageDraw
fs=sys.argv[2:]; n=len(fs); cols=min(n,6)
ims=[Image.open(f).resize((216,384)) for f in fs]
rows=(n+cols-1)//cols
sh=Image.new("RGB",(216*cols,384*rows)); d=ImageDraw.Draw(sh)
for i,(f,im) in enumerate(zip(fs,ims)):
    x,y=(i%cols)*216,(i//cols)*384; sh.paste(im,(x,y)); d.text((x+4,y+4),f.split('_')[-1][:-4],fill=(0,255,0))
sh.save(sys.argv[1])
