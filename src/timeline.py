# Builds per-language voice tracks + cue json (sentence/word timings, scene starts)
import json, re, sys, difflib, numpy as np, soundfile as sf, subprocess
SR=48000
SCENE_FIRST=[0,3,6,13,16,19]           # 0-based first sentence of scenes 1..6
EXTRA={3:1.8,6:1.0,13:1.0,16:1.0,19:1.3}  # extra pause inserted before sentence idx
LEAD=1.3
def norm(t): return re.sub(r'[^\wё]','',t.lower().replace('ё','е'))
def toks(line): return line.split()
def load(path):
    a,_=sf.read(path,dtype='float32') if path.endswith('.wav') else (None,None)
    return a
def decode(path):
    r=subprocess.run(['ffmpeg','-loglevel','error','-i',path,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True)
    return np.frombuffer(r.stdout,np.float32).copy()
def align(canon_lines, wwords):
    """canon_lines: list of str; wwords: list of {w,s,e}. returns per line list of (token,s,e)"""
    ct=[(li,t) for li,l in enumerate(canon_lines) for t in toks(l)]
    a=[norm(t) for _,t in ct]; b=[norm(w['w']) for w in wwords]
    sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
    S=[None]*len(ct); E=[None]*len(ct)
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for k in range(i2-i1): S[i1+k]=wwords[j1+k]['s']; E[i1+k]=wwords[j1+k]['e']
        elif tag=='replace' and j2>j1:
            s0=wwords[j1]['s']; e0=wwords[j2-1]['e']; n=i2-i1
            for k in range(n): S[i1+k]=s0+(e0-s0)*k/n; E[i1+k]=s0+(e0-s0)*(k+1)/n
    # interpolate missing
    for k in range(len(ct)):
        if S[k] is None:
            p=next((E[j] for j in range(k-1,-1,-1) if E[j] is not None),0.0)
            q=next((S[j] for j in range(k+1,len(ct)) if S[j] is not None),p+0.3)
            S[k]=p; E[k]=min(q,p+0.3)
    out=[[] for _ in canon_lines]
    for k,(li,t) in enumerate(ct): out[li].append([t,S[k],E[k]])
    return out
def whisper_words(wav):
    from faster_whisper import WhisperModel
    m=WhisperModel("medium",device="cpu",compute_type="int8")
    a,_=sf.read(wav,dtype='float32')
    import scipy.signal as ss
    a16=ss.resample_poly(a,1,3).astype(np.float32)
    segs,info=m.transcribe(a16,word_timestamps=True,beam_size=5,language=LANG)
    return [{'w':w.word,'s':w.start,'e':w.end} for s in segs for w in s.words]
def trim(a,th=0.01):
    idx=np.where(np.abs(a)>th)[0]
    return a[max(0,idx[0]-int(0.03*SR)):idx[-1]+int(0.08*SR)]
LANG=sys.argv[1]
if LANG=='ru':
    lines=open('ru_lines.txt').read().strip().split('\n')
    segs=json.load(open('vo.json')); W=[w for s in segs for w in s['words']]
    al=align(lines,W)
    src=decode('vo.mp3')
    # cut points between sentences at min energy
    cuts=[0]
    for i in range(1,len(lines)):
        pe=al[i-1][-1][2]; ns=al[i][0][1]
        a0,a1=int(pe*SR),int(ns*SR)
        if a1-a0<int(0.02*SR): c=(a0+a1)//2
        else:
            env=np.convolve(np.abs(src[a0:a1]),np.ones(240)/240,'same'); c=a0+int(np.argmin(env))
        cuts.append(c)
    cuts.append(len(src))
    out=np.zeros(int(130*SR),np.float32); off=LEAD; sent=[]
    for i in range(len(lines)):
        off+=EXTRA.get(i,0)
        clip=src[cuts[i]:cuts[i+1]]; st=int((cuts[i]/SR+off)*SR)
        # tiny fades to avoid clicks
        f=min(240,len(clip)//2); clip=clip.copy(); clip[:f]*=np.linspace(0,1,f); clip[-f:]*=np.linspace(1,0,f)
        out[st:st+len(clip)]+=clip
        sh=off
        sent.append({'text':lines[i],'start':al[i][0][1]+sh,'end':al[i][-1][2]+sh,
                     'words':[[t,s+sh,e+sh] for t,s,e in al[i]]})
    end=sent[-1]['end']
else:
    lines=open('en_lines.txt').read().strip().split('\n')
    ru=json.load(open('cues_ru.json'))['sentences']
    from kokoro_onnx import Kokoro
    k=Kokoro("kok/kokoro-v1.0.onnx","kok/voices-v1.0.bin")
    import scipy.signal as ss
    out=np.zeros(int(140*SR),np.float32); prev=0; sent=[]
    for i,l in enumerate(lines):
        a,sr=k.create(l,voice='am_michael',speed=0.9,lang='en-us')
        a=ss.resample_poly(a,SR//1000,sr//1000).astype(np.float32); a=trim(a)
        pause=0.9 if i in EXTRA else 0.35
        st=max(ru[i]['start'], prev+pause)
        out[int(st*SR):int(st*SR)+len(a)]+=a*0.9
        prev=st+len(a)/SR
        sent.append({'text':l,'start':st,'end':prev})
    end=prev
out=out[:int((end+0.5)*SR)]
sf.write(f'voice_{LANG}.wav',out,SR)
if LANG=='en':
    W=whisper_words(f'voice_{LANG}.wav')
    al=align(lines,W)
    for i in range(len(lines)):
        sent[i]['words']=al[i]; sent[i]['start']=al[i][0][1]; sent[i]['end']=al[i][-1][2]
scenes=[sent[i]['start']-(0 if n==0 else 0.55) for n,i in enumerate(SCENE_FIRST)]
scenes[0]=0.0
json.dump({'sentences':sent,'scenes':scenes,'voice_end':end},open(f'cues_{LANG}.json','w'),ensure_ascii=False,indent=1)
print(LANG,'voice end',round(end,2),'scenes',[round(s,2) for s in scenes])
for s in sent: print(f"{s['start']:6.2f}-{s['end']:6.2f} {s['text'][:60]}")
