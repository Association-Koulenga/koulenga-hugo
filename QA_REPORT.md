# Rapport d'intégration & QA — site Hugo de l'Association Koulenga

**Date :** 02/11/2026 · **Hugo :** v0.169.0+extended (`/opt/data/tools/hugo`, linux/arm64) · **Référentiel :** plan de migration v2 (§9 configuration, §10.2 checklist QA, §13 checklist de fin) · **Agent :** intégration & QA.

---

## 1. Résultat global

| | |
|---|---|
| Build `hugo --gc --minify --printPathWarnings --printI18nWarnings --logLevel info` | **EXIT 0, zéro warning** |
| Pages générées | 19 (dont 13 rendues : home + 11 pages + redirect `/fr/association/` + 404) |
| Fichiers non-page (médias des page bundles) | 142 |
| Fichiers statiques | 11 (`static/` + `CNAME`) |
| Aliases | 3 (`/home`, `/actions`, racine `/`) |
| QA programmatique (`scripts/qa_checks.py`) | **31 vérifications OK, 0 échec** |
| Menu | 7 entrées racine + 5 enfants, **chaque entrée exactement 1 fois** |

## 2. Corrections appliquées

### 2.1 Doublon de menu `hugo.toml` vs front matter (cause du bug)
Le front matter des pages portait l'arbre complet **avec enfants** (`identifier`/`parent`/`weight` : `association` → Teeli Yan, Adhésions & Dons, Contact et statuts ; `actions` → Réalisations, Dans la presse), **et** `hugo.toml` déclarait 7 blocs `[[menus.main]]` en parallèle → chaque entrée sortait 2 fois dans la nav.
**Décision (conforme au choix indiqué) : suppression des blocs `[[menus.main]]` de `hugo.toml`** ; le front matter est la source unique de vérité. Vérifié par build : la nav sort `Accueil → L'école - Le village → Le Burkina Faso → L'association (+3) → Actions (+2) → Le journal de Goudrin → Diaporama`, dans cet ordre, sans doublon (check QA §8).

### 2.2 `static/admin/config.yml` (Sveltia CMS) aligné sur la structure réelle
- `actualites` : `content/fr/sections/news.md` → **`content/fr/sections/news/index.md`** (page bundle headless réel).
- `photos` : l'option galerie commentée pointait vers `sections/galerie.md` (inexistant) → alignée sur **`content/fr/sections/photos/index.md`** (page headless « Cross » réelle, non rendue seule), reste commentée tant que la décision §8.6 (ligne 5) n'est pas tranchée.
- Vérifié : aucun secret dans `static/admin/` (check QA §9 — seule la prose du README mentionne le mot « secret », aucune valeur).

### 2.3 Vérifications de configuration (C1–C5) — conformes, rien à corriger
`contentDir = "content/fr"` (C1) ✓ · `locale = "fr-FR"`, `label` (C5 : pas de `languageCode`/`languageName` dépréciés) ✓ · `disableKinds = ["taxonomy", "term"]` seul (C4 : sitemap/RSS/404 actifs) ✓ · `enableRobotsTXT = true` + `timeout = "120s"` ✓ · `wrapStandAloneImageWithinParagraph = false`, `unsafe` non activé ✓.

