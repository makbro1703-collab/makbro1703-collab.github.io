#!/usr/bin/env python3
"""Собирает сайт-портфолио: content/works.json -> docs/ (готовые HTML-страницы).

Запуск: python3 build.py
Тексты и список работ лежат в content/works.json, оформление в docs/css/site.css.
"""
import json
import shutil
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;600'
    '&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
)
PLAY = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12-7.5z"/></svg>'
BACK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/></svg>'
NEXT = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>'


def page(title, body, base, description):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{FONTS}
<link rel="stylesheet" href="{base}css/site.css">
</head>
<body>
{body}
</body>
</html>
"""


def header(site, base, nav_html):
    return f"""<header class="wrap top">
  <a class="brand" href="{base}index.html"><span class="brand-name">{e(site['brand'])}</span><span class="mono dim">{e(site['label'])}</span></a>
  {nav_html}
</header>"""


def footer(site, sections, base):
    links = "".join(f'<a href="{base}index.html#{s["id"]}">{e(s["nav"])}</a>' for s in sections)
    contacts = "".join(f'<a href="{e(c["href"])}">{e(c["label"])}</a>' for c in site["contacts"])
    return f"""<footer class="foot" id="contact">
  <div class="wrap foot-in">
    <div class="foot-cols">
      <div class="foot-about"><span class="brand-name">{e(site['brand'])}</span><span>{e(site['footer'])}</span></div>
      <div class="foot-links">
        <div><span class="mono">РАБОТЫ</span>{links}</div>
        <div><span class="mono">СВЯЗЬ</span>{contacts}</div>
      </div>
    </div>
    <div class="foot-copy">© 2026 {e(site['name'])}</div>
  </div>
</footer>"""


def media(src, placeholder, cls):
    if src:
        return f'<img class="{cls}" src="{e(src)}" alt="" loading="lazy">'
    return f'<div class="{cls} ph"><span>{e(placeholder)}</span></div>'


def card(w, base):
    thumb = w.get("poster", "")
    dur = f'<span>{e(w["dur"])}</span>' if w.get("dur") else ""
    if thumb:
        pic = f'<div class="thumb"><img src="{base}{e(thumb)}" alt="" loading="lazy"><span class="thumb-dur mono">{e(w.get("dur", ""))}</span></div>'
    else:
        pic = f'<div class="thumb ph mono"><span>[КАДР]</span>{dur}</div>'
    return f"""<a class="card" href="{base}work/{e(w['slug'])}.html">
  {pic}
  <span class="card-title">{e(w['title'])}</span>
  <span class="card-tag">{e(w['tag'])}</span>
</a>"""


def build_index(data):
    site, sections, works = data["site"], data["sections"], data["works"]
    nav = '<nav class="nav" aria-label="Основное меню">' + "".join(
        f'<a href="#{s["id"]}">{e(s["nav"])}</a>' for s in sections
    ) + '<a class="pill" href="#about">Обо мне</a></nav>'
    feat = next(w for w in works if w["slug"] == site["featured"])
    feat_meta = "<span>·</span>".join(f"<span>{e(m)}</span>" for m in feat["meta"][:4])
    feat_pic = (
        f'<img src="{e(feat["poster"])}" alt="">' if feat.get("poster") else '<span class="mono">[КАДР ИЛИ ЛУП ИЗ РОЛИКА]</span>'
    )
    blocks = []
    for s in sections:
        items = [w for w in works if w["section"] == s["id"]]
        if not items:
            continue
        cards = "\n".join(card(w, "") for w in items)
        blocks.append(f"""<section id="{s['id']}" class="sec sec-{s['tone']}">
  <div class="wrap sec-in">
    <div class="sec-head"><h2>{e(s['title'])}</h2><span>{e(s['text'])}</span></div>
    <div class="grid">
{cards}
    </div>
  </div>
</section>""")
    body = f"""{header(site, '', nav)}
<main>
<section class="wrap intro">
  <span class="mono dim">{e(site['name'].upper())} · {e(site['role'])}</span>
  <h1>{e(site['headline'])}</h1>
  <p>{e(site['intro'])}</p>
</section>
<section class="wrap feat-wrap">
  <div class="feat">
    <div class="feat-text">
      <div class="badges mono"><span class="badge badge-red">ГЛАВНЫЙ КЕЙС</span><span class="badge">+ РАЗБОР</span></div>
      <div class="feat-mid">
        <h2 class="feat-title">{e(feat['title'].upper())}</h2>
        <p>{e(feat['lead'])}</p>
        <div class="meta">{feat_meta}</div>
      </div>
      <div class="feat-btns">
        <a class="btn btn-light" href="work/{e(feat['slug'])}.html">{PLAY}Смотреть</a>
        <a class="btn btn-ghost" href="work/{e(feat['slug'])}.html#process">Как это сделано</a>
      </div>
    </div>
    <div class="feat-pic">{feat_pic}</div>
  </div>
