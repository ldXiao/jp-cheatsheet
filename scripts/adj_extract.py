import json,re,sys,collections
import pykakasi; kk=pykakasi.kakasi()
rd=lambda s:"".join(t['hira'] for t in kk.convert(s))
JP=re.compile(r'[぀-ヿ一-鿿]')
g=json.load(open(sys.argv[1]))['grammar_points']
out=[]
def first_jp(seg):
    seg=seg.strip().split(' / ')[0].strip()
    seg=re.sub(r'\s*\((?![^)]*[぀-鿿])[^)]*\)','',seg)
    return seg if JP.search(seg) and not re.search(r'[A-Za-z]',seg) else None
for x in g:
    f=x.get('formation','')+' ; '+x['pattern']
    i=n=None
    # i-adjective clause
    m=re.search(r'i-adj(?:ective)?\s*(stem|〜?くて|〜?く|plain|〜い)?\s*\+\s*([^;/+]+)',f)
    if m:
        kind=(m.group(1) or 'plain').replace('〜','')
        suf=first_jp(m.group(2))
        if suf: i=({'stem':'stem','くて':'kute','く':'ku','plain':'plain','い':'plain'}.get(kind,'plain'),suf)
    m=re.search(r'na-adj(?:ective)?\s*(?:stem)?\s*(?:\+\s*(な|だ|である|で|に|なの)\s*)?(?:\+\s*)?([^;/+]+)',f)
    if m:
        conn=m.group(1) or ''
        suf=first_jp(m.group(2))
        if suf: n=(conn,suf)
    if i or n:
        ex=(x.get('examples') or [{}])[0]
        out.append(dict(id='a.'+x['id'],lv=x['level'],gloss=x['meaning_en'],pat=x['pattern'],x=x.get('meaning_detailed',''),
          notes=(x.get('formation_notes') or [])[:2],j=ex.get('japanese',''),e=ex.get('english',''),
          i=i and [i[0],i[1],rd(i[1])], n=n and [n[0],n[1],rd(n[1])]))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(len(out),collections.Counter(o['lv'] for o in out))
for o in out[:400:6]: print(o['lv'],o['i'] and o['i'][:2],o['n'] and o['n'][:2],'|',o['pat'][:45])
