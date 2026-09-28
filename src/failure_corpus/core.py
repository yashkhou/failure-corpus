from dataclasses import dataclass,asdict
import hashlib,re
@dataclass
class Failure:
    framework:str; test:str; message:str; context:str; fingerprint:str=''; count:int=1
    def as_dict(self): return asdict(self)
def normalize(s):
    s=re.sub(r'\b\d{4}-\d\d-\d\d[T ][0-9:.+\-Z]+\b','<time>',s); s=re.sub(r'(/[^\s:]+)+','<path>',s); s=re.sub(r':\d+(?::\d+)?',':<line>',s); s=re.sub(r'\b0x[0-9a-fA-F]+\b','<addr>',s)
    return re.sub(r'\s+',' ',s).strip()
def parse(text):
    out=[]; lines=text.splitlines()
    for i,line in enumerate(lines):
        framework='generic'; test='unknown'; msg=None
        if line.startswith('FAILED '): framework='pytest'; rest=line[7:]; test=rest.split(' - ',1)[0]; msg=rest.split(' - ',1)[1] if ' - ' in rest else rest
        elif re.match(r'\s*●\s+',line): framework='jest'; test=re.sub(r'^\s*●\s+','',line).strip(); msg=lines[i+1].strip() if i+1<len(lines) else test
        elif re.search(r'\b(ERROR|Exception|AssertionError)\b',line): msg=line.strip()
        if msg:
            ctx='\n'.join(lines[max(0,i-1):min(len(lines),i+3)]); key=normalize(framework+'|'+test+'|'+msg); fp=hashlib.sha256(key.encode()).hexdigest()[:16]; out.append(Failure(framework,test,msg,ctx,fp))
    return out
def dedupe(records):
    d={}
    for r in records:
        if r.fingerprint in d: d[r.fingerprint].count+=1
        else: d[r.fingerprint]=r
    return list(d.values())