</section>
{chr(10).join(blocks)}
<section id="about" class="sec sec-band">
  <div class="wrap about">
    <div class="about-photo ph mono"><span>[ФОТО]</span></div>
    <div class="about-text"><span class="mono dim">ОБО МНЕ</span><span class="about-name">{e(site['name'])}</span><p>{e(site['about'])}</p></div>
    <a class="pill" href="#contact">Связаться</a>
  </div>
</section>
</main>
{footer(site, sections, '')}"""
    return page(f"{site['brand']} — портфолио", body, "", site["intro"])


def build_work(data, i):
    site, sections, works = data["site"], data["sections"], data["works"]
    w = works[i]
    nxt = works[(i + 1) % len(works)]
    nav = f'<a class="back" href="../index.html#{e(w["section"])}">{BACK}Все работы</a>'
    badges = f'<span class="badge badge-red">{e(w["badge"])}</span>'
    if w.get("badge2"):
        badges += f'<span class="badge">{e(w["badge2"])}</span>'
    meta = "<span>·</span>".join(f"<span>{e(m)}</span>" for m in w.get("meta", []))
    if w.get("video"):
        poster = f' poster="{e(w["poster"])}"' if w.get("poster") else ""
        player = f'<video class="player" controls playsinline preload="metadata"{poster} src="{e(w["video"])}"></video>'
    else:
        player = '<div class="player player-ph"><span class="play-dot">' + PLAY + '</span><span class="mono">[ФИНАЛЬНЫЙ РОЛИК]</span></div>'
    tools = "".join(f"<li>{e(t)}</li>" for t in w.get("tools", [])) or "<li>[ИНСТРУМЕНТЫ]</li>"
    idea = w.get("idea", "[ЧТО В РОЛИКЕ ТВОЁ КАК ИДЕЯ]")
    did = w.get("did", "[КАКИЕ ЭТАПЫ ТВОИ]")
    process = ""
    if w.get("steps"):
        steps = "".join(
            f"""<li>{media(s.get('image', ''), s.get('placeholder', '[КАДР]'), 'step-pic')}
<span class="mono red">{e(s['label'])}</span><span class="step-title">{e(s['title'])}</span><span class="step-text">{e(s['text'])}</span></li>"""
            for s in w["steps"]
        )
        process = f"""<section id="process" class="sec sec-band">
  <div class="wrap sec-in">
    <div class="sec-head"><h2>Как это сделано</h2><span>{e(w.get('process_intro', ''))}</span></div>
    <ol class="steps">{steps}</ol>
  </div>
</section>"""
    note = ""
    if w.get("note"):
        note = f"""<section class="wrap note"><h2>{e(w['note_title'])}</h2><p>{e(w['note'])}</p></section>"""
    body = f"""{header(site, '../', nav)}
<main>
<section class="wrap hero-wrap">
  <div class="hero">
    <div class="hero-text">
      <div class="badges mono">{badges}</div>
      <h1 class="hero-title">{e(w['title'].upper())}</h1>
      <p>{e(w['lead'])}</p>
      <div class="meta">{meta}</div>
    </div>
    {player}
  </div>
</section>
<section class="wrap trio">
  <div class="tile"><span class="mono red">ИДЕЯ</span><h2>Что я придумал</h2><p>{e(idea)}</p></div>
  <div class="tile"><span class="mono red">РАБОТА</span><h2>Что я делал</h2><p>{e(did)}</p></div>
  <div class="tile"><span class="mono red">ИНСТРУМЕНТЫ</span><h2>Что использовал</h2><ul class="chips">{tools}</ul></div>
</section>
{process}
{note}
<section class="next">
  <div class="wrap next-in"><span class="mono dim">СЛЕДУЮЩАЯ РАБОТА</span><a href="{e(nxt['slug'])}.html">{e(nxt['title'])}{NEXT}</a></div>
</section>
</main>
{footer(site, sections, '../')}"""
    return page(f"{w['title']} — {site['brand']}", body, "../", w["lead"])


def main():
    data = json.loads((ROOT / "content" / "works.json").read_text(encoding="utf-8"))
    (OUT / "work").mkdir(parents=True, exist_ok=True)
    for old in (OUT / "work").glob("*.html"):
        old.unlink()
    (OUT / "index.html").write_text(build_index(data), encoding="utf-8")
    for i, w in enumerate(data["works"]):
        (OUT / "work" / f"{w['slug']}.html").write_text(build_work(data, i), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "CNAME").write_text("k-haz.com\n", encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    shutil.copy(OUT / "index.html", OUT / "404.html")
    print(f"Готово: 1 главная + {len(data['works'])} страниц работ в {OUT}")


if __name__ == "__main__":
    main()
