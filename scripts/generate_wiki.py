#!/usr/bin/env python3
"""Generate the first Tiny Block wiki pages from the shipped game catalog."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://tinyblock.nosuchgames.com"

BIOMES = [
    ("Plains", "Open grassland with occasional trees.", "Grass, dirt, stone", "Meadow Bloom, Prairie Sprig, Oak, Weeping Tree", "Meadow Hopper, Forest Fox, Sky Mote", "plains.webp"),
    ("Forest", "A damp woodland rich in trees and small creatures.", "Grass, dirt, stone, wood", "Prairie Sprig, Meadow Bloom, Oak, Weeping Tree", "Forest Fox, Moss Crawler, Moss Slug", "forest.webp"),
    ("Tundra", "A cold open land where water slowly freezes.", "Dirt, stone, ice", "Pine", "Snow Penguin, Sky Mote, Gloomwing", "tundra.webp"),
    ("Ice Fields", "A barren glacier of deep ice, frozen water, and exposed stone.", "Ice, stone, water", "—", "Snow Penguin, Sky Mote, Gloomwing", "ice-fields.webp"),
    ("Desert", "Dry dunes over deep stone.", "Sand, stone", "—", "Sky Mote, Dusk Prowler", "desert.webp"),
    ("Obsidian Wastes", "Weathered volcanic ground hiding obsidian, ancient formations, and lava pools.", "Cobblestone, stone, obsidian, lava", "—", "Ember Walker, Cinder Eel, Gloomwing", "obsidian.webp"),
    ("Beach", "A warm sandy edge beside open water.", "Sand, stone, water", "Palm", "Pool Drifter, Sand Crab, Sky Mote", "beach.webp"),
    ("Riverbank", "Low sandy ground shaped by flowing water.", "Sand, stone, water", "—", "Pool Drifter, Sand Crab, Moss Slug", "riverbank.webp"),
    ("Cavern", "A dark underground habitat.", "Stone", "Cave Vines", "Cave Spider, Cave Skitter, Moss Crawler", "cavern.webp"),
    ("Volcanic", "Hot rock pockets inhabited by ember creatures.", "Stone, obsidian, lava", "—", "Ember Walker, Cinder Eel", "volcanic.webp"),
]

MATERIALS = [
    ("Grass", "A living surface block used to expand fertile ground.", "grass"),
    ("Dirt", "A basic building and planting block found beneath grass.", "dirt"),
    ("Stone", "A durable underground block and a core crafting ingredient.", "stone"),
    ("Wood", "A flammable tree material that can be cut into planks.", "wood"),
    ("Water", "A flowing liquid that combines with lava to create new materials.", "water"),
    ("Lava", "A hot, slow-moving liquid used in several transformation recipes.", "lava"),
    ("Gravel", "A loose block that falls when unsupported and can become sand.", "gravel"),
    ("Sand", "A falling block used for glass and sandstone.", "sand"),
    ("Glass", "A translucent building block crafted from sand and lava.", "glass"),
    ("Charcoal", "A combustible material produced by combining wood and lava.", "charcoal"),
    ("Ice", "A cold, slippery block found in tundra and ice biomes.", "ice"),
    ("Packed Ice", "Dense polished ice that stays cold and is especially slippery.", "packed-ice"),
    ("Obsidian", "Very hard volcanic glass formed from stone, water, and lava.", "obsidian"),
    ("Lantern", "A charcoal lamp enclosed in glass that lights nearby blocks.", "lantern"),
]

PLANTS = [
    ("Meadow Bloom", "A bright wildflower that dots sunny plains with color.", "meadow-bloom"),
    ("Prairie Sprig", "A small branching plant that grows between open grassland paths.", "prairie-sprig"),
    ("Cave Vines", "Leafy strands that hang from cool stone ceilings in dark caverns.", "cave-vines"),
    ("Potted Fern", "A hardy fern kept in a warm clay pot for shelters and ruins.", "potted-fern"),
    ("Oak", "A sturdy broad-crowned tree common to plains and forests.", "oak"),
    ("Palm", "A tall bare-trunked tree crowned with wide tropical fronds.", "palm"),
    ("Pine", "A cold-tolerant evergreen with a narrow layered crown.", "pine"),
    ("Weeping Tree", "A moisture-loving tree whose foliage hangs toward the ground.", "weeping-tree"),
]

CREATURES = [
    ("Meadow Hopper", "A gentle long-eared meadow creature that bounds away after being hurt.", "Plains, Forest", "meadow-hopper"),
    ("Forest Fox", "A quick orange wanderer that avoids danger and follows berry-like plants.", "Plains, Forest", "forest-fox"),
    ("Sky Mote", "A shy flying creature that drifts through bright open air.", "Open biomes", "sky-mote"),
    ("Moss Crawler", "A dark-loving crawler drawn to moss that fights back when attacked.", "Forest, Cavern", "moss-crawler"),
    ("Moss Slug", "A slow harmless slug found in damp shade near mossy plants.", "Forest, Riverbank", "moss-slug"),
    ("Pool Drifter", "A timid blue fish that swims through water and flees from danger.", "Beach, Riverbank", "pool-drifter"),
    ("Sand Crab", "A small beach crab that scuttles over sand and defends itself.", "Beach, Riverbank", "sand-crab"),
    ("Snow Penguin", "A friendly cold-weather waddler that stays near ice and water.", "Tundra, Ice Fields", "snow-penguin"),
    ("Ember Walker", "A heatproof creature that walks along lava bottoms.", "Obsidian Wastes, Volcanic", "ember-walker"),
    ("Cave Skitter", "A red-eyed cave crawler that prefers deep darkness.", "Cavern", "cave-skitter"),
    ("Cave Spider", "A shy eight-legged hunter that hides among cave vines.", "Forest caves, Cavern", "cave-spider"),
    ("Watcher Bloom", "A rooted flower-creature that watches sunny clearings.", "Plains, Forest", "watcher-bloom"),
    ("Dusk Prowler", "A solitary night hunter that stalks open ground.", "Plains, Desert", "dusk-prowler"),
    ("Gloomwing", "A rare dark-loving flier that hunts after sunset.", "Forest, Tundra, Cavern", "gloomwing"),
    ("Cinder Eel", "A fierce lava swimmer that emerges at night.", "Obsidian Wastes, Volcanic", "cinder-eel"),
]

RECIPES = [
    (("Water", 1, "water"), ("Lava", 1, "lava"), ("Cobblestone", 1, "cobblestone")),
    (("Cobblestone", 4, "cobblestone"), ("Stone", 1, "stone")),
    (("Leaves", 4, "leaves"), ("Wood", 1, "wood")),
    (("Stone", 1, "stone"), ("Gravel", 1, "gravel")),
    (("Gravel", 1, "gravel"), ("Sand", 1, "sand")),
    (("Sand", 1, "sand"), ("Lava", 1, "lava"), ("Glass", 1, "glass")),
    (("Wood", 1, "wood"), ("Lava", 1, "lava"), ("Charcoal", 1, "charcoal")),
    (("Wood", 1, "wood"), ("Planks", 4, "planks")),
    (("Stone", 1, "stone"), ("Water", 1, "water"), ("Lava", 1, "lava"), ("Obsidian", 1, "obsidian")),
    (("Planks", 2, "planks"), ("Stone", 1, "stone"), ("Stone Pickaxe", 1, "stone-pickaxe")),
    (("Planks", 4, "planks"), ("Chest", 1, "chest")),
    (("Ice", 4, "ice"), ("Packed Ice", 1, "packed-ice")),
    (("Charcoal", 1, "charcoal"), ("Glass", 1, "glass"), ("Stone", 1, "stone"), ("Lantern", 1, "lantern")),
    (("Stone", 2, "stone"), ("Stone Bricks", 2, "stone-bricks")),
    (("Sand", 2, "sand"), ("Stone", 1, "stone"), ("Sandstone", 3, "sandstone")),
]

NAV = [
    ("Wiki", "/wiki/"), ("Biomes", "/wiki/biomes/"), ("Materials", "/wiki/materials/"),
    ("Creatures", "/wiki/creatures/"), ("Plants", "/wiki/plants/"),
    ("Recipes", "/wiki/recipes/"), ("Starter guide", "/guides/how-to-grow-your-one-block-island/"),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def page(title: str, description: str, route: str, body: str, kind: str = "CollectionPage") -> None:
    canonical = f"{BASE_URL}/{route}"
    document_title = "Tiny Block Wiki – Official Game Guide" if route == "wiki/" else f"{title} | Tiny Block Wiki"
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "Tiny Block", "item": f"{BASE_URL}/"},
        {"@type": "ListItem", "position": 2, "name": "Wiki", "item": f"{BASE_URL}/wiki/"},
    ]
    if route != "wiki/":
        breadcrumbs.append({"@type": "ListItem", "position": 3, "name": title, "item": canonical})
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": kind, "name": title, "description": description, "url": canonical, "isPartOf": {"@id": f"{BASE_URL}/#game"}},
            {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
        ],
    }
    nav = "".join(f'<a href="{href}">{esc(label)}</a>' for label, href in NAV)
    document = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(document_title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#4aa3d8">
  <meta name="apple-itunes-app" content="app-id=6793160455, app-argument=https://tinyblock.nosuchgames.com/download/">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/favicon.png" type="image/png">
  <meta property="og:title" content="{esc(document_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE_URL}/og-seo.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Lilita+One&amp;family=Nunito:wght@500;700;800&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(',', ':'))}</script>
</head>
<body class="wiki-page">
  <header class="wiki-header"><a class="wiki-brand" href="/">Tiny Block</a><a class="btn btn-primary wiki-install" href="/download/">Play free</a></header>
  <nav class="wiki-nav" aria-label="Tiny Block Wiki">{nav}</nav>
  <main class="wiki-main">{body}</main>
  <footer class="site-foot wiki-foot"><a href="/">Game</a><a href="/creators/">Creators</a><a href="/privacy/">Privacy</a><a href="https://nosuchgames.com">No Such Games</a></footer>
</body>
</html>'''
    target = ROOT / route / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")


def card_grid(items: list[tuple[str, str, str]], label: str, category: str) -> str:
    cards = "".join(
        f'<article class="wiki-card wiki-card-media"><div class="wiki-entity-art"><img src="/assets/wiki/entities/{esc(category)}/{esc(slug)}.webp" alt="{esc(name)} in Tiny Block" width="512" height="512" loading="lazy"></div><div><p class="wiki-label">{esc(label)}</p><h2>{esc(name)}</h2><p>{esc(copy)}</p></div></article>'
        for name, copy, slug in items
    )
    return f'<div class="wiki-grid">{cards}</div>'


def recipe_item(item: tuple[str, int, str]) -> str:
    name, count, slug = item
    return f'<span class="wiki-recipe-item"><img src="/assets/wiki/entities/materials/{esc(slug)}.webp" alt="" width="512" height="512" loading="lazy"><span>{esc(name)}<small>×{count}</small></span></span>'


def recipe_group(items: tuple[tuple[str, int, str], ...]) -> str:
    return '<div class="wiki-recipe-group">' + '<span class="wiki-recipe-plus" aria-hidden="true">+</span>'.join(recipe_item(item) for item in items) + '</div>'


def render() -> None:
    overview = '''<section class="wiki-hero"><p class="wiki-eyebrow">Official game guide</p><h1>Tiny Block Wiki</h1><p>Explore the biomes, materials, recipes, plants, and creatures already living inside Tiny Block.</p><img src="/assets/wiki/gameplay/05-random-world.webp" alt="A generated floating island in Tiny Block" width="1600" height="738"></section>'''
    overview += '<div class="wiki-grid">' + "".join(
        f'<a class="wiki-card wiki-card-link" href="{href}"><p class="wiki-label">Guide</p><h2>{esc(label)}</h2><p>Open the current in-game catalog and learn where each discovery fits.</p></a>'
        for label, href in NAV[1:]
    ) + "</div>"
    page("Tiny Block Wiki", "The official guide to Tiny Block biomes, materials, crafting recipes, plants, creatures, and One Block progression.", "wiki/", overview)

    biome_cards = []
    for name, copy, terrain, plants, creatures, image in BIOMES:
        media = f'<img src="/assets/wiki/biomes/{image}" alt="{esc(name)} biome in Tiny Block" width="1600" height="739" loading="lazy">' if image else ""
        biome_cards.append(f'<article class="wiki-entry wiki-entry-media">{media}<div><p class="wiki-label">Biome</p><h2>{esc(name)}</h2><p>{esc(copy)}</p><dl><dt>Terrain</dt><dd>{esc(terrain)}</dd><dt>Plants</dt><dd>{esc(plants)}</dd><dt>Creatures</dt><dd>{esc(creatures)}</dd></dl></div></article>')
    page("Biomes", "Discover the ten current Tiny Block biomes, their terrain, plants, creatures, fluids, and environmental character.", "wiki/biomes/", '<section class="wiki-title"><p class="wiki-eyebrow">World generation</p><h1>Biomes</h1><p>Floating Islands can lead from bright plains to glaciers, beaches, caverns, and volcanic ground.</p></section><div class="wiki-stack">' + "".join(biome_cards) + "</div>")

    page("Materials", "A practical catalog of Tiny Block building materials and their physical behavior in the 2D sandbox.", "wiki/materials/", '<section class="wiki-title"><p class="wiki-eyebrow">Mining and building</p><h1>Materials</h1><p>Materials do more than decorate: fluids flow, loose blocks fall, ice slides, and lava transforms ingredients.</p></section>' + card_grid(MATERIALS, "Material", "materials"))

    creature_cards = [(name, f"{copy} Habitat: {habitat}.", slug) for name, copy, habitat, slug in CREATURES]
    page("Creatures", "Meet the current Tiny Block creatures and learn which biomes and conditions they prefer.", "wiki/creatures/", '<section class="wiki-title"><p class="wiki-eyebrow">Living worlds</p><h1>Creatures</h1><p>Passive, fearful, defensive, and aggressive creatures behave differently across daylight, water, caves, and lava.</p></section>' + card_grid(creature_cards, "Creature", "creatures"))

    page("Plants", "Explore Tiny Block flowers, vines, decorative plants, and biome-specific trees.", "wiki/plants/", '<section class="wiki-title"><p class="wiki-eyebrow">Growing discoveries</p><h1>Plants</h1><p>Plant life ranges from single flowers and potted decor to hanging cave vines and full trees.</p></section>' + card_grid(PLANTS, "Plant", "plants"))

    rows = "".join(f'<tr><td>{recipe_group(recipe[:-1])}</td><td>{recipe_group(recipe[-1:])}</td></tr>' for recipe in RECIPES)
    page("Crafting Recipes", "Current starter recipes for materials, tools, storage, building blocks, and light in Tiny Block.", "wiki/recipes/", f'<section class="wiki-title"><p class="wiki-eyebrow">Crafting</p><h1>Recipes</h1><p>Use mined blocks and physical reactions to unlock stronger tools and new building materials.</p></section><div class="wiki-table-wrap"><table class="wiki-table"><thead><tr><th>Ingredients</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table></div><figure class="wiki-wide-media"><img src="/assets/wiki/gameplay/06-recipes-inventory.webp" alt="Tiny Block crafting recipes and inventory" width="1600" height="738" loading="lazy"><figcaption>The in-game recipe catalog shows what can be made from discoveries in the current world.</figcaption></figure>')

    guide = '''<section class="wiki-title"><p class="wiki-eyebrow">One Block starter guide</p><h1>How to grow your floating island</h1><p>Turn the first block into a safe, renewable base before exploring farther biomes.</p></section>
    <div class="guide-steps">
      <article><span>01</span><h2>Mine carefully</h2><p>Keep enough space around your starting point and collect the first grass, dirt, stone, wood, water, and lava discoveries.</p></article>
      <article><span>02</span><h2>Create renewable stone</h2><p>Combine water and lava for cobblestone, then use four cobblestone to craft stone.</p></article>
      <article><span>03</span><h2>Build a safe platform</h2><p>Expand horizontally before digging deep. Keep fluids separated and leave room for trees and plants to grow.</p></article>
      <article><span>04</span><h2>Craft tools and storage</h2><p>Turn wood into planks, then make a pickaxe and chest. Better tools shorten mining time and protect your discoveries.</p></article>
      <article><span>05</span><h2>Follow new biomes</h2><p>Floating Islands introduce different terrain, plants, creatures, and recipes. Prepare for darkness, ice, lava, and aggressive night creatures.</p></article>
    </div>
    <figure class="wiki-wide-media"><img src="/assets/wiki/gameplay/01-one-block-skyblock.webp" alt="Starting a One Block Skyblock world in Tiny Block" width="1600" height="738"><figcaption>A new One Block world starts small and grows through mining, crafting, and discovery.</figcaption></figure>'''
    page("How to Grow a One Block Island", "A beginner guide to mining, crafting, expanding, and surviving your first One Block Skyblock island in Tiny Block.", "guides/how-to-grow-your-one-block-island/", guide, "Article")


if __name__ == "__main__":
    render()
