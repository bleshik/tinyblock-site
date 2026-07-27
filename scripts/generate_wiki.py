#!/usr/bin/env python3
"""Generate localized Tiny Block wiki pages from the shipped game catalog."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from minecraft_compare_i18n import COMPARE
from wiki_i18n import BIOME_VARIETY, TERMS, TEXT


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://tinyblock.nosuchgames.com"
LOCALE_COLUMNS = {"en":"en","de":"de","es":"es","fr":"fr","it":"it","pt-br":"pt_BR","ar":"ar","ja":"ja","ko":"ko","ru":"ru","zh-hans":"zh_Hans","zh-hant":"zh_Hant"}

BIOMES = [
    ("Plains", "Open grassland with occasional trees.", "Grass, dirt, stone", "Meadow Bloom, Prairie Sprig, Oak, Weeping Tree", "Meadow Hopper, Forest Fox, Sky Mote", "plains.webp", "plains"),
    ("Forest", "A damp woodland rich in trees and small creatures.", "Grass, dirt, stone, wood", "Prairie Sprig, Meadow Bloom, Oak, Weeping Tree", "Forest Fox, Moss Crawler, Moss Slug", "forest.webp", "forest"),
    ("Tundra", "A cold open land where water slowly freezes.", "Dirt, stone, ice", "Pine", "Snow Penguin, Sky Mote, Gloomwing", "tundra.webp", "tundra"),
    ("Ice Fields", "A barren glacier of deep ice, frozen water, and exposed stone.", "Ice, stone, water", "—", "Snow Penguin, Sky Mote, Gloomwing", "ice-fields.webp", "ice-fields"),
    ("Desert", "Dry dunes over deep stone.", "Sand, stone", "—", "Sky Mote, Dusk Prowler", "desert.webp", "desert"),
    ("Obsidian Wastes", "Weathered volcanic ground hiding obsidian, ancient formations, and lava pools.", "Cobblestone, stone, obsidian, lava", "—", "Ember Walker, Cinder Eel, Gloomwing", "obsidian.webp", "obsidian"),
    ("Beach", "A warm sandy edge beside open water.", "Sand, stone, water", "Palm", "Pool Drifter, Sand Crab, Sky Mote", "beach.webp", "beach"),
    ("Riverbank", "Low sandy ground shaped by flowing water.", "Sand, stone, water", "—", "Pool Drifter, Sand Crab, Moss Slug", "riverbank.webp", "riverbank"),
    ("Cavern", "A dark underground habitat.", "Stone", "Cave Vines", "Cave Spider, Cave Skitter, Moss Crawler", "cavern.webp", "cavern"),
    ("Volcanic", "Hot rock pockets inhabited by ember creatures.", "Stone, obsidian, lava", "—", "Ember Walker, Cinder Eel", "volcanic.webp", "volcanic"),
]

MATERIALS = [
    ("Grass", "A living surface block used to expand fertile ground.", "grass"), ("Dirt", "A basic building and planting block found beneath grass.", "dirt"),
    ("Stone", "A durable underground block and a core crafting ingredient.", "stone"), ("Wood", "A flammable tree material that can be cut into planks.", "wood"),
    ("Water", "A flowing liquid that combines with lava to create new materials.", "water"), ("Lava", "A hot, slow-moving liquid used in several transformation recipes.", "lava"),
    ("Gravel", "A loose block that falls when unsupported and can become sand.", "gravel"), ("Sand", "A falling block used for glass and sandstone.", "sand"),
    ("Glass", "A translucent building block crafted from sand and lava.", "glass"), ("Charcoal", "A combustible material produced by combining wood and lava.", "charcoal"),
    ("Ice", "A cold, slippery block found in tundra and ice biomes.", "ice"), ("Packed Ice", "Dense polished ice that stays cold and is especially slippery.", "packed-ice"),
    ("Obsidian", "Very hard volcanic glass formed from stone, water, and lava.", "obsidian"), ("Lantern", "A charcoal lamp enclosed in glass that lights nearby blocks.", "lantern"),
]

PLANTS = [
    ("Meadow Bloom", "A bright wildflower that dots sunny plains with color.", "meadow-bloom"), ("Prairie Sprig", "A small branching plant that grows between open grassland paths.", "prairie-sprig"),
    ("Cave Vines", "Leafy strands that hang from cool stone ceilings in dark caverns.", "cave-vines"), ("Potted Fern", "A hardy fern kept in a warm clay pot for shelters and ruins.", "potted-fern"),
    ("Oak", "A sturdy broad-crowned tree common to plains and forests.", "oak"), ("Palm", "A tall bare-trunked tree crowned with wide tropical fronds.", "palm"),
    ("Pine", "A cold-tolerant evergreen with a narrow layered crown.", "pine"), ("Weeping Tree", "A moisture-loving tree whose foliage hangs toward the ground.", "weeping-tree"),
]

CREATURES = [
    ("Meadow Hopper", "A gentle long-eared meadow creature that bounds away after being hurt.", "Plains, Forest", "meadow-hopper"), ("Forest Fox", "A quick orange wanderer that avoids danger and follows berry-like plants.", "Plains, Forest", "forest-fox"),
    ("Sky Mote", "A shy flying creature that drifts through bright open air.", "Open biomes", "sky-mote"), ("Moss Crawler", "A dark-loving crawler drawn to moss that fights back when attacked.", "Forest, Cavern", "moss-crawler"),
    ("Moss Slug", "A slow harmless slug found in damp shade near mossy plants.", "Forest, Riverbank", "moss-slug"), ("Pool Drifter", "A timid blue fish that swims through water and flees from danger.", "Beach, Riverbank", "pool-drifter"),
    ("Sand Crab", "A small beach crab that scuttles over sand and defends itself.", "Beach, Riverbank", "sand-crab"), ("Snow Penguin", "A friendly cold-weather waddler that stays near ice and water.", "Tundra, Ice Fields", "snow-penguin"),
    ("Ember Walker", "A heatproof creature that walks along lava bottoms.", "Obsidian Wastes, Volcanic", "ember-walker"), ("Cave Skitter", "A red-eyed cave crawler that prefers deep darkness.", "Cavern", "cave-skitter"),
    ("Cave Spider", "A shy eight-legged hunter that hides among cave vines.", "Forest caves, Cavern", "cave-spider"), ("Watcher Bloom", "A rooted flower-creature that watches sunny clearings.", "Plains, Forest", "watcher-bloom"),
    ("Dusk Prowler", "A solitary night hunter that stalks open ground.", "Plains, Desert", "dusk-prowler"), ("Gloomwing", "A rare dark-loving flier that hunts after sunset.", "Forest, Tundra, Cavern", "gloomwing"),
    ("Cinder Eel", "A fierce lava swimmer that emerges at night.", "Obsidian Wastes, Volcanic", "cinder-eel"),
]

RECIPES = [
    (("Water",1,"water"),("Lava",1,"lava"),("Cobblestone",1,"cobblestone")), (("Cobblestone",4,"cobblestone"),("Stone",1,"stone")), (("Leaves",4,"leaves"),("Wood",1,"wood")),
    (("Stone",1,"stone"),("Gravel",1,"gravel")), (("Gravel",1,"gravel"),("Sand",1,"sand")), (("Sand",1,"sand"),("Lava",1,"lava"),("Glass",1,"glass")),
    (("Wood",1,"wood"),("Lava",1,"lava"),("Charcoal",1,"charcoal")), (("Wood",1,"wood"),("Planks",4,"planks")), (("Stone",1,"stone"),("Water",1,"water"),("Lava",1,"lava"),("Obsidian",1,"obsidian")),
    (("Planks",2,"planks"),("Stone",1,"stone"),("Stone Pickaxe",1,"stone-pickaxe")), (("Planks",4,"planks"),("Chest",1,"chest")), (("Ice",4,"ice"),("Packed Ice",1,"packed-ice")),
    (("Charcoal",1,"charcoal"),("Glass",1,"glass"),("Stone",1,"stone"),("Lantern",1,"lantern")), (("Stone",2,"stone"),("Stone Bricks",2,"stone-bricks")), (("Sand",2,"sand"),("Stone",1,"stone"),("Sandstone",3,"sandstone")),
]

MINECRAFT_SEO_PAGES = [
    ("minecraft-one-block", "Minecraft One Block", "one-block"),
    ("minecraft-biomes-list", "Minecraft Biomes List", "biomes"),
    ("minecraft-mobs-list-with-pictures", "Minecraft Mobs List with Pictures", "mobs"),
    ("minecraft-crafting-recipes", "Minecraft Crafting Recipes", "recipes"),
]

MINECRAFT_DISCLAIMER = "NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT."

MINECRAFT_BIOME_PAIRS = [
    ("Plains", "plains.jpg", "plains", "plains.webp", "https://www.minecraft.net/en-us/article/around-block--plains"),
    ("Dark Forest", "forest.jpg", "forest", "forest.webp", "https://www.minecraft.net/en-us/article/around-block--dark-forest"),
    ("Snowy Taiga", "snow.jpg", "tundra", "tundra.webp", "https://www.minecraft.net/en-us/article/snowy-taiga"),
    ("Desert", "desert.jpg", "desert", "desert.webp", "https://www.minecraft.net/en-us/article/desert"),
    ("Dripstone Caves", "caves.jpg", "cavern", "cavern.webp", "https://www.minecraft.net/en-us/article/around-block--dripstone-caves"),
    ("Nether Wastes", "nether.jpg", "volcanic", "volcanic.webp", "https://www.minecraft.net/en-us/article/around-block--nether-wastes"),
]

MINECRAFT_SEO_COMMON = {
    "en": ("Search guides and comparisons", "Independent comparison", "Tiny Block is an independent game"),
    "de": ("Suchguides und Vergleiche", "Unabhängiger Vergleich", "Tiny Block ist ein eigenständiges Spiel"),
    "es": ("Guías de búsqueda y comparaciones", "Comparación independiente", "Tiny Block es un juego independiente"),
    "fr": ("Guides de recherche et comparaisons", "Comparaison indépendante", "Tiny Block est un jeu indépendant"),
    "it": ("Guide di ricerca e confronti", "Confronto indipendente", "Tiny Block è un gioco indipendente"),
    "pt-br": ("Guias de pesquisa e comparações", "Comparação independente", "Tiny Block é um jogo independente"),
    "ar": ("أدلة البحث والمقارنات", "مقارنة مستقلة", "Tiny Block لعبة مستقلة"),
    "ja": ("検索ガイドと比較", "独立した比較", "Tiny Blockは独立したゲームです"),
    "ko": ("검색 가이드와 비교", "독립적인 비교", "Tiny Block은 독립적인 게임입니다"),
    "ru": ("Поисковые гиды и сравнения", "Независимое сравнение", "Tiny Block — самостоятельная игра"),
    "zh-hans": ("搜索指南与比较", "独立比较", "Tiny Block是一款独立游戏"),
    "zh-hant": ("搜尋指南與比較", "獨立比較", "Tiny Block是一款獨立遊戲"),
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load_catalog() -> tuple[list[dict], dict[str, dict[str, str]]]:
    locales = json.loads((ROOT / "content/locales.json").read_text(encoding="utf-8"))["locales"]
    with (ROOT / "content/game-ui.csv").open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    catalog = {row["keys"]: {code: row.get(column, "") for code, column in LOCALE_COLUMNS.items()} for row in rows}
    return locales, catalog


def entity(catalog: dict, locale: str, slug: str, original: str, description: bool = False, kind: str = "BLOCK") -> str:
    suffix = slug.upper().replace("-", "_")
    key = f"ENTITY_DESCRIPTION_{suffix}" if description else f"ENTITY_{suffix}"
    if key in catalog and catalog[key].get(locale):
        return catalog[key][locale]
    if not description and slug in TERMS[locale]:
        return TERMS[locale][slug]
    generic = f"ENTITY_DESCRIPTION_{kind}" if description else ""
    return catalog.get(generic, {}).get(locale) or original


def localize_list(value: str, locale: str, catalog: dict) -> str:
    if value == "—":
        return value
    result = []
    for original in value.split(", "):
        slug = original.lower().replace(" ", "-")
        result.append(entity(catalog, locale, slug, original))
    return ", ".join(result)


def locale_route(locale: dict, tail: str) -> str:
    return tail if not locale["output"] else f'{locale["output"]}/{tail}'


def page(title: str, description: str, tail: str, body: str, locale: dict, locales: list[dict], kind: str = "CollectionPage") -> None:
    code, text = locale["code"], TEXT[locale["code"]]
    route = locale_route(locale, tail)
    canonical = f"{BASE_URL}/{route}"
    document_title = f"Tiny Block {text['wiki']} – {text['official']}" if tail == "wiki/" else f"{title} | Tiny Block Wiki"
    alternates = "\n".join(f'  <link rel="alternate" hreflang="{esc(item["hreflang"])}" href="{BASE_URL}/{locale_route(item, tail)}">' for item in locales)
    alternates += f'\n  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/{tail}">'
    breadcrumbs = [{"@type":"ListItem","position":1,"name":"Tiny Block","item":f'{BASE_URL}/{locale["output"] + "/" if locale["output"] else ""}'},{"@type":"ListItem","position":2,"name":text["wiki"],"item":f'{BASE_URL}/{locale_route(locale, "wiki/")}'}]
    if tail != "wiki/":
        breadcrumbs.append({"@type":"ListItem","position":3,"name":title,"item":canonical})
    schema = {"@context":"https://schema.org","@graph":[{"@type":kind,"name":title,"description":description,"url":canonical,"inLanguage":locale["html_lang"],"isPartOf":{"@id":f"{BASE_URL}/#game"}},{"@type":"BreadcrumbList","itemListElement":breadcrumbs}]}
    nav_items = [("wiki","wiki/"),("biomes","wiki/biomes/"),("materials","wiki/materials/"),("creatures","wiki/creatures/"),("plants","wiki/plants/"),("recipes","wiki/recipes/")]
    nav = "".join(f'<a href="/{locale_route(locale, href)}">{esc(text[key])}</a>' for key, href in nav_items)
    if code == "en":
        nav += '<a href="/guides/how-to-grow-your-one-block-island/">Starter guide</a>'
    language_links = "".join(f'<a href="/{locale_route(item, tail)}" lang="{esc(item["html_lang"])}"{(" aria-current=\"page\"" if item["code"] == code else "")}>{esc(item["label"])}</a>' for item in locales)
    home = "/" if not locale["output"] else f'/{locale["output"]}/'
    document = f'''<!DOCTYPE html>
<html lang="{esc(locale["html_lang"])}" dir="{esc(locale["direction"])}">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(document_title)}</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#4aa3d8">
  <meta name="apple-itunes-app" content="app-id=6793160455, app-argument=https://tinyblock.nosuchgames.com/download/">
  <link rel="canonical" href="{canonical}">
{alternates}
  <link rel="icon" href="/favicon.png" type="image/png">
  <meta property="og:title" content="{esc(document_title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="article"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE_URL}/og-seo.png"><meta property="og:locale" content="{esc(locale["og_locale"])}"><meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Lilita+One&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet"><link rel="stylesheet" href="/styles.css?v=20260727-7">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body class="wiki-page"><header class="wiki-header"><a class="wiki-brand" href="{home}">Tiny Block</a><div class="wiki-header-actions"><a class="btn btn-primary wiki-install" href="/download/">{esc(text["play"])}</a><details class="language-menu"><summary aria-label="{esc(text["language"])}">{esc(locale["label"])}</summary><nav aria-label="{esc(text["language"])}">{language_links}</nav></details></div></header>
  <nav class="wiki-nav" aria-label="Tiny Block Wiki">{nav}</nav><main class="wiki-main">{body}</main>
  <footer class="site-foot wiki-foot"><a href="{home}">{esc(text["game"])}</a><a href="/creators/">{esc(text["creators"])}</a><a href="/privacy/">{esc(text["privacy"])}</a><a href="https://nosuchgames.com">No Such Games</a></footer>
</body></html>'''
    target = ROOT / route / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")


def card_grid(items: list[tuple], label: str, category: str, locale: str, catalog: dict) -> str:
    cards = []
    for item in items:
        name, copy, slug = item[0], item[1], item[-1]
        localized_name = entity(catalog, locale, slug, name)
        kind = {"materials":"BLOCK", "creatures":"CREATURE", "plants":"PLANT"}[category]
        localized_copy = copy if locale == "en" else entity(catalog, locale, slug, copy, True, kind)
        cards.append(f'<article class="wiki-card wiki-card-media"><div class="wiki-entity-art"><img src="/assets/wiki/entities/{category}/{slug}.webp" alt="{esc(localized_name)} — Tiny Block" width="512" height="512" loading="lazy"></div><div><p class="wiki-label">{esc(label)}</p><h2>{esc(localized_name)}</h2><p>{esc(localized_copy)}</p></div></article>')
    return '<div class="wiki-grid">' + "".join(cards) + '</div>'


def recipe_item(item: tuple[str, int, str], locale: str, catalog: dict) -> str:
    name, count, slug = item
    name = entity(catalog, locale, slug, name)
    return f'<span class="wiki-recipe-item"><img src="/assets/wiki/entities/materials/{slug}.webp" alt="" width="512" height="512" loading="lazy"><span>{esc(name)}<small>×{count}</small></span></span>'


def recipe_group(items: tuple, locale: str, catalog: dict) -> str:
    return '<div class="wiki-recipe-group">' + '<span class="wiki-recipe-plus" aria-hidden="true">+</span>'.join(recipe_item(item, locale, catalog) for item in items) + '</div>'


def infinite_banner(text: dict[str, str]) -> str:
    return f'<aside class="wiki-infinite"><p class="wiki-label">{esc(text["infinite_kicker"])}</p><h2>{esc(text["infinite_title"])}</h2><p>{esc(text["infinite_copy"])}</p><div class="wiki-infinite-mark" aria-hidden="true">∞</div></aside>'


def biome_variety_banner(text: dict[str, str]) -> str:
    return f'<aside class="wiki-infinite wiki-biome-variety"><p class="wiki-label">{esc(text["kicker"])}</p><h2>{esc(text["title"])}</h2><p>{esc(text["copy"])}</p><div class="wiki-infinite-mark" aria-hidden="true">∞</div></aside>'


def minecraft_links(locale: dict, text: dict[str, str]) -> str:
    prefix = "" if not locale["output"] else f'/{locale["output"]}'
    cards = []
    descriptions = {
        "minecraft-one-block": locale["lede"],
        "minecraft-biomes-list": text["biomes_intro"],
        "minecraft-mobs-list-with-pictures": text["creatures_intro"],
        "minecraft-crafting-recipes": text["recipes_intro"],
    }
    for slug, keyword, _kind in MINECRAFT_SEO_PAGES:
        cards.append(f'<a class="wiki-card wiki-card-link" href="{prefix}/{slug}/"><p class="wiki-label">Minecraft × Tiny Block</p><h2>{esc(keyword)}</h2><p>{esc(descriptions[slug])}</p></a>')
    search_guides = MINECRAFT_SEO_COMMON[locale["code"]][0]
    return f'<section class="wiki-title"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h2>{esc(search_guides)}</h2></section><div class="wiki-grid">' + "".join(cards) + '</div>'


def minecraft_disclaimer(locale_code: str) -> str:
    _search, independent, own_game = MINECRAFT_SEO_COMMON[locale_code]
    return f'<aside class="wiki-infinite"><p class="wiki-label">{esc(independent)}</p><h2>{esc(own_game)}</h2><p>{esc(MINECRAFT_DISCLAIMER)}</p><div class="wiki-infinite-mark" aria-hidden="true">≠</div></aside>'


def comparison_facts(locale_code: str, intro_key: str, facts_key: str) -> str:
    copy = COMPARE[locale_code]
    facts = "".join(f'<article><h3>{esc(title)}</h3><p>{esc(body)}</p></article>' for title, body in copy[facts_key])
    return f'<section class="comparison-section"><div class="comparison-heading"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h2>{esc(copy["title"])}</h2><p>{esc(copy[intro_key])}</p></div><div class="comparison-facts">{facts}</div></section>'


def comparison_duo(left_image: str, left_alt: str, left_caption: str, left_url: str, right_image: str, right_alt: str, right_caption: str) -> str:
    return f'<div class="comparison-duo"><figure><img src="{left_image}" alt="{esc(left_alt)}" width="1200" height="676" loading="lazy"><figcaption><a href="{left_url}" rel="nofollow">{esc(left_caption)}</a></figcaption></figure><figure><img src="{right_image}" alt="{esc(right_alt)}" width="1600" height="900" loading="lazy"><figcaption>{esc(right_caption)}</figcaption></figure></div>'


def one_block_comparison(locale_code: str) -> str:
    copy = COMPARE[locale_code]
    rows = "".join(
        f'<tr><th scope="row">{esc(title)}</th><td data-label="Minecraft One Block">{esc(copy["one_minecraft"][index])}</td><td data-label="Tiny Block">{esc(tiny_body)}</td></tr>'
        for index, (title, tiny_body) in enumerate(copy["one_facts"])
    )
    return f'<div class="comparison-table-wrap"><table class="comparison-table"><thead><tr><th scope="col"></th><th scope="col">Minecraft One Block</th><th scope="col">Tiny Block</th></tr></thead><tbody>{rows}</tbody></table></div>'


def comparison_cta(prefix: str, text: dict[str, str], locale: dict) -> str:
    return f'<div class="wiki-grid"><a class="wiki-card wiki-card-link" href="{prefix}/wiki/"><p class="wiki-label">{esc(text["guide"])}</p><h2>Tiny Block Wiki</h2><p>{esc(text["catalog"])}</p></a><a class="wiki-card wiki-card-link" href="/download/"><p class="wiki-label">iOS + Android</p><h2>{esc(text["play"])}</h2><p>{esc(locale["platforms"])}</p></a></div>'


def minecraft_page_title(kind: str, keyword: str, text: dict[str, str]) -> str:
    if kind == "one-block":
        return f"{keyword} vs Tiny Block"
    if kind == "biomes":
        return f"{keyword} vs Tiny Block {text['biomes']}"
    if kind == "mobs":
        return f"{keyword}: Tiny Block {text['creatures']}"
    return f"{keyword} vs Tiny Block {text['recipes']}"


def minecraft_page_body(kind: str, keyword: str, locale: dict, text: dict[str, str], catalog: dict) -> tuple[str, str]:
    prefix = "" if not locale["output"] else f'/{locale["output"]}'
    if kind == "one-block":
        copy = COMPARE[locale["code"]]
        description = f'{keyword}. {copy["one_intro"]}'
        media = comparison_duo(
            "/assets/wiki/minecraft/one-block.jpg",
            "Minecraft Marketplace 1 Block Skyblock by Fall Studios",
            f'1 Block Skyblock by Fall Studios · {copy["source"]}',
            "https://www.minecraft.net/en-us/article/marketplace-content-april-2026",
            "/assets/wiki/gameplay/00-one-block-start.webp?v=20260727-one-block",
            "Tiny Block One Block starting world",
            copy["tiny"],
        )
        comparison = f'<section class="comparison-section"><div class="comparison-heading"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h2>{esc(copy["title"])}</h2><p>{esc(copy["one_intro"])}</p></div>{one_block_comparison(locale["code"])}</section>'
        body = f'<section class="wiki-title"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h1 class="comparison-title">{esc(keyword)} vs Tiny Block</h1><p>{esc(locale["lede"])}</p></section>{media}{minecraft_disclaimer(locale["code"])}{comparison}{comparison_cta(prefix, text, locale)}'
        return description, body

    if kind == "biomes":
        copy = COMPARE[locale["code"]]
        description = f'{keyword}. {copy["biome_intro"]}'
        biome_terrain = {slug: terrain for _name, _description, terrain, _plants, _creatures, _image, slug in BIOMES}
        pairs = "".join(
            f'<article class="comparison-pair"><div class="comparison-pair-images"><figure><img src="/assets/wiki/minecraft/{mc_image}" alt="Minecraft {esc(mc_name)} biome" width="1170" height="500" loading="lazy"><figcaption><a href="{source}" rel="nofollow">Minecraft: {esc(mc_name)} · {esc(copy["source"])}</a></figcaption></figure><figure><img src="/assets/wiki/biomes/{tiny_image}?v=20260727-game" alt="Tiny Block {esc(TERMS[locale["code"]][tiny_slug])} biome" width="2560" height="1280" loading="lazy"><figcaption>Tiny Block: {esc(TERMS[locale["code"]][tiny_slug])}</figcaption></figure></div><h2>{esc(mc_name)} ↔ {esc(TERMS[locale["code"]][tiny_slug])}</h2><p>{esc(copy["biome_pair"])}</p><p><strong>{esc(text["terrain"])}:</strong> {esc(localize_list(biome_terrain[tiny_slug], locale["code"], catalog))}</p></article>'
            for mc_name, mc_image, tiny_slug, tiny_image, source in MINECRAFT_BIOME_PAIRS
        )
        body = f'<section class="wiki-title"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h1 class="comparison-title">{esc(keyword)} vs Tiny Block {esc(text["biomes"])}</h1><p>{esc(copy["biome_intro"])}</p></section>{minecraft_disclaimer(locale["code"])}<section class="comparison-section"><div class="comparison-heading"><h2>{esc(copy["title"])}</h2><p>{esc(copy["biome_intro"])}</p></div><div class="comparison-pairs">{pairs}</div></section>{comparison_cta(prefix, text, locale)}'
        return description, body

    if kind == "mobs":
        copy = COMPARE[locale["code"]]
        description = f'{keyword}. {copy["mobs_intro"]}'
        collage = "".join(f'<img src="/assets/wiki/entities/creatures/{slug}.webp" alt="{esc(entity(catalog, locale["code"], slug, name))}" width="512" height="512" loading="lazy">' for name, _creature_copy, _habitat, slug in CREATURES[:6])
        media = f'<div class="comparison-duo"><figure><img src="/assets/wiki/minecraft/mobs.jpg" alt="Minecraft hostile and passive mobs" width="1200" height="676" loading="lazy"><figcaption><a href="https://www.minecraft.net/en-us/article/minecraft-mobs" rel="nofollow">{esc(copy["source"])}</a></figcaption></figure><figure class="comparison-entity-figure"><div class="comparison-entity-collage">{collage}</div><figcaption>{esc(copy["tiny"])}</figcaption></figure></div>'
        examples = [(name, f'{creature_copy} Habitat: {habitat}.', slug) for name, creature_copy, habitat, slug in CREATURES[:6]]
        body = f'<section class="wiki-title"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h1 class="comparison-title">{esc(keyword)}: Tiny Block {esc(text["creatures"])}</h1><p>{esc(copy["mobs_intro"])}</p></section>{minecraft_disclaimer(locale["code"])}{media}{comparison_facts(locale["code"], "mobs_intro", "mobs_facts")}{card_grid(examples, text["creature"], "creatures", locale["code"], catalog)}{comparison_cta(prefix, text, locale)}'
        return description, body

    copy = COMPARE[locale["code"]]
    description = f'{keyword}. {copy["craft_intro"]}'
    media = comparison_duo("/assets/wiki/minecraft/crafting.jpg", "Minecraft crafting recipe book", copy["source"], "https://www.minecraft.net/en-us/article/how-craft", "/assets/wiki/gameplay/06-recipes-inventory.webp", "Tiny Block recipes catalog", copy["tiny"])
    rows = "".join(f'<tr><td data-label="{esc(text["ingredients"])}">{recipe_group(recipe[:-1], locale["code"], catalog)}</td><td data-label="{esc(text["result"])}">{recipe_group(recipe[-1:], locale["code"], catalog)}</td></tr>' for recipe in RECIPES[:6])
    body = f'<section class="wiki-title"><p class="wiki-eyebrow">Minecraft × Tiny Block</p><h1 class="comparison-title">{esc(keyword)} vs Tiny Block {esc(text["recipes"])}</h1><p>{esc(copy["craft_intro"])}</p></section>{minecraft_disclaimer(locale["code"])}{media}{comparison_facts(locale["code"], "craft_intro", "craft_facts")}<div class="wiki-table-wrap"><table class="wiki-table"><thead><tr><th>{esc(text["ingredients"])}</th><th>{esc(text["result"])}</th></tr></thead><tbody>{rows}</tbody></table></div>{comparison_cta(prefix, text, locale)}'
    return description, body


def render() -> None:
    locales, catalog = load_catalog()
    for locale in locales:
        code, text = locale["code"], TEXT[locale["code"]]
        prefix = "" if not locale["output"] else f'/{locale["output"]}'
        overview = f'<section class="wiki-hero"><p class="wiki-eyebrow">{esc(text["official"])}</p><h1>Tiny Block {esc(text["wiki"])}</h1><p>{esc(text["overview"])}</p><img src="/assets/wiki/gameplay/05-random-world.webp?v=20260726-color" alt="Tiny Block" width="1600" height="900"></section>{infinite_banner(text)}'
        overview += '<div class="wiki-grid">' + "".join(f'<a class="wiki-card wiki-card-link" href="{prefix}/wiki/{slug}/"><p class="wiki-label">{esc(text["guide"])}</p><h2>{esc(text[key])}</h2><p>{esc(text["catalog"])}</p></a>' for key, slug in (("biomes","biomes"),("materials","materials"),("creatures","creatures"),("plants","plants"),("recipes","recipes"))) + '</div>'
        if code == "en":
            overview = overview[:-6] + '<a class="wiki-card wiki-card-link" href="/guides/how-to-grow-your-one-block-island/"><p class="wiki-label">Guide</p><h2>Starter guide</h2><p>Grow a safe and renewable One Block island from the first discovery.</p></a></div>'
        overview += minecraft_links(locale, text)
        page(f'Tiny Block {text["wiki"]}', text["overview"], "wiki/", overview, locale, locales)

        biome_cards = []
        for name, copy, terrain, plants, creatures, image, slug in BIOMES:
            image_width, image_height = (2493, 1280) if image == "beach.webp" else (2560, 1280)
            image_version = "20260727-beach2" if image == "beach.webp" else "20260727-game"
            localized_name = TERMS[code][slug]
            description = f'<p>{esc(copy)}</p>' if code == "en" else ""
            biome_cards.append(f'<article class="wiki-entry wiki-entry-media"><img src="/assets/wiki/biomes/{image}?v={image_version}" alt="{esc(localized_name)} — Tiny Block" width="{image_width}" height="{image_height}" loading="lazy"><div><p class="wiki-label">{esc(text["biome"])}</p><h2>{esc(localized_name)}</h2>{description}<dl><dt>{esc(text["terrain"])}</dt><dd>{esc(localize_list(terrain, code, catalog))}</dd><dt>{esc(text["plants"])}</dt><dd>{esc(localize_list(plants, code, catalog))}</dd><dt>{esc(text["creatures"])}</dt><dd>{esc(localize_list(creatures, code, catalog))}</dd></dl></div></article>')
        page(text["biomes"], text["biomes_intro"], "wiki/biomes/", f'<section class="wiki-title"><p class="wiki-eyebrow">{esc(text["world"])}</p><h1>{esc(text["biomes"])}</h1><p>{esc(text["biomes_intro"])}</p></section>{biome_variety_banner(BIOME_VARIETY[code])}<div class="wiki-stack">{"".join(biome_cards)}</div>', locale, locales)
        page(text["materials"], text["materials_intro"], "wiki/materials/", f'<section class="wiki-title"><p class="wiki-eyebrow">{esc(text["mining"])}</p><h1>{esc(text["materials"])}</h1><p>{esc(text["materials_intro"])}</p></section>{infinite_banner(text)}{card_grid(MATERIALS, text["material"], "materials", code, catalog)}', locale, locales)
        creature_items = [(name, f'{copy} Habitat: {habitat}.', slug) for name, copy, habitat, slug in CREATURES]
        page(text["creatures"], text["creatures_intro"], "wiki/creatures/", f'<section class="wiki-title"><p class="wiki-eyebrow">{esc(text["living"])}</p><h1>{esc(text["creatures"])}</h1><p>{esc(text["creatures_intro"])}</p></section>{infinite_banner(text)}{card_grid(creature_items, text["creature"], "creatures", code, catalog)}', locale, locales)
        page(text["plants"], text["plants_intro"], "wiki/plants/", f'<section class="wiki-title"><p class="wiki-eyebrow">{esc(text["growing"])}</p><h1>{esc(text["plants"])}</h1><p>{esc(text["plants_intro"])}</p></section>{infinite_banner(text)}{card_grid(PLANTS, text["plant"], "plants", code, catalog)}', locale, locales)
        rows = "".join(f'<tr><td data-label="{esc(text["ingredients"])}">{recipe_group(recipe[:-1], code, catalog)}</td><td data-label="{esc(text["result"])}">{recipe_group(recipe[-1:], code, catalog)}</td></tr>' for recipe in RECIPES)
        recipes_body = f'<section class="wiki-title"><p class="wiki-eyebrow">{esc(text["crafting"])}</p><h1>{esc(text["recipes"])}</h1><p>{esc(text["recipes_intro"])}</p></section>{infinite_banner(text)}<div class="wiki-table-wrap"><table class="wiki-table"><thead><tr><th>{esc(text["ingredients"])}</th><th>{esc(text["result"])}</th></tr></thead><tbody>{rows}</tbody></table></div><figure class="wiki-wide-media"><img src="/assets/wiki/gameplay/06-recipes-inventory.webp" alt="Tiny Block" width="1600" height="739" loading="lazy"><figcaption>{esc(text["recipe_caption"])}</figcaption></figure>'
        page(text["recipes"], text["recipes_intro"], "wiki/recipes/", recipes_body, locale, locales)

        for slug, keyword, kind in MINECRAFT_SEO_PAGES:
            description, body = minecraft_page_body(kind, keyword, locale, text, catalog)
            page(minecraft_page_title(kind, keyword, text), description, f"{slug}/", body, locale, locales, "Article")


if __name__ == "__main__":
    render()
