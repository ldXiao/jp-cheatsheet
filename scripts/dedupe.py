import json,re,sys
from playwright.sync_api import sync_playwright
rows=json.load(open(sys.argv[1]))
def clean(s):
    s=re.sub(r'\([A-Za-z+ ].*$','',s); s=re.split(r'(?<=[^\sA-Za-z])(?:or|V|Verb)',s)[0]
    s=re.sub(r'[A-Za-z.;].*$','',s); return s.strip()
for r in rows:
    r['suf']=clean(r['suf'])
rows=[r for r in rows if r['suf'] and not re.search(r'[A-Za-z]',r['suf'])]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg=b.new_page(); pg.goto("file:///home/claude/app/index.html"); pg.wait_for_timeout(1200)
    pg.evaluate("pick(flat.findIndex(v=>v[0]==='書く'))")
    existing=pg.evaluate("""(()=>{const s=new Set();for(const id in REG){let v;try{v=compute(REG[id])}catch(e){continue};[v].flat().filter(Boolean).forEach(p=>s.add(p.k.replace(/[（(].*?[)）]/g,'').replace(/…/g,'')))}return [...s]})()""")
    base={"dict":"S.dict","i":"S.i","n":"S.n","a":"zuStem(S)","te":"S.te","ta":"S.ta","vol":"S.vol","ba":"S.ba","pot":"S.pot"}
    out=[];seen=set()
    ex=set(existing)
    for r in rows:
        k=pg.evaluate(f"(()=>{{const S=cur;const p={base[r['base']]};return p?p.k+{json.dumps(r['suf'])}:null}})()")
        if not k: continue
        norm=re.sub(r'[（(].*?[)）]','',k)
        if norm in ex or norm in seen: continue
        seen.add(norm); r['_k']=k; out.append(r)
    b.close()
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(len(rows),'->',len(out))
import collections; print(collections.Counter(r['base'] for r in out), collections.Counter(r['lv'] for r in out))
