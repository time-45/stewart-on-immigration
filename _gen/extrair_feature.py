#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_feature.py — converte um artigo de série (Serie-*/...html) numa entrada de feature
para o site, e faz MERGE em _features.json (por slug + idioma).

Uso: python3 extrair_feature.py <artigo.html> --slug <slug> --lang en [--track "PERM Proposed Rule Series"] [--cover URL] --out <_features.json>
"""
import sys, os, re, json, html as _html, argparse

def clean(s): return re.sub(r'\s+', ' ', s or '').strip()
def text(s):  return _html.unescape(clean(re.sub(r'<[^>]+>', '', s or '')))

def parse(path):
    h = open(path, encoding='utf-8').read()
    mk = re.search(r'class="kicker">(.*?)</div>', h, re.S)
    mh = re.search(r'<div class="lead">.*?<h2>(.*?)</h2>', h, re.S)
    mde= re.search(r'class="deck">(.*?)</div>', h, re.S)
    kicker = text(mk.group(1)) if mk else ''
    title  = text(mh.group(1)) if mh else ''
    deck   = text(mde.group(1)) if mde else ''
    # corpo: do fim do .deck até o <div class="exped"
    after = h
    if mde: after = h[mde.end():]
    after = re.split(r'<div class="exped"', after)[0]
    # captura <p>…</p> e <h3>…</h3> na ordem
    blocks = []
    for m in re.finditer(r'<(p|h3)\b[^>]*>(.*?)</\1>', after, re.S):
        tag = m.group(1); content = clean(m.group(2))
        if not text(content): continue
        blocks.append(f'<{tag}>{content}</{tag}>')
    return {'kicker':kicker, 'title':title, 'deck':deck, 'body':blocks}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('article'); ap.add_argument('--slug', required=True)
    ap.add_argument('--lang', required=True); ap.add_argument('--track', default='')
    ap.add_argument('--cover', default=''); ap.add_argument('--out', required=True)
    a = ap.parse_args()
    entry_lang = parse(a.article)
    data = {'features': []}
    if os.path.exists(a.out):
        try: data = json.load(open(a.out, encoding='utf-8'))
        except Exception: data = {'features': []}
    feats = data.setdefault('features', [])
    feat = next((f for f in feats if f.get('slug')==a.slug), None)
    if feat is None:
        feat = {'slug': a.slug}
        feats.append(feat)
    if a.track: feat['track'] = a.track
    if a.cover: feat['cover'] = a.cover
    feat[a.lang] = entry_lang
    json.dump(data, open(a.out,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'feature {a.slug} [{a.lang}] -> {a.out}  (title="{entry_lang["title"][:50]}", blocks={len(entry_lang["body"])})')

if __name__ == '__main__':
    main()
