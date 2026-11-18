#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar_site.py — gera o site público "Stewart on Immigration" (GitHub Pages) a partir
de um modelo de dados da edição: home (estilo Law360), página de edição, arquivo e sobre.
Design aprovado (tokens/componentes em assets/soi.css + assets/soi.js), self-contained.

Uso: python3 gerar_site.py dados/2026-11-17.json out/
Sem args, usa o dado embutido (TODAY) para demonstração.
"""
import os, sys, json, html

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "assets", "soi.css"), encoding="utf-8").read()
JS  = open(os.path.join(HERE, "assets", "soi.js"), encoding="utf-8").read()

SOCIAL = [
    ("Website",  "https://www.joelstewartpa.com/",            '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'),
    ("LinkedIn", "https://www.linkedin.com/in/joelstewartpa", '<path fill="currentColor" stroke="none" d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0zM.5 8h4V24h-4zM8 8h3.8v2.2h.05c.53-1 1.82-2.2 3.75-2.2 4 0 4.7 2.6 4.7 6V24h-4v-7.1c0-1.7 0-3.9-2.4-3.9s-2.7 1.8-2.7 3.8V24H8z"/>'),
    ("Reddit",   "https://www.reddit.com/user/JS-FGI",         '<circle cx="12" cy="13" r="9"/><circle cx="8.5" cy="13" r="1.1" fill="currentColor" stroke="none"/><circle cx="15.5" cy="13" r="1.1" fill="currentColor" stroke="none"/><path d="M9 16.5c1.8 1.2 4.2 1.2 6 0"/><circle cx="19" cy="6.5" r="1.4"/><path d="M15 5.2 16.8 5"/>'),
    ("Substack", "https://joelstewartpa.substack.com",         '<path fill="currentColor" stroke="none" d="M4 4h16v2.4H4zM4 8.3h16V22l-8-4.2L4 22z"/>'),
    ("Instagram","https://www.instagram.com/joel.miami",       '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r="1.1" fill="currentColor" stroke="none"/>'),
]
CONTACT_EMAIL = "js@joelstewartpa.com"
CONTACT_WA    = "+1 954-772-7600"

SHARE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'

NAV = {"en":[("Latest","index.html"),("Archive","archive.html"),("About","about.html")],
       "pt":[("Últimas","index-pt.html"),("Arquivo","archive-pt.html"),("Sobre","about-pt.html")]}
AVAIL = {"en","pt"}  # idiomas gerados nesta rodada; o seletor só aparece p/ o outro se existir
FEATURES = []        # carregado de <dados>/_features.json em main()

def e(x): return html.escape(str(x), quote=True)

def nav_links(items, active):
    out=[]
    for lab,h in items:
        cls=' class="on"' if lab==active else ''
        out.append(f'<a href="{h}"{cls}>{e(lab)}</a>')
    return "".join(out)

import re, unicodedata
def slug(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii','ignore').decode('ascii')
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s[:60] or 'item'

def head(title, desc=""):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>{e(title)}</title>'
            + (f'<meta name="description" content="{e(desc)}">' if desc else '')
            + f'<style>{CSS}</style></head><body>')

def topbar(active, lang, lang_switch_href):
    items = NAV[lang]
    nav = nav_links(items, active)
    other = "pt" if lang=="en" else "en"
    lang_btn = ""
    if other in AVAIL:
        lang_lbl = "PT" if lang=="en" else "EN"
        lang_ttl = "Ler em português" if lang=="en" else "Read in English"
        lang_btn = f'<a class="eicon" href="{lang_switch_href}" title="{lang_ttl}">{lang_lbl}</a>'
    return (
      '<div class="rprog" id="rprog"></div>'
      '<header class="ebar" id="ebar"><div class="ebar-in">'
      f'<a class="ewm" href="{items[0][1]}">Stewart <b>on</b> Immigration</a>'
      f'<nav>{nav}</nav><span class="sp"></span>'
      f'{lang_btn}'
      '<span style="position:relative">'
      f'<button class="eicon" id="shareBtn" title="Share" aria-haspopup="true">{SHARE_SVG}</button>'
      '<div class="shmenu" id="shMenu" style="position:absolute;right:0;top:42px;min-width:168px;background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow2);padding:6px;display:none;flex-direction:column;z-index:70;font-family:var(--sans)">'
      '<button data-sh="copy" style="display:flex;align-items:center;gap:10px;padding:9px 11px;border:0;background:none;color:var(--ink);font-size:13px;font-weight:600;cursor:pointer;border-radius:9px;text-align:left;width:100%">Copy link</button>'
      '<a data-sh="li" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;padding:9px 11px;color:var(--ink);font-size:13px;font-weight:600;border-radius:9px">LinkedIn</a>'
      '<a data-sh="wa" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;padding:9px 11px;color:var(--ink);font-size:13px;font-weight:600;border-radius:9px">WhatsApp</a>'
      '</div></span>'
      '<button class="eicon" id="themeBtn" title="Theme" aria-label="Theme"><svg id="thIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg></button>'
      '</div></header>'
    )

def footer(lang):
    social = "".join(f'<a href="{u}" target="_blank" rel="noopener" title="{e(n)}" aria-label="{e(n)}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{svg}</svg></a>' for n,u,svg in SOCIAL)
    if lang=="en":
        contact = f'Written contact only: <b>{CONTACT_EMAIL}</b> · WhatsApp <b>{CONTACT_WA}</b>'
        legal = ('<b>Disclaimer:</b> This bulletin is provided for general informational purposes only and does not constitute legal advice. '
                 'Reading it, or interacting with any linked content, creates no attorney-client relationship. Consult a qualified attorney before acting on any matter.')
        stamp = '&copy; 2026 <b>Joel Stewart, P.A.</b> · All rights reserved.'
    else:
        contact = f'Contato apenas por escrito: <b>{CONTACT_EMAIL}</b> · WhatsApp <b>{CONTACT_WA}</b>'
        legal = ('<b>Aviso legal:</b> Este boletim é fornecido apenas para fins informativos gerais e não constitui aconselhamento jurídico. '
                 'A leitura ou a interação com qualquer conteúdo vinculado não estabelece relação advogado-cliente. Consulte um profissional qualificado antes de tomar qualquer decisão.')
        stamp = '&copy; 2026 <b>Joel Stewart, P.A.</b> · Todos os direitos reservados.'
    return (f'<footer class="sitefoot reveal"><div class="social">{social}</div>'
            f'<div class="contact">{contact}</div>'
            f'<div class="legal">{legal}</div>'
            f'<div class="stamp">{stamp}</div></footer>')

def tagclass(t):
    return {"final":"t-final","prop":"t-prop","alert":"t-alert","watch":"t-alert","effect":"t-final"}.get(t,"t-final")

MON_EN = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
MON_PT = ["","jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
def short_label(date, lang):
    try:
        y,m,dd = date.split("-"); m=int(m); dd=int(dd)
        return f'{MON_EN[m]} {dd}' if lang=="en" else f'{dd} {MON_PT[m]}'
    except Exception:
        return date

# ---------- HOME ----------
def render_home(d, lang, index):
    L = d[lang]
    ed_href = f'edicoes/{d["date"]}-{lang}.html'
    lead = L["lead"]
    read_lbl = "Read the full edition" if lang=="en" else "Ler a edição completa"
    arch_lbl = "Archive" if lang=="en" else "Arquivo"
    sub_lbl  = "OFFICIAL SOURCES" if lang=="en" else "FONTES OFICIAIS"
    issue_lbl= (f'ISSUE No. {d["issue"]}' if lang=="en" else f'EDIÇÃO Nº {d["issue"]}')
    upd = ("Updated " if lang=="en" else "Atualizado em ") + L["date_long"]

    hero = (f'<section class="hero reveal"><div class="eyebrow">'
            f'<span class="badge">✓ {sub_lbl}</span>'
            f'<span style="font-weight:700;color:var(--ink);letter-spacing:.04em">{issue_lbl}</span>'
            f'<span>· {e(upd)}</span></div>'
            f'<div class="kicker" style="margin-top:14px">{e(lead["kicker"])}</div>'
            f'<h2>{e(lead["headline"])}</h2>'
            f'<p class="deck">{e(lead["deck"])}</p>'
            f'<div class="herobtns">'
            f'<a class="btn primary" href="{ed_href}">{read_lbl} {ARROW}</a>'
            f'<a class="btn" href="{NAV[lang][1][1]}">{arch_lbl}</a>'
            f'<button class="iconbtn" data-cardshare data-url="" title="Share">{SHARE_SVG}</button>'
            f'</div>'
            f'<div class="src" style="margin-top:12px">{lead["src"]}</div></section>')

    # colunas: cards de seções à esquerda, rail à direita
    main_html = ['<div class="col-main">']
    for sec in L["sections"]:
        main_html.append(f'<div class="secrule reveal"><h3>{e(sec["head"])}</h3></div>')
        main_html.append('<div class="cards">')
        its = sec["items"]; n = len(its)
        for i, it in enumerate(its):
            lonely = (i == n-1 and n % 2 == 1)   # card sozinho na última linha → ocupa a largura
            span = " span" if (it.get("span") or lonely) else ""
            srcline = f'<span class="csrc">{it["src"]}</span>' if it.get("src") else '<span></span>'
            anchor = f'{ed_href}#{slug(it["title"])}'
            read_more = "Read in the edition" if lang=="en" else "Ler na edição"
            main_html.append(
                f'<article class="ncard reveal{span}">'
                f'<a class="cardlink" href="{anchor}" aria-label="{e(it["title"])}"></a>'
                f'<span class="tag {tagclass(it.get("tagtype","final"))}">{e(it.get("tag",""))}</span>'
                f'<h4>{e(it["title"])}</h4>'
                f'<p class="cdeck">{e(it["deck"])}</p>'
                f'<div class="cfoot">{srcline}'
                f'<button class="iconbtn" data-cardshare data-url="{anchor}" data-title="{e(it["title"])}" title="Share" style="width:32px;height:32px">{SHARE_SVG}</button>'
                f'</div></article>')
        main_html.append('</div>')
    # seção de FEATURES (se houver), ao fim da coluna principal
    feats = [f for f in FEATURES if lang in f]
    if feats:
        feat_h = "Feature Series" if lang=="en" else "Matérias de Série"
        main_html.append(f'<div class="secrule reveal"><h3>{feat_h}</h3></div>')
        for f in feats:
            F = f[lang]; href = f'edicoes/feature-{f["slug"]}-{lang}.html'
            cover = f.get("cover")
            img = f'<div class="fcimg" style="background-image:url(\'{e(cover)}\')"></div>' if cover else '<div class="fcimg"></div>'
            more = "Read the full article" if lang=="en" else "Ler a matéria completa"
            main_html.append(
                f'<article class="featcard reveal">'
                f'<a class="cardlink" href="{href}" aria-label="{e(F["title"])}"></a>'
                f'{img}<div class="fcbody">'
                f'<div class="fckick">{e(F.get("kicker",""))}</div>'
                f'<h3>{e(F["title"])}</h3>'
                f'<p class="fcdeck">{e(F.get("deck",""))}</p>'
                f'<span class="fcmore">{more} {ARROW}</span>'
                f'</div></article>')
    main_html.append('</div>')

    # rail
    dl = L.get("deadlines", [])
    dl_html = "".join(f'<li>{x}</li>' for x in dl)
    recent = [r for r in index if r["date"] != d["date"]][:6]
    chips = "".join(f'<a class="chip" href="edicoes/{r["date"]}-{lang}.html">{e(short_label(r["date"],lang))}</a>' for r in recent)
    if not chips:
        chips = ('<span style="font-family:var(--sans);font-size:13px;color:var(--muted)">'
                 + ("Earlier editions will appear here as they publish." if lang=="en"
                    else "As edições anteriores aparecem aqui conforme são publicadas.") + '</span>')
    rail_dl_h = "Deadlines &amp; What to Watch" if lang=="en" else "Prazos &amp; O que Observar"
    rail_rc_h = "Recent Editions" if lang=="en" else "Edições Recentes"
    see_all = "See the full archive" if lang=="en" else "Ver todo o arquivo"
    rail = (f'<aside class="rail">'
            f'<div class="railcard reveal"><h3>{rail_dl_h}</h3><ul>{dl_html}</ul></div>'
            f'<div class="railcard reveal"><h3>{rail_rc_h}</h3><div class="chips">{chips}</div>'
            f'<a class="railmore" href="{NAV[lang][1][1]}">{see_all} {ARROW}</a></div>'
            f'</aside>')

    lang_switch = "index-pt.html" if lang=="en" else "index.html"
    title = "Stewart on Immigration" + ("" if lang=="en" else " — Boletim diário")
    body = (head(title, lead["deck"]) + topbar("Latest" if lang=="en" else "Últimas", lang, lang_switch)
            + '<main><div class="home">' + hero + "".join(main_html) + rail + '</div></main>'
            + footer(lang) + f'<script>{JS}</script></body></html>')
    return body

# ---------- ARQUIVO ----------
def render_archive(d, lang, index):
    rows = []
    for r in index:
        meta = r.get(lang, {})
        rows.append(f'<a class="arcrow reveal" href="edicoes/{r["date"]}-{lang}.html">'
                    f'<span class="n">{("No." if lang=="en" else "Nº")} {r["issue"]}</span>'
                    f'<span class="dt">{e(meta.get("date_long",r["date"]))}</span>'
                    f'<span class="hl">{e(meta.get("headline",""))}</span>'
                    f'<span class="lk">{("Open" if lang=="en" else "Abrir")} →</span></a>')
    h = "Archive" if lang=="en" else "Arquivo"
    sub = "Every edition of the bulletin, newest first." if lang=="en" else "Todas as edições do boletim, da mais recente para a mais antiga."
    lang_switch = "archive-pt.html" if lang=="en" else "archive.html"
    body = (head(f"Archive — Stewart on Immigration") + topbar("Archive" if lang=="en" else "Arquivo", lang, lang_switch)
            + f'<main><div class="panel reveal" style="margin-bottom:18px"><h2>{h}</h2><p class="muted">{sub}</p></div>'
            + '<div class="arclist">' + "".join(rows) + '</div></main>'
            + footer(lang) + f'<script>{JS}</script></body></html>')
    return body

# ---------- SOBRE ----------
def render_about(d, lang):
    lang_switch = "about-pt.html" if lang=="en" else "about.html"
    if lang=="en":
        body_in = ('<h2>About</h2>'
            '<p><b>Stewart on Immigration</b> is a daily U.S. immigration-law bulletin, compiled exclusively from official and primary sources — '
            'the Federal Register, USCIS (including the AAO), the Department of Labor/OFLC/FLAG, the Department of State and the Visa Bulletin, '
            'U.S. and Brazilian consular posts, EOIR/BIA/OALJ, DHS, CISA and the courts — together with AILA.</p>'
            '<p>Each edition explains what a development means in practice, rather than merely citing it. It is commentary on the public record, '
            'written for readers who follow immigration policy closely.</p>'
            '<p class="muted">Edited by <a href="https://www.joelstewartpa.com/" style="color:var(--accent2)">Joel Stewart, P.A.</a> '
            'General information only; not legal advice. Reading this bulletin creates no attorney-client relationship.</p>')
        t="About — Stewart on Immigration"
    else:
        body_in = ('<h2>Sobre</h2>'
            '<p><b>Stewart on Immigration</b> é um boletim diário de direito de imigração dos EUA, compilado exclusivamente de fontes oficiais e primárias — '
            'Federal Register, USCIS (inclusive a AAO), Departamento do Trabalho/OFLC/FLAG, Departamento de Estado e Visa Bulletin, '
            'postos consulares dos EUA e do Brasil, EOIR/BIA/OALJ, DHS, CISA e tribunais — além da AILA.</p>'
            '<p>Cada edição explica o que uma novidade significa na prática, em vez de apenas citá-la. É comentário sobre o registro público, '
            'escrito para quem acompanha de perto a política de imigração.</p>'
            '<p class="muted">Editado por <a href="https://www.joelstewartpa.com/" style="color:var(--accent2)">Joel Stewart, P.A.</a> '
            'Informativo geral; não constitui aconselhamento jurídico. A leitura deste boletim não estabelece relação advogado-cliente.</p>')
        t="Sobre — Stewart on Immigration"
    body = (head(t) + topbar("About" if lang=="en" else "Sobre", lang, lang_switch)
            + f'<main><div class="panel reveal">{body_in}</div></main>'
            + footer(lang) + f'<script>{JS}</script></body></html>')
    return body

# ---------- EDIÇÃO (folha completa) ----------
def render_edition(d, lang):
    L = d[lang]
    lead = L["lead"]
    issue_tag = (f'Issue No. {d["issue"]} · {L["date_short"]}' if lang=="en" else f'Edição Nº {d["issue"]} · {L["date_short"]}')
    sect_names = " &middot; ".join(e(s["head"]) for s in L["sections"])
    parts = [f'<div class="sheet" lang="{lang}">',
             f'<div class="toprule"><span></span><span>{issue_tag}</span></div>',
             f'<div class="masthead"><h1>Stewart on Immigration</h1><div class="sub byline">Joel Stewart, P.A.</div></div>',
             f'<div class="dateline"><span>{e(L["date_long"])}</span><span>{sect_names}</span></div>',
             f'<div class="lead"><div class="kicker">{e(lead["kicker"])}</div><h2>{e(lead["headline"])}</h2>',
             f'<div class="deck">{e(lead["deck"])}</div>']
    for p in lead.get("body", []):
        parts.append(f'<p>{p}</p>')
    parts.append(f'<div class="src">{lead["src"]}</div></div>')
    for sec in L["sections"]:
        parts.append(f'<div class="sechead"><h3>{e(sec["head"])}</h3></div>')
        its = sec["items"]; n = len(its)
        one = " one" if n==1 else ""
        parts.append(f'<div class="grid{one}">')
        for i, it in enumerate(its):
            wide = " wide" if (n>1 and i==n-1 and n%2==1) else ""
            body = "".join(f'<p>{p}</p>' for p in it.get("body", [f'<p>{e(it["deck"])}</p>']))
            if not it.get("body"): body = f'<p>{e(it["deck"])}</p>'
            parts.append(f'<div class="item{wide}" id="{slug(it["title"])}" style="scroll-margin-top:72px"><span class="tag {tagclass(it.get("tagtype","final"))}">{e(it.get("tag",""))}</span>'
                         f'<h4>{e(it["title"])}</h4>{body}'
                         + (f'<div class="src">{it["src"]}</div>' if it.get("src") else '') + '</div>')
        parts.append('</div>')
    # FEATURE SERIES dentro da edição (mesma do site), apontando para a página da matéria
    efeats = [f for f in FEATURES if lang in f]
    if efeats:
        parts.append(f'<div class="sechead"><h3>{"Feature Series" if lang=="en" else "Matérias de Série"}</h3></div>')
        for f in efeats:
            F = f[lang]; href = f'feature-{f["slug"]}-{lang}.html'; cover = f.get("cover")
            img = f'<div class="fcimg" style="background-image:url(\'{e(cover)}\')"></div>' if cover else '<div class="fcimg"></div>'
            more = "Read the full article" if lang=="en" else "Ler a matéria completa"
            parts.append(
                f'<article class="featcard" style="margin-top:4px">'
                f'<a class="cardlink" href="{href}" aria-label="{e(F["title"])}"></a>'
                f'{img}<div class="fcbody"><div class="fckick">{e(F.get("kicker",""))}</div>'
                f'<h3>{e(F["title"])}</h3><p class="fcdeck">{e(F.get("deck",""))}</p>'
                f'<span class="fcmore">{more} {ARROW}</span></div></article>')
    # expediente + disclaimer
    if lang=="en":
        parts.append('<div class="exped"><a href="https://www.joelstewartpa.com/">Joel Stewart, P.A.</a></div>')
        parts.append('<div class="disclaimer">General information only; not legal advice. Reading this bulletin, or interacting with any linked content, creates no attorney-client relationship. Compiled from official and primary sources.</div>')
        home_lbl, arch_lbl, about_lbl = "Latest","Archive","About"
    else:
        parts.append('<div class="exped"><a href="https://www.joelstewartpa.com/">Joel Stewart, P.A.</a></div>')
        parts.append('<div class="disclaimer">Informativo geral; não constitui aconselhamento jurídico. A leitura deste boletim, ou a interação com qualquer conteúdo vinculado, não estabelece relação advogado-cliente. Compilado de fontes oficiais e primárias.</div>')
        home_lbl, arch_lbl, about_lbl = "Últimas","Arquivo","Sobre"
    parts.append('</div>')
    # nav da edição aponta para a raiz do site (um nível acima de edicoes/)
    otherlang = "pt" if lang=="en" else "en"
    lang_switch = (f'{d["date"]}-pt.html' if lang=="en" else f'{d["date"]}-en.html')
    tb = topbar_rel(home_lbl, lang, lang_switch, prefix="../", lang_ok=(otherlang in d))
    title = f'Stewart on Immigration — {e(L["date_long"])}'
    return (head(title, lead["deck"]) + tb + '<main>' + "".join(parts) + '</main>'
            + footer(lang).replace('class="sitefoot reveal"','class="sitefoot"')
            + f'<script>{JS}</script></body></html>')

def topbar_rel(active, lang, lang_switch_href, prefix="", lang_ok=None):
    """topbar com hrefs relativos a uma subpasta (edicoes/)."""
    items = [(lab, prefix+h) for lab,h in NAV[lang]]
    nav = nav_links(items, active)
    other = "pt" if lang=="en" else "en"
    show = (other in AVAIL) if lang_ok is None else lang_ok
    lang_btn = ""
    if show:
        lang_lbl = "PT" if lang=="en" else "EN"
        lang_ttl = "Ler em português" if lang=="en" else "Read in English"
        lang_btn = f'<a class="eicon" href="{lang_switch_href}" title="{lang_ttl}">{lang_lbl}</a>'
    return (
      '<div class="rprog" id="rprog"></div>'
      '<header class="ebar" id="ebar"><div class="ebar-in">'
      f'<a class="ewm" href="{items[0][1]}">Stewart <b>on</b> Immigration</a>'
      f'<nav>{nav}</nav><span class="sp"></span>'
      f'{lang_btn}'
      '<span style="position:relative">'
      f'<button class="eicon" id="shareBtn" title="Share" aria-haspopup="true">{SHARE_SVG}</button>'
      '<div class="shmenu" id="shMenu" style="position:absolute;right:0;top:42px;min-width:168px;background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow2);padding:6px;display:none;flex-direction:column;z-index:70;font-family:var(--sans)">'
      '<button data-sh="copy" style="display:flex;align-items:center;gap:10px;padding:9px 11px;border:0;background:none;color:var(--ink);font-size:13px;font-weight:600;cursor:pointer;border-radius:9px;text-align:left;width:100%">Copy link</button>'
      '<a data-sh="li" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;padding:9px 11px;color:var(--ink);font-size:13px;font-weight:600;border-radius:9px">LinkedIn</a>'
      '<a data-sh="wa" target="_blank" rel="noopener" style="display:flex;align-items:center;gap:10px;padding:9px 11px;color:var(--ink);font-size:13px;font-weight:600;border-radius:9px">WhatsApp</a>'
      '</div></span>'
      '<button class="eicon" id="themeBtn" title="Theme" aria-label="Theme"><svg id="thIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg></button>'
      '</div></header>'
    )

def build_index(data_path):
    """Monta a lista de TODAS as edições (mais nova primeiro) varrendo a pasta de dados.
    Cada entrada: {date, issue, en:{date_long,headline}, pt:{...}}."""
    ddir = os.path.dirname(os.path.abspath(data_path))
    idx = []
    for fn in os.listdir(ddir):
        if not fn.endswith(".json") or fn.startswith("_"): continue
        try:
            j = json.load(open(os.path.join(ddir, fn), encoding="utf-8"))
            if "date" not in j or "issue" not in j: continue
        except Exception:
            continue
        entry = {"date": j["date"], "issue": j["issue"]}
        for lg in ("en","pt"):
            if lg in j:
                entry[lg] = {"date_long": j[lg].get("date_long", j["date"]),
                             "headline": j[lg].get("lead",{}).get("headline","")}
        idx.append(entry)
    idx.sort(key=lambda r: r["date"], reverse=True)
    return idx

# ---------- FEATURE (página própria, estilo matéria) ----------
def render_feature(f, lang):
    F = f[lang]
    lang_switch = f'feature-{f["slug"]}-{"pt" if lang=="en" else "en"}.html'
    has_other = ("pt" if lang=="en" else "en") in f
    # troca o alvo do seletor só se a outra língua existir (senão AVAIL já esconde o botão)
    body = "".join(F.get("body", []))
    back = "All editions" if lang=="en" else "Todas as edições"
    kicker = F.get("kicker","")
    sheet = (f'<div class="sheet" lang="{lang}">'
             f'<div class="toprule"><span></span><span>{"Feature Series" if lang=="en" else "Matéria de Série"}</span></div>'
             f'<div class="masthead"><h1>Stewart on Immigration</h1><div class="sub byline">Joel Stewart, P.A.</div></div>'
             f'<div class="lead"><div class="kicker">{e(kicker)}</div><h2>{e(F["title"])}</h2>'
             f'<div class="deck">{e(F.get("deck",""))}</div></div>'
             f'{body}'
             f'<div class="exped"><a href="https://www.joelstewartpa.com/">Joel Stewart, P.A.</a></div>'
             + ('<div class="disclaimer">General information only; not legal advice. Reading this article creates no attorney-client relationship.</div>' if lang=="en"
                else '<div class="disclaimer">Informativo geral; não constitui aconselhamento jurídico. A leitura deste artigo não estabelece relação advogado-cliente.</div>')
             + '</div>')
    home_lbl = "Latest" if lang=="en" else "Últimas"
    tb = topbar_rel(home_lbl, lang, lang_switch, prefix="../", lang_ok=has_other)
    title = f'{F["title"]} — Stewart on Immigration'
    return (head(title, F.get("deck","")) + tb + '<main>' + sheet + '</main>'
            + footer(lang).replace('class="sitefoot reveal"','class="sitefoot"')
            + f'<script>{JS}</script></body></html>')

def main():
    data_path = sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,"dados","2026-11-17.json")
    outdir = sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,"out")
    d = json.load(open(data_path, encoding="utf-8"))
    index = build_index(data_path)
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir,"edicoes"), exist_ok=True)
    langs = [l for l in ("en","pt") if l in d]
    global AVAIL, FEATURES; AVAIL = set(langs)
    # features curadas (opcional): <dados>/_features.json {"features":[...]}
    featpath = os.path.join(os.path.dirname(os.path.abspath(data_path)), "_features.json")
    if os.path.exists(featpath):
        try: FEATURES = json.load(open(featpath, encoding="utf-8")).get("features", [])
        except Exception: FEATURES = []
    # páginas de feature (uma por slug+idioma existente)
    for f in FEATURES:
        for lg in ("en","pt"):
            if lg in f:
                open(os.path.join(outdir,"edicoes",f'feature-{f["slug"]}-{lg}.html'),"w",encoding="utf-8").write(render_feature(f,lg))
    for lang in langs:
        home = "index.html" if lang=="en" else "index-pt.html"
        open(os.path.join(outdir,home),"w",encoding="utf-8").write(render_home(d,lang,index))
        arc = "archive.html" if lang=="en" else "archive-pt.html"
        open(os.path.join(outdir,arc),"w",encoding="utf-8").write(render_archive(d,lang,index))
        ab = "about.html" if lang=="en" else "about-pt.html"
        open(os.path.join(outdir,ab),"w",encoding="utf-8").write(render_about(d,lang))
        edp = os.path.join(outdir,"edicoes",f'{d["date"]}-{lang}.html')
        open(edp,"w",encoding="utf-8").write(render_edition(d,lang))
    # páginas de TODAS as outras edições do índice (arquivo navegável), numa só rodada
    ddir = os.path.dirname(os.path.abspath(data_path))
    for fn in os.listdir(ddir):
        if not fn.endswith(".json") or fn.startswith("_"): continue
        if fn == os.path.basename(data_path): continue
        try:
            jd = json.load(open(os.path.join(ddir, fn), encoding="utf-8"))
            if "date" not in jd: continue
        except Exception:
            continue
        for lg in ("en","pt"):
            if lg in jd:
                open(os.path.join(outdir,"edicoes",f'{jd["date"]}-{lg}.html'),"w",encoding="utf-8").write(render_edition(jd,lg))
    print("gerado:", ", ".join(langs), f"({len(index)} edições no índice) ->", outdir)

if __name__=="__main__":
    main()
