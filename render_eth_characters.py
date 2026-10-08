import numpy as np, cv2, random, math, subprocess, glob
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
random.seed(3); np.random.seed(3)
W,H,FPS,DUR=1280,720,24,84
fp=[p for p in glob.glob('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')][0]
F=lambda s: ImageFont.truetype(fp,s)
F_big,F_mid,F_cap,F_hud,F_sm=F(64),F(34),F(30),F(44),F(22)
COL={'zei':(0,200,180),'bai':(255,70,160),'mu':(245,185,60),'fin':(150,110,255)}
import os
EV=[(0,5,"NARRATOR","Snowmoon. Chapter seven. The final round."),
(5,8.5,"NARRATOR","Tomorrow, Zei faces Bai in the final."),
(8.5,12,"ZEI","One more look at the strategy."),
(12,18,"NARRATOR","Smoke rises over Dzego as the friends climb to the arena."),
(18,20,"BAI","Zei, look at that smoke."),
(20,24,"NARRATOR","This time, each player's AI can read the other's thoughts."),
(24.5,27,"MU","Dze go ba fau gie!"),
(28,34,"NARRATOR","The battle begins. Gliders, spaceships and walls clash across the grid."),
(34,37,"BAI","Got you. The diagonals are mine."),
(37,46,"NARRATOR","Zei walks into the trap and falls behind, seventeen to twenty-two."),
(46,49,"ZEI","Wait... I see it."),
(49,58,"NARRATOR","Sixteen strategies. One hidden factory. A move Bai never saw coming."),
(58,66,"NARRATOR","The grid turns. Fourteen to eleven, and Zei is ahead."),
(66,69,"NARRATOR","Twelve to six. The arena erupts."),
(69,73.5,"BAI","I resign. Well played, Zei."),
(74,80,"MU","Winning is not only thinking well. It is also knowing what to hide."),
(80,84,"NARRATOR","Zei keeps one letter. For his eyes only.")]
VOICE=None
if os.path.exists('voice.wav'):
    subprocess.run("ffmpeg -y -loglevel error -i voice.wav -ac 1 -ar 8000 voice_mono.wav",shell=True,check=True)
    sr_,v=wavfile.read('voice_mono.wav'); v=np.abs(v.astype(np.float32)); v/= (np.percentile(v,98)+1e-6); VOICE=(v,sr_)
def amp_at(t):
    if VOICE is not None:
        v,sr_=VOICE; i=int(t*sr_); seg=v[i:i+int(sr_/FPS)]; return float(min(1,seg.mean()*1.6)) if len(seg) else 0
    return max(0.0,math.sin(t*13)*math.sin(t*4.1+1))**0.6
CUR=("",0)
KEY=[(28,17,22),(44,17,22),(50,14,11),(58,14,11),(66,12,6),(74,12,6)]
def score(t):
    if t<28 or t>74.5: return None
    for (t0,a0,b0),(t1,a1,b1) in zip(KEY,KEY[1:]):
        if t0<=t<=t1:
            f=(t-t0)/(t1-t0); return round(a0+(a1-a0)*f),round(b0+(b1-b0)*f)
def mix(c,o,a): return tuple(int(c[i]*(1-a)+o[i]*a) for i in range(3))
def eth(d,cx,cy,s,col,mood='smile',look=0,t=0,amp=0):
    L=mix(col,(255,255,255),.35); D=mix(col,(0,0,0),.4)
    P=lambda pts:[(cx+x*s,cy+y*s) for x,y in pts]
    d.polygon(P([(0,-70),(-40,2),(0,-14)]),fill=L); d.polygon(P([(0,-70),(40,2),(0,-14)]),fill=col)
    d.polygon(P([(-40,2),(0,22),(40,2),(0,-14)]),fill=mix(col,(0,0,0),.15))
    d.polygon(P([(-40,14),(0,70),(0,34)]),fill=L); d.polygon(P([(40,14),(0,70),(0,34)]),fill=D)
    blink=(int(t*2.3)%7==0) and (t*2.3%1)<0.25
    for ex in (-12,12):
        if blink: d.line([(cx+(ex-6)*s,cy-4*s),(cx+(ex+6)*s,cy-4*s)],fill=(20,20,30),width=max(2,int(2*s)))
        else:
            r=(8 if mood!='shock' else 11)*s
            d.ellipse([cx+ex*s-r,cy-4*s-r,cx+ex*s+r,cy-4*s+r],fill=(255,255,255))
            pr=3.5*s; d.ellipse([cx+(ex+look*3)*s-pr,cy-4*s-pr,cx+(ex+look*3)*s+pr,cy-4*s+pr],fill=(15,15,30))
    mx,my=cx,cy+10*s
    if mood=='smile': d.arc([mx-12*s,my-8*s,mx+12*s,my+8*s],20,160,fill=(20,20,30),width=max(2,int(3*s)))
    elif mood=='frown': d.arc([mx-10*s,my,mx+10*s,my+14*s],200,340,fill=(20,20,30),width=max(2,int(3*s)))
    elif mood=='shock': d.ellipse([mx-6*s,my-3*s,mx+6*s,my+9*s],fill=(30,10,20))
    elif mood=='talk': hh=(2+12*amp)*s; d.ellipse([mx-(6+4*amp)*s,my+3*s-hh/2,mx+(6+4*amp)*s,my+3*s+hh/2],fill=(40,10,20))
    elif mood=='open': d.ellipse([mx-9*s,my-5*s,mx+9*s,my+8*s],fill=(40,10,20))
