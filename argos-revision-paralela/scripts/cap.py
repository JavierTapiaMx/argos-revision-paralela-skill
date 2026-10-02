# -*- coding: utf-8 -*-
import csv,re,unicodedata
from PIL import Image,ImageDraw
import os
IMG=os.environ.get('ARGOS_IMG','img')+'/'; TSV=os.environ.get('ARGOS_TSV','tsv')+'/'
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(ch for ch in s if unicodedata.category(ch)!='Mn')
    return re.sub(r'[^a-z0-9]','',s)
_c={}
def words(page):
    if page in _c: return _c[page]
    rows=[]
    with open(TSV+page+'.tsv',encoding='utf-8') as f:
        r=csv.DictReader(f,delimiter='\t',quoting=csv.QUOTE_NONE)
        for x in r:
            if x['level']=='5' and x['text'].strip():
                rows.append((norm(x['text']),int(x['left']),int(x['top']),int(x['width']),int(x['height']),(x['block_num'],x['par_num'],x['line_num'])))
    _c[page]=rows; return rows
def find(page,phrase,nth=0):
    ws=words(page); toks=[norm(t) for t in phrase.split() if norm(t)]
    hits=[]
    for i in range(len(ws)-len(toks)+1):
        if all(ws[i+k][0]==toks[k] or (len(toks[k])>3 and toks[k] in ws[i+k][0]) for k in range(len(toks))):
            seg=ws[i:i+len(toks)]
            x0=min(s[1] for s in seg);y0=min(s[2] for s in seg);x1=max(s[1]+s[3] for s in seg);y1=max(s[2]+s[4] for s in seg)
            hits.append((x0,y0,x1,y1))
    return hits[nth] if len(hits)>nth else None
def union(bs):
    return (min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs))
def render(page,boxes,crop,out,pad=6,scale=1.0):
    """boxes: lista de (x0,y0,x1,y1) a resaltar; crop: (x0,y0,x1,y1) en px de 300 ppp."""
    im=Image.open(IMG+page+'_r.png').convert('RGBA')
    ov=Image.new('RGBA',im.size,(0,0,0,0)); dr=ImageDraw.Draw(ov)
    for b in boxes:
        b=(b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad)
        dr.rectangle(b,fill=(255,235,0,70))
    im=Image.alpha_composite(im,ov).convert('RGB'); dr=ImageDraw.Draw(im)
    for b in boxes:
        b=(b[0]-pad,b[1]-pad,b[2]+pad,b[3]+pad); dr.rectangle(b,outline=(220,0,0),width=4)
    cr=(max(0,crop[0]),max(0,crop[1]),min(im.width,crop[2]),min(im.height,crop[3]))
    c=im.crop(cr)
    if scale!=1.0: c=c.resize((int(c.width*scale),int(c.height*scale)),Image.LANCZOS)
    c.save(out); return c.size

def _match(ws,toks,start=0):
    for i in range(start,len(ws)-len(toks)+1):
        if all(ws[i+k][0]==toks[k] or (len(toks[k])>4 and toks[k] in ws[i+k][0]) for k in range(len(toks))):
            return i
    return -1
def line_boxes(page,start,end=None,nth=0):
    ws=words(page); ts=[norm(t) for t in start.split() if norm(t)]
    i=-1; pos=0
    for _ in range(nth+1):
        i=_match(ws,ts,pos); pos=i+1
        if i<0: return None
    j=i+len(ts)
    if end:
        te=[norm(t) for t in end.split() if norm(t)]
        k=_match(ws,te,j-1 if False else i)
        if k<0: return None
        j=k+len(te)
    seg=ws[i:j]; lines={}
    for w in seg: lines.setdefault(w[5],[]).append(w)
    out=[]
    for ln,l in lines.items():
        out.append((min(w[1] for w in l),min(w[2] for w in l),max(w[1]+w[3] for w in l),max(w[2]+w[4] for w in l)))
    return out
