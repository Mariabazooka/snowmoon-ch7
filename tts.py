import ctypes, sys
L='/usr/lib/x86_64-linux-gnu/'
ctypes.CDLL(L+'libflite.so.1',mode=ctypes.RTLD_GLOBAL)
for n in ('libflite_usenglish.so.1','libflite_cmulex.so.1'): ctypes.CDLL(L+n,mode=ctypes.RTLD_GLOBAL)
flite=ctypes.CDLL(L+'libflite.so.1'); flite.flite_init()
def load(v):
    lib=ctypes.CDLL(L+'libflite_cmu_us_%s.so.1'%v,mode=ctypes.RTLD_GLOBAL)
    f=getattr(lib,'register_cmu_us_%s'%v); f.restype=ctypes.c_void_p; return f(None)
V={v:load(v) for v in ('slt','rms','awb','kal16')}
flite.flite_text_to_speech.argtypes=[ctypes.c_char_p,ctypes.c_void_p,ctypes.c_char_p]; flite.flite_text_to_speech.restype=ctypes.c_float
def say(text,voice,path): return flite.flite_text_to_speech(text.encode(),V[voice],path.encode())
if __name__=='__main__':
    for v in V: print(v,say("Winning is not only thinking well. It is also knowing what to hide.",v,'tts/test_%s.wav'%v))
