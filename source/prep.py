import json, sys
S=sys.argv[1]
TL={
 "en":{"vo":"vo_a","chunks":[[0,12.1,0.8],[12.1,20.75,13.4],[20.75,28.9,22.35],[28.9,41.1,30.5],[41.1,54.5,42.9],[54.5,60.15,57.1],[60.15,67.1,63.55],[67.1,70.53,75.5]],
   "shots":[["city",0],["window",13.2],["asia",22.2],["trade",30.3],["europe",42.8],["toll",56.6],["after",63.4],["final",74.0]],
   "ev":{"asiaMap":26.6,"tradeMap":34.2,"infect":37.2,"plague":41.4,"europeCity":46.9,"europeDoc":53.4,"title":79.6,"black":85.0},
   "fix":{"Issy-Kul":"Issyk-Kul","14th century":"14th century"}},
 "ru":{"vo":"vo_b","chunks":[[0,11.05,0.8],[11.05,19.5,12.65],[19.5,31.75,21.6],[31.75,41.85,34.05],[41.85,55.4,44.25],[55.4,60.95,57.8],[60.95,66.45,64.15],[66.45,70.69,75.65]],
   "shots":[["city",0],["window",12.4],["asia",21.4],["trade",33.8],["europe",44.0],["toll",57.8],["after",63.9],["final",74.0]],
   "ev":{"asiaMap":28.9,"tradeMap":36.6,"infect":39.4,"plague":43.3,"europeCity":48.6,"europeDoc":54.9,"title":79.6,"black":85.0},
   "fix":{"Иссекуль":"Иссык-Куль","внесла":"унесла","презнем":"прежним","центральной Азии":"Центральной Азии","14 веке":"XIV веке","«чёрной смертью»":"«Чёрной смертью»","чёрная смерть":"Чёрная смерть"}},
}
def fmt(t):
    ms=int(round(t*1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
for lang,cfg in TL.items():
    d=json.load(open(f"{S}/{cfg['vo']}.json"))
    subs=[]
    for s in d["segs"]:
        ch=next(c for c in cfg["chunks"] if c[0]-0.05<=s["start"]<c[1])
        off=ch[2]-ch[0]
        words=[(w["s"],w["e"],w["w"]) for w in s["words"]]
        # split long segments at punctuation nearest the middle
        txt=s["text"]
        pieces=[words]
        if len(txt)>58:
            n=len(words); best=None
            for i in range(1,n):
                left=''.join(w[2] for w in words[:i]).strip()
                score=abs(len(left)-len(txt)/2) - (25 if left.endswith((',', '.', '—')) else 0)
                if best is None or score<best[0]: best=(score,i)
            pieces=[words[:best[1]],words[best[1]:]]
        for p in pieces:
            t=''.join(w[2] for w in p).strip()
            for a,b in cfg["fix"].items(): t=t.replace(a,b)
            subs.append([round(p[0][0]+off,2),round(p[-1][1]+off+0.25,2),t])
    PF={"the Black Death had killed tens of":("the Black Death had killed",None),"millions of people across Eurasia.":("tens of millions of people across Eurasia.",None),
        "Вместе с торговлей распространялась и опасная инфекция —":("Вместе с торговлей распространялась",-2.0),"чума.":("и опасная инфекция — чума.",-2.0)}
    for sb in subs:
        if sb[2] in PF:
            nt,sh=PF[sb[2]]
            if sh is not None and nt.startswith("Вместе"): sb[1]+=sh
            if sh is not None and nt.startswith("и опасная"): sb[0]+=sh
            sb[2]=nt
    for i in range(len(subs)-1):
        subs[i][1]=min(subs[i][1],subs[i+1][0]-0.05)
    cfg["subs"]=subs
    with open(f"{S}/subs_{lang}.srt","w") as f:
        for i,(a,b,t) in enumerate(subs,1): f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{t}\n\n")
    for s in subs: print(lang,s)
json.dump(TL,open(f"{S}/timeline.json","w"),ensure_ascii=False,indent=1)
