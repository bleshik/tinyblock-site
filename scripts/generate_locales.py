#!/usr/bin/env python3
"""Generate localized static landing pages and SEO discovery files."""

from __future__ import annotations

import datetime as dt
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from string import Template

from wiki_i18n import TEXT as WIKI_TEXT
from multiplayer_seo_locales import EXTRA_PAGES as EXTRA_LOCAL_MULTIPLAYER_SEO_PAGES
from multiplayer_seo_locales import PAGES as LOCAL_MULTIPLAYER_SEO_PAGES


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://tinyblock.nosuchgames.com"
APP_STORE_URL = "https://apps.apple.com/app/id6793160455"
GOOGLE_PLAY_URL = "https://play.google.com/store/apps/details?id=com.nosuchgames.tinyblock"
STATIC_ROUTES = [
    ("games-to-play-with-friends-on-phone/", "weekly", "0.8"),
    ("one-block-skyblock-multiplayer/", "weekly", "0.8"),
    ("play-minecraft-with-friends-free-alternative/", "weekly", "0.8"),
    ("multiplayer-games-with-voice-chat/", "weekly", "0.8"),
    ("minecraft-proximity-chat-alternative/", "weekly", "0.8"),
    ("multiplayer-survival-game/", "weekly", "0.8"),
    ("wiki/", "weekly", "0.8"),
    ("wiki/biomes/", "monthly", "0.7"),
    ("wiki/materials/", "monthly", "0.7"),
    ("wiki/creatures/", "monthly", "0.7"),
    ("wiki/plants/", "monthly", "0.7"),
    ("wiki/recipes/", "monthly", "0.7"),
    ("guides/how-to-grow-your-one-block-island/", "monthly", "0.7"),
    ("creators/", "monthly", "0.4"),
    ("privacy/", "yearly", "0.2"),
]
WIKI_ROUTES = ["wiki/", "wiki/biomes/", "wiki/materials/", "wiki/creatures/", "wiki/plants/", "wiki/recipes/"]
SEO_DATA = json.loads((ROOT / "content" / "seo-keywords.json").read_text(encoding="utf-8"))
MULTIPLAYER_HOME = json.loads((ROOT / "content" / "multiplayer-home.json").read_text(encoding="utf-8"))
FREE_LABELS = {
    "en": "FREE",
    "de": "KOSTENLOS",
    "es": "GRATIS",
    "fr": "GRATUIT",
    "it": "GRATIS",
    "pt-br": "GRÁTIS",
    "ar": "مجانًا",
    "ja": "無料",
    "ko": "무료",
    "ru": "БЕСПЛАТНО",
    "zh-hans": "免费",
    "zh-hant": "免費",
}


def previous_sitemap_dates() -> dict[str, str]:
    sitemap_path = ROOT / "sitemap.xml"
    if not sitemap_path.exists():
        return {}
    try:
        document = ET.parse(sitemap_path)
    except ET.ParseError:
        return {}
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    result = {}
    for entry in document.findall("s:url", namespace):
        location = entry.findtext("s:loc", default="", namespaces=namespace)
        lastmod = entry.findtext("s:lastmod", default="", namespaces=namespace)
        if location and lastmod:
            result[location] = lastmod
    return result


def sitemap_entry(url: str, previous_dates: dict[str, str], today: str, changefreq: str, priority: str, force_today: bool = False) -> str:
    lastmod = today if force_today else previous_dates.get(url, today)
    return f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"


def route_url(locale: dict) -> str:
    return f"{BASE_URL}/" if not locale["output"] else f"{BASE_URL}/{locale['output']}/"


