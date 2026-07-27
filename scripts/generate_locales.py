#!/usr/bin/env python3
"""Generate localized static landing pages and SEO discovery files."""

from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path
from string import Template

from wiki_i18n import TEXT as WIKI_TEXT


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://tinyblock.nosuchgames.com"
APP_STORE_URL = "https://apps.apple.com/app/id6793160455"
GOOGLE_PLAY_URL = "https://play.google.com/store/apps/details?id=com.nosuchgames.tinyblock"
STATIC_ROUTES = [
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
MINECRAFT_SEO_ROUTES = [
    "minecraft-one-block/",
    "minecraft-biomes-list/",
    "minecraft-mobs-list-with-pictures/",
    "minecraft-crafting-recipes/",
]


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
            }
        )
        rendered = template.safe_substitute(values)
        target = ROOT / "index.html" if not locale["output"] else ROOT / locale["output"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")

    lastmod = dt.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{route_url(locale)}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>{'1.0' if not locale['output'] else '0.8'}</priority></url>"
        for locale in locales
    )
    urls += "\n" + "\n".join(
        f"  <url><loc>{BASE_URL}/{route}</loc><lastmod>{lastmod}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
        for route, changefreq, priority in STATIC_ROUTES
    )
    urls += "\n" + "\n".join(
        f"  <url><loc>{BASE_URL}/{locale['output']}/{route}</loc><lastmod>{lastmod}</lastmod><changefreq>{'weekly' if route == 'wiki/' else 'monthly'}</changefreq><priority>{'0.8' if route == 'wiki/' else '0.7'}</priority></url>"
        for locale in locales if locale["output"]
        for route in WIKI_ROUTES
    )
    urls += "\n" + "\n".join(
        f"  <url><loc>{BASE_URL}/{route}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>"
        for route in MINECRAFT_SEO_ROUTES
    )
    urls += "\n" + "\n".join(
        f"  <url><loc>{BASE_URL}/{locale['output']}/{route}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>"
        for locale in locales if locale["output"]
        for route in MINECRAFT_SEO_ROUTES
    )
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    render()
