import numpy as np, cv2, random, math, subprocess
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
random.seed(7); np.random.seed(7)
W,H,FPS,DUR=1280,720,24,84
GW,GH=160,90
import glob
fp=(glob.glob('/usr/share/fonts/**/DejaVuSans-Bold.ttf',recursive=True)+glob.glob('/usr/share/fonts/**/*Bold*.ttf',recursive=True)+glob.glob('/usr/share/fonts/**/*.ttf',recursive=True))[0]
F_big=ImageFont.truetype(fp,54); F_mid=ImageFont.truetype(fp,34); F_cap=ImageFont.truetype(fp,28); F_hud=ImageFont.truetype(fp,40); F_sm=ImageFont.truetype(fp,15)
TEAL=(0,215,190); MAG=(255,60,150)
SEG=[(0,5,"SNOWMOON","Chapter 7  -  The Final Round"),
(5,12,"Pafogai Du, Dzego  -  3724 Rainmoon 23","Zei studies Minpentai alone. Tomorrow he faces his friend Bai."),
(12,20,"Rainmoon 24","Smoke rises over the city. Zei, Fin and Bai climb the mountain pyramid to the final."),
(20,28,"THE NEW RULE","Each player gets a personal AI, and can read the other AI's thoughts."),
(28,36,"","The battle begins. Gliders, spaceships, walls."),
(36,46,"","Bai sets a trap along the diagonals. Zei falls into it. Seventeen to twenty-two."),
(46,58,"","Then something clicks. Sixteen strategies. One hidden factory."),
(58,66,"","Bai never saw it coming. Fourteen to eleven."),
(66,74,"12 - 6","Bai resigns. The audience cheers."),
(74,80,"Mu's lesson","Winning is not only thinking well. It is also knowing what to hide."),
(80,84,"For Zei's eyes only","A dark purple letter. Chapter 8 awaits.")]
KEY=[(0,0,0),(28,17,22),(44,17,22),(50,14,11),(58,14,11),(66,12,6),(84,12,6)]
def score(t):
    for (t0,a0,b0),(t1,a1,b1) in zip(KEY,KEY[1:]):
        if t0<=t<=t1:
            if t0==0: return None
            f=(t-t0)/(t1-t0); return round(a0+(a1-a0)*f),round(b0+(b1-b0)*f)
POOL=["scan glider lanes: diagonal NE ... ok","build wall: west flank layer 3","reflect spaceship off south wall","allocate 80% resources: factory","predict opponent counter: 4 of 16","simulate trigger: glider type / time","defense: diagonals sealed","expand territory, east base","symbol count check","queue glider storm: north"]
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        if d.textlength((cur+" "+w).strip(),font=font)<=maxw: cur=(cur+" "+w).strip()
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def center(d,y,text,font,fill,alpha,maxw=1100):
    for ln in wrap(d,text,font,maxw):
        w=d.textlength(ln,font=font); d.text(((W-w)/2,y),ln,font=font,fill=fill+(alpha,)); y+=font.size+10
    return y