def body(d,cx,cy,s,col,armL=(-40,60),armR=(40,60),bob=0):
    cy=cy+bob
    shirt=mix(col,(0,0,0),.55)
    d.rounded_rectangle([cx-30*s,cy+78*s,cx+30*s,cy+160*s],radius=int(14*s),fill=shirt)
    for sx,(ax,ay) in ((-1,armL),(1,armR)):
        d.line([(cx+sx*28*s,cy+90*s),(cx+sx*28*s+ax*s,cy+90*s+ay*s)],fill=shirt,width=int(16*s))
        d.ellipse([cx+sx*28*s+ax*s-8*s,cy+90*s+ay*s-8*s,cx+sx*28*s+ax*s+8*s,cy+90*s+ay*s+8*s],fill=mix(col,(255,255,255),.2))
    for sx in (-1,1): d.line([(cx+sx*12*s,cy+158*s),(cx+sx*12*s,cy+235*s)],fill=(30,30,50),width=int(14*s))
def person(d,name,cx,cy,s,mood='smile',armL=(-40,60),armR=(40,60),look=0,t=0,bobamp=4):
    amp=0
    if name==CUR[0]: mood='talk'; amp=CUR[1]
    bob=math.sin(t*3+hash(name)%7)*bobamp+(amp*3*s if name==CUR[0] else 0)
    body(d,cx,cy,s,COL[name],armL,armR,bob); eth(d,cx,cy+bob,s,COL[name],mood,look,t,amp)
def grad(c1,c2):
    a=np.linspace(0,1,H)[:,None,None]; return Image.fromarray((np.array(c1)*(1-a)+np.array(c2)*a).repeat(W,1).astype(np.uint8))