### 2.4 Améliorations qualité détectées pendant la QA
- **`/fr/association/` exclu du sitemap** (`sitemap: disable: true` en front matter) : c'est une page de redirection noindex — elle n'a pas à être proposée aux moteurs (le `fr/sitemap.xml` passe de 13 à **12 `<loc>`** : home + 11 pages).
- **`partials/images-block.html`** : émission de `width`/`height` sur les `<img>` (les 4 images du bloc « Cross » de la home n'avaient que `loading`/`decoding`) → 0 image interne sans dimensions.
- **`partials/mobile-menu.html`** : `loading="lazy"` sur le logo du menu overlay. Le logo d'en-tête reste **volontairement eager** (above-the-fold, LCP).
- **`static/CNAME`** : `koulenga.com` ajouté (domaine personnalisé GitHub Pages, §10.3-A — à activer avec « Enforce HTTPS » dans les réglages Pages).

## 3. Vérifications QA (script : `scripts/qa_checks.py`, résultats : `qa_results.json`)

| # | Vérification | Résultat |
|---|---|---|
| 1 | Aucune URL ni chemin `/fr/fr/` (C1) | OK — 0 fichier, 0 occurrence HTML |
| 2 | Mapping §5.1 : 14 URLs + home servies | OK — 14/14 présentes dans `public/` |
| 2 | Variantes sans slash final (répertoire + index) | OK — toutes |
| 3 | Alias `/home` → `/fr/` : meta-refresh 0 s + noindex + canonical | OK |
| 3 | Alias `/actions` → `/fr/actions/a-venir/` : idem | OK |
| 3 | Racine `/` → `/fr/` (auto Hugo) : idem | OK |
| 3 | `/fr/association/` : layout redirect → `/fr/association/oyonnax/` + noindex | OK |
| 3 | PDF AG de `/fr/association/*.pdf` publiés malgré la redirection (A7) | OK |
| 4 | Render hook liens : `target="_blank"` ⇒ `rel="noopener noreferrer"` | OK — 0 anomalie sur tout le site |
| 4 | Render hook images : `loading="lazy"` partout | OK — 0 anomalie (chrome `/img/` volontairement eager) |
| 4 | Images internes : `width` + `height` (anti-CLS) | OK — 0 anomalie |
| 5 | `sitemap.xml` racine = sitemapindex → `/fr/sitemap.xml` | OK |
| 5 | `fr/sitemap.xml` : home + 11 pages (12 `<loc>`), 0 page de redirection | OK |
| 5 | `robots.txt` avec `Sitemap: https://koulenga.com/sitemap.xml` | OK |
| 5 | RSS `/fr/index.xml` : 11 items (pages, hors home/redirections) | OK |
| 5 | 404 à la racine (`public/404.html` copiée de `public/fr/404.html`) + contenu réel | OK |
| 6 | JSON-LD home : `application/ld+json`, JSON valide, type `NGO` | OK |
| 6 | Pages intérieures : 2 scripts JSON-LD (NGO + BreadcrumbList) | OK |
| 7 | Médias : 15 URLs sondées servies (bundles, headless `sections/news`, `sections/photos`, PDF) | OK — 15/15 |
| 8 | Menu : 12 entrées, ordre attendu, aucun doublon | OK |
| 9 | `static/admin/` : aucune valeur de secret | OK |

## 4. CI — `.github/workflows/deploy.yml` (créé)

Workflow **GitHub Pages** conforme au modèle officiel actuel de la doc Hugo (gohugo.io « Deploy to GitHub Pages », consultée le 02/11/2026) :
`actions/checkout@v7` (submodules, full history) → `actions/configure-pages@v6` → **Hugo extended 0.169.0 épinglé par tarball** + **Dart Sass 1.106.1 épinglé** → build `--gc --minify --printPathWarnings --printI18nWarnings --logLevel info --baseURL <pages>` → **copie `public/fr/404.html` → `public/404.html`** → **QA bloquante** (`python3 scripts/qa_checks.py`, exit 1 ⇒ pas de déploiement) → `upload-pages-artifact@v5` → job `deploy` avec `actions/deploy-pages@v5`.
`permissions: contents: read, pages: write, id-token: write` · `concurrency: pages` sans annulation · **aucun `continue-on-error`** · déclenché sur `push` → `master` + manuel.

## 5. Restes & risques (à traiter avant/après bascule)

| # | Reste | Réf. plan |
|---|---|---|
| R1 | `og:image` 1200×630 absente (`params.ogImage` resté en commentaire dans `hugo.toml`) — obligatoire avant bascule | A13 |
| R2 | Contraste charte non corrigé (`#bf5f2c` 4,30:1 et `#f7fb05`/`#996a51` 4,14:1 échouent AA texte normal) ; corrections ou usage « large text » assumé à décider | R13/§6.4 |
| R3 | Placeholder Sveltia : `backend.base_url` (`sveltia-cms-auth.<sous-domaine>.workers.dev`) + décision galerie (`sections/photos`) à trancher | §8 |
| R4 | `/` → `/fr/` est un meta-refresh Hugo (pas une 301) ; `/fr/association`, `/fr/actions` : meta-refresh/alias (pas des 301 serveur) — acceptable sur GitHub Pages, 301 exactes recommandées si nginx | §5.2 |
| R5 | Images non optimisées (~67 Mo, noms avec espaces/accents conservés volontairement) ; phase 7 SCSS/Dart Sass + WebP home à faire | R6/§6.2 |
| R6 | Non automatisable ici : `htmltest` (règle `_blank`), validation W3C, captures desktop/mobile 375 px, relecture humaine des 13 textes, soumission Search Console | §10.2 |
| R7 | GitHub Pages : paramétrage à faire côté GitHub (Source = GitHub Actions, domaine `koulenga.com` via `CNAME` déjà posé, « Enforce HTTPS ») | §10.3-A |

*Réexécutable : `cd koulenga-hugo && hugo --gc --minify --printPathWarnings --printI18nWarnings --logLevel info && cp public/fr/404.html public/404.html && python3 scripts/qa_checks.py` (exit 0 attendu ; en CI via `KOULENGA_PUBLIC`/`KOULENGA_BASE`).*