# life
g=np.zeros((GH,GW),np.uint8)
g[:,:GW//2][np.random.rand(GH,GW//2)<.2]=1; g[:,GW//2:][np.random.rand(GH,GW-GW//2)<.2]=2
K=np.ones((3,3),np.float32); K[1,1]=0
def nb_count(x):
    r=np.zeros_like(x)
    for dy in (-1,0,1):
        for dx in (-1,0,1):
            if dy or dx: r+=np.roll(np.roll(x,dy,0),dx,1)
    return r
def step(g):
    a=(g>0).astype(np.float32); z=(g==1).astype(np.float32); b=(g==2).astype(np.float32)
    n=nb_count(a); nz=nb_count(z); nb=nb_count(b)
    keep=(a>0)&((n==2)|(n==3)); born=(a==0)&(n==3)
    out=np.zeros_like(g); out[keep]=g[keep]; out[born]=np.where(nz[born]>nb[born],1,2); return out
GL=[(0,1),(1,2),(2,0),(2,1),(2,2)]
def inject(g,side):
    y=random.randint(5,GH-8); x=random.randint(2,20) if side==1 else random.randint(GW-22,GW-4)
    for dy,dx in GL:
        xx=x+dx if side==1 else x+(2-dx); g[(y+dy)%GH,xx%GW]=side
lines_scan=np.ones((H,W,1),np.float32); lines_scan[::8]=0.82; lines_scan[:,::8]=np.minimum(lines_scan[:,::8],0.82)
out=cv2.VideoWriter('silent.mp4',cv2.VideoWriter_fourcc(*'mp4v'),FPS,(W,H))
N=DUR*FPS
for i in range(N):
    t=i/FPS
    if i%2==0:
        g=step(g)
        if (i//2)%30==0: inject(g,1); inject(g,2)
        if (i//2)%120==0 and np.count_nonzero(g)<400:
            g[np.random.rand(GH,GW)<.05]=random.choice([1,2])
    img=np.zeros((GH,GW,3),np.float32)
    img[g==1]=TEAL; img[g==2]=MAG
    big=cv2.resize(img,(W,H),interpolation=cv2.INTER_NEAREST)*lines_scan
    glow=cv2.resize(cv2.GaussianBlur(img,(0,0),1.8),(W,H),interpolation=cv2.INTER_LINEAR)
    big=np.clip(big+glow*0.9,0,255)
    bg=np.array([14,10,28],np.float32)
    bright=1.0 if 28<=t<74 else 0.3
    if 20<=t<28: bright=0.55
    frame=bg+(big)*bright*(0.92)
    frame=np.clip(frame,0,255).astype(np.uint8)
    im=Image.fromarray(frame).convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    for s0,s1,head,cap in SEG:
        if s0<=t<s1:
            a=int(255*min(1,(t-s0)/0.6,(s1-t)/0.6))
            if head:
                hf=F_big if len(head)<14 else F_mid
                y=250 if t<28 or t>=66 else 120
                if t>=74: y=260
                center(d,y,head,hf,(255,255,255),a)
            d.rectangle([0,H-150,W,H],fill=(0,0,0,int(a*0.6)))
            center(d,H-125,cap,F_cap,(255,255,255),a,1100)
    sc=score(t)
    if sc and t<74.5:
        d.text((60,30),"ZEI",font=F_hud,fill=TEAL+(255,)); d.text((60+110,30),str(sc[0]),font=F_hud,fill=(255,255,255,255))
        tw=d.textlength("BAI",font=F_hud); d.text((W-60-tw,30),"BAI",font=F_hud,fill=MAG+(255,)); d.text((W-60-tw-70,30),str(sc[1]),font=F_hud,fill=(255,255,255,255))
    if 20<=t<58:
        for side,x0,col in ((0,40,TEAL),(1,W-340,MAG)):
            d.rectangle([x0,90,x0+300,215],fill=(0,0,0,110))
            d.text((x0+10,95),("ZEI's AI - transcript" if side==0 else "BAI's AI - transcript"),font=F_sm,fill=col+(255,))
            k=int(t*2)
            for j in range(5):
                d.text((x0+10,120+j*18),POOL[(k+j*3+side*4)%len(POOL)],font=F_sm,fill=(200,255,235,220))
    if 66<=t<74: pass
    im=Image.alpha_composite(im,ov).convert("RGB")
    out.write(cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR))
out.release()
# audio
sr=44100; tt=np.linspace(0,DUR,int(sr*DUR),endpoint=False)
drone=0.18*np.sin(2*np.pi*55*tt)+0.1*np.sin(2*np.pi*82.4*tt+0.5*np.sin(2*np.pi*0.1*tt))+0.05*np.sin(2*np.pi*110*tt)
drone*= (0.7+0.3*np.sin(2*np.pi*0.08*tt))
au=drone.copy()
ph=(tt%0.5)
kick=np.sin(2*np.pi*(60+120*np.exp(-ph*30))*ph)*np.exp(-ph*9)*0.35
mask=((tt>=28)&(tt<74)).astype(float); au+=kick*mask
ri=((tt>=50)&(tt<58)); au+=ri*0.12*np.sin(2*np.pi*(220+ (tt-50)*110)*tt)*((tt-50)/8).clip(0,1)
for ct in (46,58,66,80):
    m=(tt>=ct)&(tt<ct+3); x=tt-ct
    au+=m*0.18*(np.sin(2*np.pi*523.25*x)+0.5*np.sin(2*np.pi*784*x))*np.exp(-x*1.5)
fade=np.minimum(1,np.minimum(tt/2,(DUR-tt)/3)); au*=fade
au=au/np.max(np.abs(au))*0.85
wavfile.write('music.wav',sr,(au*32767).astype(np.int16))
subprocess.run("ffmpeg -y -loglevel error -i silent.mp4 -i music.wav -c:v libx264 -pix_fmt yuv420p -crf 20 -c:a aac -b:a 160k -shortest /mnt/user-data/outputs/snowmoon_chapter7.mp4",shell=True,check=True)
print("done")
