"""Extract verb-attaching grammar points from the two CC BY-SA 4.0 datasets.
Usage: python3 -I extract.py <jld grammar.json> <openjlpt grammar dir> <out.json>
"""
import json, re, sys, os, collections
import pykakasi
kks = pykakasi.kakasi()

JP = re.compile(r'[぀-ヿ一-鿿々〜～]')

def reading(s):
    return "".join(t['hira'] for t in kks.convert(s))

BASE_RULES = [  # (regex on the first segment, base)
    (r'volitional|意向', 'vol'),
    (r'ば-?form|仮定|V-?ば\b|V ば', 'ba'),
    (r'potential', 'pot'),
    (r'causative[- ]passive', 'cp'),
    (r'causative', 'caus'),
    (r'passive', 'pas'),
    (r'imperative', 'imp'),
    (r'ます-?stem|masu|Verb[- ]stem|V[- ]stem|連用', 'i'),
    (r'negative stem|ない-?stem|nai-stem|未然', 'a'),
    (r'ない-?form|V[- ]?ない|Verb-?ない|nai-form|negative', 'n'),
    (r'たら', 'tara'),
    (r'て-?form|V[- ]?て|Verb-?て|te-form|V-?で', 'te'),
    (r'た-?form|V[- ]?た|Verb-?た|ta-form|past', 'ta'),
    (r'dict|plain|Plain|Verb|V\b', 'dict'),
]

def base_of(seg):
    for rx, b in BASE_RULES:
        if re.search(rx, seg):
            return b
    return None

def clean_suffix(parts, first=''):
    out = []
    if re.search(r'noun|Noun|na-adj', first) and parts and parts[0].strip() in ('の', 'な', 'である', 'だ'):
        parts = parts[1:]
    for p in parts:
        p = p.strip()
        if re.search(r'\b(V|Verb|noun|Noun|adj|i-adj|na-adj)\b', p) and not JP.search(p.split('/')[0]):
            break  # second verb slot etc.
        alt = p.split(' / ')[0].strip()
        alt = re.sub(r'\s*\(.*?\)\s*$', lambda m: m.group(0) if JP.search(m.group(0)) else '', alt)
        if not JP.search(alt):
            break
        out.append(alt)
    s = "".join(out)
    s = s.replace('〜', '').replace('～', '').replace(' ', '')
    return s

def parse(pattern, formation):
    # prefer the formation's first verb clause if it is more explicit
    cands = []
    for src in (pattern, formation):
        for clause in re.split(r';|\.\s', src):
            if ' + ' not in clause:
                continue
            segs = clause.split(' + ')
            first = segs[0]
            if not re.search(r'\bV\b|Verb|V-|V\s|Plain|plain|ます-stem|stem|dict', first):
                continue
            b = base_of(first)
            if not b:
                continue
            suf = clean_suffix(segs[1:], first)
            if suf:
                cands.append((b, suf))
                break
        if cands:
            break
    if not cands:
        return None
    b, suf = cands[0]
    # normalise bases that carry part of the ending
    if b == 'tara':
        b, suf = 'ta', 'ら' + suf
    if b == 'a' and not re.match(r'[ずざんぬ]', suf):
        b = 'n'
        if not suf.startswith('な'):
            suf = 'ない' + suf
    if b == 'n' and not suf.startswith('な'):
        suf = 'ない' + suf
    if b == 'n':
        suf = suf[2:] if suf.startswith('ない') else suf
        suf = 'ない' + suf
    if b == 'vol':
        suf = re.sub(r'^[うよ]う', '', suf)
    if b == 'ba':
        suf = re.sub(r'^ば', '', suf)
    if b == 'te':
        suf = re.sub(r'^[てで]', '', suf)
    if b == 'ta':
        suf = re.sub(r'^[ただ]', '', suf)
    return b, suf

def main(jld_path, oj_dir, out):
    rows, skipped = [], []
    g = json.load(open(jld_path))['grammar_points']
    for x in g:
        p = parse(x['pattern'], x.get('formation', ''))
        if not p:
            skipped.append(('jld', x['level'], x['pattern']))
            continue
        b, suf = p
        ex = (x.get('examples') or [{}])[0]
        rows.append(dict(id='g.' + x['id'], lv=x['level'], base=b, suf=suf, sufR=reading(suf),
                         gloss=x['meaning_en'], pat=x['pattern'], x=x.get('meaning_detailed', ''),
                         notes=(x.get('formation_notes') or [])[:2],
                         j=ex.get('japanese', ''), e=ex.get('english', ''), src='jld'))
    seen = {(r['base'], r['suf']) for r in rows}
    for lvl in ['n5', 'n4', 'n3', 'n2', 'n1']:
        fp = os.path.join(oj_dir, lvl + '.json')
        if not os.path.exists(fp):
            continue
        for x in json.load(open(fp)):
            pat = x.get('pattern', '')
            core = re.split(r'[/（(]', pat)[0].strip()
            if core.count('〜') + core.count('～') != 1 or not core.startswith(('〜', '～')):
                skipped.append(('oj', x['level'], pat)); continue
            core_s = re.sub(r'[（(].*?[）)]', '', core[1:]).strip()
            form = x.get('formation', '')
            m = None; cands=[]
            for mm in re.finditer(r'Verb-([a-zA-Zぁ-ん]+)(?: stem)? \+ ((?:の \+ )?[^/+]+)(?= /|$| \+ Noun)', form):
                cand = mm.group(2).replace('の + ', 'の').replace(' ', '')
                if core_s and core_s.lstrip('てでただ').split('〜')[0] in cand and not re.search(r'[A-Za-z]', cand):
                    cands.append(mm)
            pref = [c for c in cands if c.group(1).lower()!='nai' or core_s.startswith('な')]
            m = (pref or cands or [None])[0]
            if not m:
                skipped.append(('oj', x['level'], pat)); continue
            tag = 'V-' + m.group(1)
            suf = m.group(2).replace('の + ', 'の').replace(' ', '').strip()
            b = {'dict':'dict','plain':'dict','ta':'ta','te':'te','nai':'n','stem':'i','masu':'i','vol':'vol','volitional':'vol','ba':'ba','potential':'pot','passive':'pas','causative':'caus'}.get(m.group(1).lower(), base_of(tag) or 'dict')
            if b == 'n' and m.group(0).find('nai stem') >= 0: b = 'a'
            if b == 'n' and not suf.startswith('ない'): suf = 'ない' + suf
            if not suf: skipped.append(('oj', x['level'], pat)); continue
            key = (b, suf)
            if key in seen: continue
            seen.add(key)
            ex = (x.get('examples') or [{}])[0]
            rows.append(dict(id='o.' + x['id'], lv=x['level'], base=b, suf=suf, sufR=reading(suf),
                             gloss=x.get('meaning', ''), pat=pat, x='Formation: ' + form,
                             notes=[], j=ex.get('ja', ''), e=ex.get('en', ''), src='oj'))
    json.dump(rows, open(out, 'w'), ensure_ascii=False, indent=0)
    print('kept', len(rows), collections.Counter(r['base'] for r in rows), collections.Counter(r['lv'] for r in rows))
    print('skipped', len(skipped))
    json.dump(skipped, open(out + '.skipped.json', 'w'), ensure_ascii=False, indent=0)

if __name__ == '__main__':
    main(*sys.argv[1:])
