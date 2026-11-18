#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_json.py — lê a edição HTML gerada pela tarefa (edicoes/AAAA-MM-DD-en.html e -pt.html)
e produz o JSON de dados que o gerador do site consome. Assim a tarefa NÃO precisa escrever JSON:
o site deriva do próprio HTML da edição.

Uso: python3 extrair_json.py <en.html> [<pt.html>] <saida.json> [AAAA-MM-DD]
(se só um HTML for passado, gera só aquele idioma)
"""
import sys, os, re, json, html as _html

def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def text(s):
    # texto puro: tira tags e DESESCAPA entidades (o gerador re-escapa com e())
    return _html.unescape(clean(re.sub(r'<[^>]+>', '', s or '')))

def inner(tag_html):
    # remove a tag externa, mantém o conteúdo interno (com HTML)
    m = re.match(r'^\s*<[^>]+>(.*)</[^>]+>\s*$', tag_html, re.S)
    return m.group(1) if m else tag_html

def tagtype_from_class(cls):
    if 't-prop' in cls: return 'prop'
    if 't-alert' in cls: return 'alert'
    return 'final'

def first_sentences(text, maxlen=220):
    t = _html.unescape(clean(re.sub(r'<[^>]+>', '', text)))
    # pega até ~2 frases ou maxlen
    parts = re.split(r'(?<=[.!?])\s+', t)
    out = parts[0] if parts else t
    if len(out) < 130 and len(parts) > 1:
        out = (out + ' ' + parts[1]).strip()
    if len(out) > maxlen:
        out = out[:maxlen].rsplit(' ',1)[0] + '…'
    return out

def parse_lang(path):
    h = open(path, encoding='utf-8').read()
    d = {}
    # issue + date_short do toprule (direita): "Issue No. 80 · 11/17/2026" / "Edição Nº 80 · 17/11/2026"
    m = re.search(r'class="toprule">.*?<span></span><span>(.*?)</span>', h, re.S) or \
        re.search(r'class="toprule">.*?<span>(.*?)</span>\s*</div>', h, re.S)
    issue = None; date_short = ''
    if m:
        tr = clean(m.group(1))
        mi = re.search(r'(?:No\.|Nº)\s*(\d+)', tr)
        if mi: issue = int(mi.group(1))
        md = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', tr)
        if md: date_short = md.group(1)
    # dateline: primeira <span> = data por extenso
    m = re.search(r'class="dateline">\s*<span>(.*?)</span>', h, re.S)
    d['date_long'] = text(m.group(1)) if m else ''
    d['date_short'] = date_short
    # LEAD
    m = re.search(r'<div class="lead">(.*?)</div>\s*<div class="sechead"', h, re.S)
    lead_html = m.group(1) if m else ''
    mk = re.search(r'class="kicker">(.*?)</div>', lead_html, re.S)
    mh = re.search(r'<h2>(.*?)</h2>', lead_html, re.S)
    mde = re.search(r'class="deck">(.*?)</div>', lead_html, re.S)
    body = [clean(x) for x in re.findall(r'<p>(.*?)</p>', lead_html, re.S)]
    msrc = re.search(r'class="src">(.*?)</div>', lead_html, re.S)
    d['lead'] = {
        'kicker': text(mk.group(1)) if mk else '',
        'headline': text(mh.group(1)) if mh else '',
        'deck': text(mde.group(1)) if mde else '',
        'body': body,
        'src': clean(msrc.group(1)) if msrc else ''
    }
    # SEÇÕES: cada sechead h3 inicia uma seção; itens vêm no .grid seguinte
    d['deadlines'] = []
    d['sections'] = []
    # divide por sechead
    blocks = re.split(r'<div class="sechead"><h3>(.*?)</h3></div>', h)
    # blocks[0] = antes da 1ª sechead; depois alterna head, conteúdo
    for i in range(1, len(blocks), 2):
        head = text(blocks[i])
        content = blocks[i+1] if i+1 < len(blocks) else ''
        # corta no próximo sechead/exped/disclaimer/foot
        content = re.split(r'<div class="(?:exped|disclaimer|foot)"', content)[0]
        low = head.lower()
        # Prazos / Deadlines -> brief ul
        if ('prazo' in low) or ('deadline' in low) or ('watch' in low) or ('observar' in low):
            lis = re.findall(r'<li>(.*?)</li>', content, re.S)
            d['deadlines'] = [clean(x) for x in lis]
            continue
        is_persp = ('perspect' in low)
        items = []
        # cada item começa com <div class="item...">; dividimos por esse marcador
        for seg in content.split('<div class="item')[1:]:
            mcls = re.match(r'([^"]*)">', seg)
            mtag = re.search(r'<span class="tag ([^"]+)">(.*?)</span>', seg)
            mh4 = re.search(r'<h4>(.*?)</h4>', seg, re.S)
            ps = [clean(x) for x in re.findall(r'<p>(.*?)</p>', seg, re.S)]
            ms = re.search(r'class="src">(.*?)</div>', seg, re.S)
            if not mh4: continue
            item = {
                'tag': text(mtag.group(2)) if mtag else '',
                'tagtype': tagtype_from_class(mtag.group(1)) if mtag else 'final',
                'title': text(mh4.group(1)),
                'deck': first_sentences(ps[0]) if ps else '',
                'body': ps,
                'src': clean(ms.group(1)) if ms else ''
            }
            if is_persp: item['span'] = True
            items.append(item)
        if items:
            d['sections'].append({'head': head, 'items': items})
    return issue, d

def main():
    args = sys.argv[1:]
    # último arg .json = saída; penúltimo pode ser data
    date = None
    if args and re.match(r'^\d{4}-\d{2}-\d{2}$', args[-1]):
        date = args[-1]; args = args[:-1]
    out = args[-1]; htmls = args[:-1]
    result = {}
    issue = None
    for p in htmls:
        lg = 'pt'
        if re.search(r'-en\.html$', p): lg = 'en'
        iss, dd = parse_lang(p)
        if iss and not issue: issue = iss
        result[lg] = dd
    if not date:
        m = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(htmls[0]))
        date = m.group(1) if m else ''
    result = {'date': date, 'issue': issue or 0, **result}
    json.dump(result, open(out,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'extraído: {date} issue {issue} langs={list(k for k in ("en","pt") if k in result)} -> {out}')

if __name__ == '__main__':
    main()
