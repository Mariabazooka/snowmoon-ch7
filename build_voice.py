import re, subprocess, numpy as np, tts
from scipy.io import wavfile
src=open('make3.py').read(); a=src.index("EV=["); b=src.index("VOICE=None")
ns={}; exec(src[a:b].replace("import os",""),ns); EV=ns['EV']
SR=22050; DUR=84
VOICE={'NARRATOR':('rms',0.93),'ZEI':('awb',1.0),'BAI':('slt',1.04),'MU':('slt',0.86)}
SPELL={"Dze go ba fau gie!":"Dzeh go bah foh gee!","Dzego":"Dzeh go","Snowmoon":"Snow moon","Minpentai":"Min pen tie"}
track=np.zeros(SR*DUR,np.float32)
for i,(s,e,sp,text) in enumerate(EV):
    v,pitch=VOICE[sp]; t=text
    for k,x in SPELL.items(): t=t.replace(k,x)
    tts.say(t,v,'tts/raw%d.wav'%i)
    def conv(tempo):
        f="asetrate=%d,aresample=%d,atempo=%.4f"%(int(16000*pitch),SR,(1/pitch)*tempo)
        subprocess.run(["ffmpeg","-y","-loglevel","error","-i","tts/raw%d.wav"%i,"-af",f,"-ac","1","-ar",str(SR),"tts/l%d.wav"%i],check=True)
        return wavfile.read("tts/l%d.wav"%i)[1].astype(np.float32)/32768
    x=conv(1.0); win=(e-s)-0.25
    if len(x)/SR>win: x=conv(min(1.5,len(x)/SR/win*1.02)); 
    st=int(s*SR); track[st:st+len(x)]+=x[:len(track)-st]
    print(sp,round(len(x)/SR,2),'/',e-s)
track=track/np.max(np.abs(track))*0.92
wavfile.write('voice.wav',SR,(track*32767).astype(np.int16))