def render() -> None:
    content = json.loads((ROOT / "content" / "locales.json").read_text(encoding="utf-8"))
    locales = content["locales"]
    template = Template((ROOT / "templates" / "landing.html").read_text(encoding="utf-8"))

    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{html.escape(locale["hreflang"])}" href="{route_url(locale)}">'
        for locale in locales
    )
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/">'

    for locale in locales:
        canonical = route_url(locale)
        language_links = "\n".join(
            f'        <a href="{("/" if not item["output"] else "/" + item["output"] + "/")}" lang="{html.escape(item["html_lang"])}"'
            f'{" aria-current=\"page\"" if item["code"] == locale["code"] else ""}>{html.escape(item["label"])}</a>'
            for item in locales
        )
        og_alternates = "\n".join(
            f'  <meta property="og:locale:alternate" content="{html.escape(item["og_locale"])}">'
            for item in locales
            if item["code"] != locale["code"]
        )
        feature_cards = "\n".join(
            f'      <article class="feature-card"><span class="feature-number">{index:02d}</span><h2>{html.escape(feature["title"])}</h2><p>{html.escape(feature["copy"])}</p></article>'
            for index, feature in enumerate(locale["features"], 1)
        )
        faq_items = "\n".join(
            f'        <article class="faq-item"><h3>{html.escape(item["question"])}</h3><p>{html.escape(item["answer"])}</p></article>'
            for item in locale["faq"]
        )
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": ["VideoGame", "MobileApplication"],
                    "@id": f"{BASE_URL}/#game",
                    "name": "Tiny Block",
                    "alternateName": locale["h1"],
                    "url": canonical,
                    "image": f"{BASE_URL}/og-seo.png",
                    "description": locale["meta_description"],
                    "inLanguage": locale["html_lang"],
                    "applicationCategory": "GameApplication",
                    "operatingSystem": ["iOS", "Android"],
                    "genre": ["Sandbox", "Survival", "Crafting", "Skyblock"],
                    "playMode": ["SinglePlayer", "MultiPlayer", "CoOp"],
                    "featureList": [
                        MULTIPLAYER_HOME[locale["code"]]["public"],
                        MULTIPLAYER_HOME[locale["code"]]["private"],
                        MULTIPLAYER_HOME[locale["code"]]["voice"],
                    ],
                    "author": {"@type": "Organization", "name": "No Such Games", "url": "https://nosuchgames.com"},
                    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                    "sameAs": [APP_STORE_URL, GOOGLE_PLAY_URL],
                },
                {
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": item["question"],
                            "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
                        }
                        for item in locale["faq"]
                    ],
                },
            ],
        }
        values = {key: html.escape(str(value), quote=True) for key, value in locale.items() if not isinstance(value, (list, dict))}
        values.update(
            {
                "canonical_url": canonical,
                "alternate_links": alternates,
                "og_alternates": og_alternates,
                "language_links": language_links,
                "feature_cards": feature_cards,
                "faq_items": faq_items,
                "structured_data": json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
                "home_path": "/" if not locale["output"] else f"/{locale['output']}/",
                "current_language": html.escape(locale["label"]),
                "wiki_path": "/wiki/" if not locale["output"] else f"/{locale['output']}/wiki/",
                "wiki_label": html.escape(WIKI_TEXT[locale["code"]]["wiki"]),
                "multiplayer_kicker": html.escape(MULTIPLAYER_HOME[locale["code"]]["kicker"]),
                "multiplayer_title": html.escape(MULTIPLAYER_HOME[locale["code"]]["title"]),
                "multiplayer_copy": html.escape(MULTIPLAYER_HOME[locale["code"]]["copy"]),
                "multiplayer_public": html.escape(MULTIPLAYER_HOME[locale["code"]]["public"]),
                "multiplayer_private": html.escape(MULTIPLAYER_HOME[locale["code"]]["private"]),
                "multiplayer_voice": html.escape(MULTIPLAYER_HOME[locale["code"]]["voice"]),
                "free_label": html.escape(FREE_LABELS[locale["code"]]),
            }
        )
        rendered = template.safe_substitute(values)
        target = ROOT / "index.html" if not locale["output"] else ROOT / locale["output"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")

    lastmod = dt.date.today().isoformat()
    previous_dates = previous_sitemap_dates()
    force_today = {
        *(route_url(locale) for locale in locales),
        *(f"{BASE_URL}/{locale['output'] + '/' if locale['output'] else ''}wiki/" for locale in locales),
        *(f"{BASE_URL}/{route}" for route, _changefreq, _priority in STATIC_ROUTES[:6]),
    }
    urls = "\n".join(
        sitemap_entry(route_url(locale), previous_dates, lastmod, "weekly", "1.0" if not locale["output"] else "0.8", route_url(locale) in force_today)
        for locale in locales
    )
    urls += "\n" + "\n".join(
        sitemap_entry(f"{BASE_URL}/{route}", previous_dates, lastmod, changefreq, priority, f"{BASE_URL}/{route}" in force_today)
        for route, changefreq, priority in STATIC_ROUTES
    )
    urls += "\n" + "\n".join(
        sitemap_entry(f"{BASE_URL}/{locale['output']}/{route}", previous_dates, lastmod, "weekly" if route == "wiki/" else "monthly", "0.8" if route == "wiki/" else "0.7")
        for locale in locales if locale["output"]
        for route in WIKI_ROUTES
    )
    urls += "\n" + "\n".join(
        sitemap_entry(f"{BASE_URL}/{locale['output'] + '/' if locale['output'] else ''}{page['locales'][locale['code']]['slug']}/", previous_dates, lastmod, "monthly", "0.7" if locale["code"] == "en" else "0.6")
        for locale in locales
        for page in SEO_DATA["pages"].values()
    )
    urls += "\n" + "\n".join(
        sitemap_entry(
            f"{BASE_URL}/{locale['output']}/{LOCAL_MULTIPLAYER_SEO_PAGES[locale['code']]['slug']}/",
            previous_dates,
            lastmod,
            "weekly",
            "0.8",
            True,
        )
        for locale in locales if locale["code"] != "en"
    )
    urls += "\n" + "\n".join(
        sitemap_entry(
            f"{BASE_URL}/{locale['output']}/{page['slug']}/",
            previous_dates,
            lastmod,
            "weekly",
            "0.8",
            True,
        )
        for locale in locales if locale["code"] != "en"
        for page in EXTRA_LOCAL_MULTIPLAYER_SEO_PAGES.get(locale["code"], [])
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    render()