BG={'dark':grad((10,8,30),(26,16,56)),'warm':grad((255,190,120),(110,60,120)),'sky':grad((40,80,150),(220,170,150)),'toast':grad((24,20,60),(70,40,90)),'arena':grad((8,6,22),(30,14,52)),'calm':grad((20,30,60),(60,50,110))}
# sim
GW,GH=80,45
g=np.zeros((GH,GW),np.uint8); g[:,:GW//2][np.random.rand(GH,GW//2)<.2]=1; g[:,GW//2:][np.random.rand(GH,GW-GW//2)<.2]=2
def nbc(x):
    r=np.zeros_like(x)
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dy or dx: r+=np.roll(np.roll(x,dy,0),dx,1)
    return r
def step(g):
    a=(g>0).astype(np.float32); z=(g==1).astype(np.float32); b=(g==2).astype(np.float32)
    n=nbc(a);nz=nbc(z);nb=nbc(b)
    keep=(a>0)&((n==2)|(n==3)); born=(a==0)&(n==3)
    o=np.zeros_like(g); o[keep]=g[keep]; o[born]=np.where(nz[born]>nb[born],1,2); return o
GL=[(0,1),(1,2),(2,0),(2,1),(2,2)]
def inject(g,side):
    y=random.randint(3,GH-6); x=random.randint(2,12) if side==1 else random.randint(GW-14,GW-4)
    for dy,dx in GL: g[(y+dy)%GH,(x+(dx if side==1 else 2-dx))%GW]=side
def panel(t):
    img=np.full((GH,GW,3),(12,10,30),np.uint8); img[g==1]=COL['zei']; img[g==2]=COL['bai']
    big=cv2.resize(img,(640,360),interpolation=cv2.INTER_NEAREST)
    gl=cv2.resize(cv2.GaussianBlur(img,(0,0),1.5),(640,360)); big=np.clip(big.astype(np.int32)+gl*0.6,0,255).astype(np.uint8)
    return Image.fromarray(big)
def wrap(d,text,font,maxw):
    out=[];cur=""
    for w in text.split():
        if d.textlength((cur+" "+w).strip(),font=font)<=maxw: cur=(cur+" "+w).strip()
        else: out.append(cur);cur=w
    out.append(cur); return out
def star(d,cx,cy,r1,r2,n,col):
    pts=[]
    for i in range(n*2):
        r=r1 if i%2==0 else r2; a=math.pi*i/n; pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    d.polygon(pts,fill=col)
def ctext(d,y,text,font,fill=(255,255,255)):
    w=d.textlength(text,font=font); d.text(((W-w)/2,y),text,font=font,fill=fill)
out=cv2.VideoWriter('silent3.mp4',cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
LABEL=[(0,5,""),(5,12,"Pafogai Du, Dzego"),(12,20,"Rainmoon 24"),(20,28,"The new rule"),(28,36,"MINPENTAI  -  THE FINAL"),(36,46,"MINPENTAI  -  THE FINAL"),(46,58,"MINPENTAI  -  THE FINAL"),(58,66,"MINPENTAI  -  THE FINAL"),(66,74,"MINPENTAI  -  THE FINAL"),(74,80,"After the match"),(80,84,"")]
for i in range(DUR*FPS):
    t=i/FPS
    _e=[e for e in EV if e[0]<=t<e[1]]
    CUR=(_e[0][2].lower(),amp_at(t)) if _e and _e[0][2]!='NARRATOR' else ('',0)
    if 28<=t<74 and i%3==0:
        g=step(g)
        if (i//3)%20==0: inject(g,1);inject(g,2)
    if t<5: bg='dark'
    elif t<12: bg='warm'
    elif t<20: bg='sky'
    elif t<28: bg='toast'
    elif t<74: bg='arena'
    else: bg='calm'
    im=BG[bg].copy(); d=ImageDraw.Draw(im)
    if t<5:
        for k,n in enumerate(['zei','bai','mu','fin']): person(d,n,300+k*230,330,0.8,'smile',t=t)
        ctext(d,70,"SNOWMOON",F_big)
    elif t<12:
        d.rectangle([0,560,W,H],fill=(90,50,70)); d.rectangle([320,470,700,490],fill=(60,30,50))
        person(d,'zei',500,230,0.85,'smile',(-30,70),(30,60),look=1,t=t)
        d.rectangle([548,450,590,470],fill=(40,40,70)); d.rectangle([402,452,432,472],fill=(240,240,240))
        for k in range(3): d.line([(417+math.sin(t*4+k)*5,440-k*14),(417+math.sin(t*4+k+1)*5,426-k*14)],fill=(255,255,255),width=3)
        rx=1300-min(1,(t-5)/4)*470
        d.rounded_rectangle([rx,420,rx+150,560],radius=14,fill=(70,80,110)); d.rectangle([rx+15,435,rx+135,490],fill=(10,20,40))
        d.line([(rx+25,462),(rx+125,462)],fill=(100,100,140),width=4); kx=rx+25+((math.sin(t*2)+1)/2)*100; d.ellipse([kx-8,454,kx+8,470],fill=COL['zei'])
        d.ellipse([rx+20,545,rx+50,575],fill=(30,30,40)); d.ellipse([rx+100,545,rx+130,575],fill=(30,30,40))
    elif t<20:
        d.polygon([(0,720),(0,560),(640,170),(1280,560),(1280,720)],fill=(60,70,100)); d.polygon([(640,170),(1280,560),(1280,720),(900,720)],fill=(40,50,80))
        p=(t-12)/8
        for k,n in enumerate(['zei','fin','bai']):
            u=0.18+0.5*p-k*0.07; x=u*1280; y=560-(560-170)*min(1,x/640) if x<640 else 170+(x-640)*(390/640)
            person(d,n,x,y-117,0.5,'smile',(-20,40),(20,40),t=t+k)
        for k in range(8):
            r=30+((t*20+k*13)%50); sy=500-((t*40+k*60)%320); d.ellipse([1050+k*18-r,sy-r,1050+k*18+r,sy+r],fill=(90,90,100))
    elif t<28:
        d.rectangle([0,600,W,H],fill=(40,25,60))
        p=min(1,max(0,(t-23)/2.5)); gx=lambda base,c:base+(640-base)*0.35*p
        person(d,'mu',640,150,0.9,'smile',(-60,50),(60-p*10,-20-p*50),t=t)
        person(d,'zei',340,180,0.8,'smile',(-30,60),(60+p*50,-10-p*45),look=1,t=t)
        person(d,'bai',940,180,0.8,'smile',(-60-p*50,-10-p*45),(30,60),look=-1,t=t)
        if t>=26:
            fl=max(0,1-(t-26)/0.6); star(d,640,150,90*fl+10,40*fl+5,8,(255,255,200))
    elif t<74:
        d.rectangle([0,640,W,H],fill=(25,15,45))
        for r in range(2):
            for k in range(36): d.ellipse([20+k*36+(r*18)+math.sin(t*3+k)*3-12,660+r*30+math.sin(t*4+k+r)*4-12,20+k*36+(r*18)+12,660+r*30+12],fill=(70+k*3%80,60,120))
        pn=panel(t); im.paste(pn,(320,80)); d=ImageDraw.Draw(im); d.rectangle([318,78,962,442],outline=(160,140,255),width=3)
        if 46<=t<66:
            pulse=0.5+0.5*math.sin(t*6); x0=480;y0=210
            d.rectangle([x0,y0,x0+120,y0+70],outline=(255,240,120),width=int(3+3*pulse)); d.text((x0+8,y0+18),"FACTORY",font=F_sm,fill=(255,240,120))
        mz=mb='smile';az=ab=(30,60);lz=0
        if 36<=t<46: mz='frown';mb='smile'
        if 46<=t<58: mz='open'
        if 58<=t<66: mb='shock';mz='smile'
        if 66<=t<74: mb='frown';mz='smile';ab=(60,-80)
        person(d,'zei',180,230,0.95,mz,(-30,60),(40,60) if t<66 else (50,-70),look=1,t=t)
        person(d,'bai',1100,230,0.95,mb,(-40-0,60) if t<66 else (-60,60),(30,60) if t<66 else (60,-90),look=-1,t=t)
        person(d,'mu',90,430,0.4,'frown' if 36<=t<46 else 'smile',t=t); person(d,'fin',1190,430,0.4,'shock' if 36<=t<46 else 'smile',t=t)
        if 28<=t<31: ctext(d,230,str(3-int(t-28)),F(150),(255,255,255))
        if 47<=t<49: star(d,200,180,95,45,9,(255,240,110)); d.text((125,160),"CLICK!",font=F_mid,fill=(40,30,0))
        if 66<=t<74:
            for k in range(70):
                x=(k*97+t*45*(1+k%3))%W; y=((k*53+t*140*(1+k%2)))%H; c=[(255,90,160),(0,215,190),(255,220,90),(150,110,255)][k%4]
                d.rectangle([x,y,x+9,y+14],fill=c)
            ctext(d,230,"12 - 6",F_big,(255,255,255))
        sc=score(t)
        if sc:
            d.text((330,18),"ZEI",font=F_hud,fill=COL['zei']); d.text((330+95,18),str(sc[0]),font=F_hud,fill=(255,255,255))
            tw=d.textlength("BAI",font=F_hud); d.text((950-tw,18),"BAI",font=F_hud,fill=COL['bai']); d.text((950-tw-70,18),str(sc[1]),font=F_hud,fill=(255,255,255))
    elif t<80:
        person(d,'mu',640,120,1.15,'smile',(-50,60),(55,0),t=t)
        person(d,'zei',250,260,0.7,'smile',look=1,t=t); person(d,'bai',1030,260,0.7,'smile',look=-1,t=t)
        d.rounded_rectangle([780,70,1220,200],radius=26,fill=(255,255,255)); d.polygon([(820,200),(860,200),(760,260)],fill=(255,255,255))
        d.text((810,95),"Win with your mind,",font=F_cap,fill=(30,20,60)); d.text((810,140),"and keep some secrets.",font=F_cap,fill=(30,20,60))
    else:
        person(d,'zei',640,110,1.1,'smile',(-30,60),(-5,40),look=0,t=t)
        gl=0.5+0.5*math.sin(t*5); d.rounded_rectangle([600,410,740,490],radius=8,fill=(110,50,170),outline=(210,170,255),width=int(2+3*gl)); d.line([(600,410),(670,455),(740,410)],fill=(210,170,255),width=3)
        ctext(d,520,"FOR ZEI'S EYES ONLY",F_mid,(230,200,255))
    lab=[l for a,b,l in LABEL if a<=t<b][0]
    if lab and t>=5:
        d=ImageDraw.Draw(im); w=d.textlength(lab,font=F_sm)
        if not (28<=t<74): d.text(((W-w)/2,24),lab,font=F_sm,fill=(255,255,255))
    if _e:
        s0,s1=_e[0][0],_e[0][1]; cap=(_e[0][2]+': ' if _e[0][2]!='NARRATOR' else '')+_e[0][3]
    else: s0,s1,cap=0,0,''
    al=min(1,(t-s0)/0.3,(s1-t)/0.3) if cap else 0; crop=im.crop((0,H-130,W,H)).convert("RGBA"); ov=Image.new("RGBA",crop.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rectangle([0,0,W,130],fill=(0,0,0,int(150*al)))
    ls=wrap(od,cap,F_cap,1120); y=65-len(ls)*19
    for ln in ls:
        w=od.textlength(ln,font=F_cap); od.text(((W-w)/2,y),ln,font=F_cap,fill=(255,255,255,int(255*al))); y+=38
    im.paste(Image.alpha_composite(crop,ov).convert("RGB"),(0,H-130))
    out.write(cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR))
out.release()
# srt + voice script
def ts(x): return "%02d:%02d:%02d,%03d"%(x//3600,(x%3600)//60,int(x%60),int((x%1)*1000))
open('/mnt/user-data/outputs/snowmoon-ch7/subtitles.srt','w').write("\n".join("%d\n%s --> %s\n%s\n"%(i+1,ts(a),ts(b-0.2),(sp+': ' if sp!='NARRATOR' else '')+c) for i,(a,b,sp,c) in enumerate(EV)))
open('/mnt/user-data/outputs/snowmoon-ch7/voiceover.txt','w').write("Record ONE continuous 84-second track (voice.wav): each line starts at its time. Silence in between. Characters' mouths move on lines marked ZEI/BAI/MU.\nNARRATOR = calm deep voice. ZEI = young male. BAI = young female. MU = warm adult female.\n\n"+"\n".join("[%02d:%04.1f - %02d:%04.1f] %s: %s"%(a//60,a%60,b//60,b%60,sp,c) for a,b,sp,c in EV)+"\n")
sr=44100; tt=np.linspace(0,DUR,sr*DUR,endpoint=False)
au=0.18*np.sin(2*np.pi*55*tt)+0.1*np.sin(2*np.pi*82.4*tt)+0.05*np.sin(2*np.pi*110*tt); au*=0.7+0.3*np.sin(2*np.pi*0.08*tt)
ph=tt%0.5; au+=np.sin(2*np.pi*(60+120*np.exp(-ph*30))*ph)*np.exp(-ph*9)*0.3*((tt>=28)&(tt<74))
for ct in (26,47,58,66,80):
    x=tt-ct; m=(x>=0)&(x<3); au+=m*0.18*(np.sin(2*np.pi*523.25*x)+0.5*np.sin(2*np.pi*784*x))*np.exp(-np.clip(x,0,9)*1.5)
au*=np.minimum(1,np.minimum(tt/2,(DUR-tt)/3)); au=au/np.max(np.abs(au))*0.8
wavfile.write('music2.wav',sr,(au*32767).astype(np.int16))
MUX="ffmpeg -y -loglevel error -i silent3.mp4 -i music2.wav "+("-i voice.wav -filter_complex '[1:a]volume=0.3[m];[2:a]volume=1.0[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]' -map 0:v -map '[a]' " if VOICE is not None else "")
subprocess.run(MUX+"-c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 160k -shortest /mnt/user-data/outputs/snowmoon_chapter7_eth_voice.mp4",shell=True,check=True)
print("done")
