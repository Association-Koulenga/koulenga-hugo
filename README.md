# Site de l'Association Koulenga — dev.koulenga.com

Site statique [Hugo](https://gohugo.io/) de l'association Koulenga, migré depuis Grav
conformément au **plan de migration v2** (`plan-migration-koulenga-grav-vers-hugo.md`,
anomalies C1–C5 corrigées, revue « production ready » du 02/11/2026 intégrée).

## Structure

```
koulenga-hugo/
├── hugo.toml            # config du site (§9) : C1–C5, menus en pageRef, params charte
├── content/fr/          # contenu français (page bundles + médias, URLs /fr/… conservées)
├── themes/koulenga/     # thème (portage du thème Grav koulenga / Quark / Spectre)
├── static/
│   ├── admin/           # Sveltia CMS — back-office des éditeurs (§8 du plan)
│   └── images/          # médias globaux (bibliothèque du CMS)
└── README.md
```

## Prérequis

- **Hugo extended 0.169.x** (épinglé — v0.146 minimum, changement majeur de résolution
  des templates ; `extended` requis pour `toCSS`/pipeline d'images de la phase 7).

## Build

```sh
# développement
hugo server -D

# production (§10.1) : --gc nettoie les images orphelines du cache, --minify,
# --printPathWarnings fait remonter les duplications de chemins (type C1)
hugo --gc --minify --printPathWarnings --printI18nWarnings
```

Sortie attendue : ~30–40 pages HTML + ~140 médias, build < 1 s sans pipeline d'images.
La 404 est générée sous `/fr/404.html` (`defaultContentLanguageInSubdir`, vérifié) :
la CI copie `public/fr/404.html` → `public/404.html` pour GitHub Pages (A6).

## Thème `koulenga`

Portage du thème Grav `koulenga` (surcouche de **Quark 2.1.6** / **Spectre.css**,
icônes **Line Awesome**) — charte : fond terracotta `#996a51`, texte blanc, header
fixe/transparent, sticky footer, menu burger mobile plein écran.

- **Phase 1 (fidélité)** : les CSS compilés Grav (`spectre.css`, `spectre-icons.css`,
  `theme.css`, `custom.css`, `line-awesome.min.css`) sont repris **tels quels** dans
  `themes/koulenga/assets/css/`, minifiés + empreintés à chaque build ; les ajouts
  du portage (skip-link, `prefers-reduced-motion`, focus clavier) vivent dans
  `assets/css/koulenga.css`. Phase 2 éventuelle : portage SCSS + Dart Sass épinglé.
- **JS vanilla** (`assets/js/site.js`) : portage de `site.js` + `jquery.treemenu.js`
  de Quark **sans jQuery** — header « scrolled », burger accessible (ARIA, focus,
  Escape), tree menu, défilement `#to-start`. Aucun autre JS n'est chargé.
- **SEO** : title corrigé, description par page, canonical, Open Graph, Twitter
  Cards, JSON-LD (NGO + BreadcrumbList), robots.txt avec `Sitemap:`, RSS `/fr/index.xml`.
- **Redirections** : `aliases` en front matter **sans préfixe `/fr`** (C2) — la page
  d'alias est surchargée dans le thème avec `noindex` (A15). **Attention** : depuis
  Hugo 0.146, les sections sans `_index.md` sont rendues automatiquement — pour les
  anciennes URLs `/fr/association/` et `/fr/actions/` (pages-redirect Grav), utiliser
  le layout dédié **`layout: redirect`** (décision A7-a du plan §4.6) sur le branch
  bundle correspondant avec `params.redirect: /association/oyonnax` (chemin logique
  sans `/fr`) : un `aliases` ciblant la même URL entrerait en collision avec la page
  de section auto-rendue (vérifié par build de test).

## Édition (bénévoles)

Back-office Sveltia CMS sur **`https://dev.koulenga.com/admin/`** (connexion GitHub) —
collections, workflow brouillon → revue → publication : voir
`static/admin/README-SVELTIA.md` et la section 8 du plan. Les éditeurs ne touchent
jamais à `themes/` ni à la CI.
