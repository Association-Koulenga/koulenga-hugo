# Rapport de migration du contenu — Grav → Hugo (`content/fr/`)

> Mission : création de `/opt/data/koulenga-hugo/content/fr/**` selon le **plan v2 du
> 02/11/2026** (§2 inventaire, §4 contenu, §4.4 home modulaire, §4.6 cas particuliers,
> §5 URLs, §8.6 mapping des 18 pages). Périmètre respecté : **seuls `content/` et ce
> rapport ont été écrits** — `hugo.toml`, `themes/` et `static/` n'ont pas été touchés.
>
> Vérifié par **build réel Hugo v0.169.0+extended** (linux/arm64) : 17 pages, 140
> « non-page files », 3 alias, **0 avertissement de chemin**, **0 `/fr/fr/`**, et
> **101 URLs relatives du HTML rendu contrôlées → 0 non résolue**.

---

## 1. Résumé exécutif

| Élément | Résultat |
|---|---|
| Fichiers `.md` Grav migrés | **17 des 18** (le module vide `_gallery` n'est pas migré, cf. §6) |
| Pages publiques créées | **14** (home `_index.md` + 13 pages, URLs §5.1 du plan) |
| Pages headless créées | **4** (`sections/_index.md`, `sections/news/`, `sections/photos/`, `actions/_index.md`) |
| Médias copiés | **142 fichiers** dans les bundles (les 140 du dépôt Grav, tous préservés — noms d'origine, espaces/accents compris — + copies de service, cf. §3) |
| Correctifs de contenu appliqués | **15** (liens morts supprimés/réparés, markdown dégradé corrigé — journalisés §5) |
| Liens cassés restants dans le contenu | **0** (vérifié par script + build) |
| Build de contrôle | **OK sur le site complet réel** (hugo.toml + thèmes/koulenga + content/) : **701 URLs relatives du HTML rendu → 0 non résolue**, redirection A7 exacte, parité des colonnes et du bloc photos avec la production (§7) |

---

## 2. Pages créées (mapping Grav → Hugo)

| # | Source Grav | Cible Hugo | Notes |
|---|---|---|---|
| 1 | `01.home/modular.md` + `_banner/hero.fr.md` | `content/fr/_index.md` | home modulaire : corps propre de la home (§2.6.1 du plan) + `params.hero_text` (appel aux dons HelloAsso) + `params.home.heroImages` + `params.banner_images` |
| 2 | `02.le-village/columns.fr.md` | `content/fr/le-village/index.md` | `layout: columns` (découpage `<hr>` côté thème, C3) |
| 3 | `03.le-burkina-faso/columns.fr.md` | `content/fr/le-burkina-faso/index.md` | `layout: columns` |
| 4 | `04.association/default.fr.md` | `content/fr/association/_index.md` | **décision A7-a** (§4.6) : page **rendue** avec `layout: redirect` + `params.redirect: "/fr/association/oyonnax/"` — les 5 PDF d'AG restent publiés sous `/fr/association/` (vérifié : `public/fr/association/*.pdf`) |
| 5 | `04.association/01.oyonnax/columns.fr.md` | `content/fr/association/oyonnax/index.md` | porte l'entrée de menu « L'association » (le menu pointe oyonnax, pas la page de redirection — §6.1 du plan) |
| 6 | `04.association/02.teeli-yan/columns.fr.md` | `content/fr/association/teeli-yan/index.md` | `layout: columns` |
| 7 | `04.association/03.adhesions/columns.fr.md` | `content/fr/association/adhesions/index.md` | `layout: columns` |
| 8 | `04.association/04.statuts/default.fr.md` | `content/fr/association/statuts/index.md` | front matter Grav `content: @self.children` sans effet (pas d'enfants) → ignoré, page simple |
| 9 | `05.actions/default.fr.md` | `content/fr/actions/_index.md` | page Grav de **redirection pure** (sans titre ni contenu) → en Hugo : page **non rendue** (`build: {render: false, list: never}`) ; la redirection `/fr/actions/` est assurée par l'**alias `/actions` sur `a-venir`** (vérifié : `public/fr/actions/index.html` = meta-refresh vers `/fr/actions/a-venir/`) |
| 10 | `05.actions/01.a-venir/default.fr.md` | `content/fr/actions/a-venir/index.md` | porte l'entrée de menu « Actions » + `aliases: ["/actions"]` |
| 11 | `05.actions/02.actions-precedentes/columns.fr.md` | `content/fr/actions/actions-precedentes/index.md` | `layout: columns` |
| 12 | `05.actions/03.presse/default.fr.md` | `content/fr/actions/presse/index.md` | front matter collection sans effet → ignoré, page simple |
| 13 | `06.journal/default.fr.md` | `content/fr/journal/index.md` | 13 PDF |
| 14 | `07.diaporama/default.fr.md` | `content/fr/diaporama/index.md` | 13 images |
| — | `01.home/_news/text.fr.md` | `content/fr/sections/news/index.md` | **page headless** (`build: {render: false, list: never, publishResources: true}`) rendue par le partial d'accueil ; médias publiés sous `/fr/sections/news/` (vérifié) |
| — | `01.home/_photo/image.fr.md` | `content/fr/sections/photos/index.md` | **page headless** idem (title « Cross », `date: 2024-04-07T16:01:00+02:00` issue du `publish_date` Grav, `image_align: right`) |
| — | *(nouveau, sans équivalent Grav)* | `content/fr/sections/_index.md` | headless — **empêche la page publique parasite `/fr/sections/`** que Hugo crée sinon automatiquement (constaté par build réel) |
| — | `01.home/_gallery/text.fr.md` | *(non migré)* | module **vide** (titre sans contenu) — « à trancher avec l'association » (§4.6) ; si conservé : créer `sections/galerie.md` headless sur ce modèle |

Les sections headless sont atteignables côté thème via `site.GetPage "sections/news"` /
`site.GetPage "sections/photos"` (vérifié par build : `.Content` et `.Resources`
accessibles, `RelPermalink` vide, ressources **publiées** grâce à `publishResources: true`).

## 3. Médias copiés (142 fichiers)

Copie brute **sans renommage** (§4.3 du plan : noms d'origine conservés, y compris
espaces et accents — « `Départ d'un groupe.JPG` », « `Journal de Goudrin N°9.pdf` »…) :

| Bundle | Médias |
|---|---|
| `content/fr/` (home) | 23 (4 fichiers propres de `01.home` + 18 du bandeau `_banner` + 4 du bloc photos `_photo`, doublons de noms fusionnés) |
| `le-village/` | 18 |
| `le-burkina-faso/` | 3 |
| `association/` | 5 (PDF d'AG — publiés sous `/fr/association/`, décision A7) |
| `association/oyonnax/` | 10 (9 du dossier Grav + 1 copie du PDF AG 2018, cf. §5) |
| `association/teeli-yan/` | 3 |
| `association/adhesions/` | 1 |
| `association/statuts/` | 3 |
| `actions/a-venir/` | 5 |
| `actions/actions-precedentes/` | 10 |
| `actions/presse/` | 16 |
| `journal/` | 13 |
| `diaporama/` | 13 |
| `sections/news/` | 15 |
| `sections/photos/` | 4 |
| **Total** | **142** (104 `.jpg` + 2 `.jpeg` + 6 `.png` + 30 `.pdf`) |

Détail des comptes (vérifiés sur disque) : **104 jpg + 2 jpeg + 6 png + 30 pdf = 142**.
Le dépôt Grav contient 140 médias, **tous préservés** ; « `2022-12-17-10-20-18
6.jpg` » y figure 3 fois (`01.home`, `_banner`, `_photo`, octets identiques
vérifiés) et est copié 2 fois (bundle home + bundle photos). **3 copies
supplémentaires** sont posées, chacune pour un contract explicite : le PDF
« `COMPTE RENDU AG 2018.pdf` » dans `association/oyonnax/` (réparation du lien,
§5.5) et « `drapeau.jpg` » + « `koulenga.jpg` » dans le bundle home (le
`partials/images-block.html` du thème résout `params.photo_images` **contre les
ressources du bundle home** — les 2 autres images du bloc y sont déjà présentes
via `_banner`).

## 4. Conventions de front matter appliquées

- **`title`** : repris tel quel (les `''` d'échappement Grav convertis en apostrophes).
- **`date`** : seule page datée → `_photo` (`publish_date: 2024-04-07 16:01`, heure de
  Paris) devient `date: 2024-04-07T16:01:00+02:00` sur `sections/photos/`.
- **`weight`** = ancien ordre Grav × 10 : rubriques 10 → 70 (`home` 10, `le-village` 20,
  `le-burkina-faso` 30, `association` 40, `actions` 50, `journal` 60, `diaporama` 70) ;
  sous-pages 10/20/30/40 dans leur rubrique.
- **`menu`** : déclaré **en front matter** (page bundles), arbre fidèle au menu de
  production : Accueil (10) → L'école - Le village (20) → Le Burkina Faso (30) →
  **L'association → oyonnax (40)** avec enfants teeli-yan (20), adhesions (30),
  statuts (40) → **Actions → a-venir (50)** avec enfants Réalisations (20),
  Dans la presse (30) → Le journal de Goudrin (60) → Diaporama (70).
  ⚠️ **hugo.toml ne doit PAS re-déclarer `[[menus.main]]`** (doublons d'entrées sinon).
- **`aliases` SANS préfixe `/fr`** (C2, vérifié par build) : `["/home"]` sur la home,
  `["/actions"]` sur `a-venir`. **Pas d'alias `/association`** : la page
  `/fr/association/` existe comme bundle rendu (A7-a) — un alias sur oyonnax
  entrerait en collision avec elle (chemin dupliqué).
- **`params`** : `media_order` (chaîne Grav d'origine, ordre préservé), `image_align`,
  `body_classes` quand présents. Côté home : `params.home.heroImages` = 1ʳᵉ image du
  `media_order` du `_banner` (`2022-12-17-10-16-12.jpg`) + un fallback
  (`DSCN0285 - Copie.JPG`, 2ᵉ du media_order — §2.6.2/A31 : pas les 18 entrées) ;
  `params.hero_text` (appel aux dons HelloAsso, rendu par
  `$.Page.RenderString` dans `partials/hero.html`) ; `params.banner_images`
  (structure objets `{image: {src, alt}}` → image de fond du hero, lue par
  `partials/hero-image.html`) ; `params.photo_images` (les 4 images du module
  `_photo`, mêmes objets, lues par `partials/images-block.html` **contre les
  ressources du bundle home**, d'où leur copie dans `content/fr/`).
  `params.image_align` de la home = **`right`** : c'est la valeur du module
  `_photo` (bloc photos aligné à droite — vérifié en production : 4 images
  `align-right`), celle du `_banner` (« left ») n'étant utilisée par aucun template.
- **`layout`** : `columns` sur les 6 pages au template Grav « columns »
  (le-village, le-burkina-faso, oyonnax, teeli-yan, adhesions, actions-precedentes) ;
  `redirect` sur `association/_index.md` (contrat thème : `layouts/redirect.html`
  lisant `params.redirect` — meta-refresh 0 s + canonical + noindex, A7-a).
- **`draft`** : aucun brouillon côté Grav → aucune page en brouillon.
- Abandonnés (sans objet en Hugo) : `onpage_menu`, `content: items/@self…` (la home
  modulaire devient partials + pages headless), `redirect:` Grav (remplacé par alias
  ou page de redirection).

## 5. Nettoyage des anomalies (journal complet)

Politique appliquée (§2.5/§4.2 du plan) : **réparer vers une cible qui existe ;
sinon supprimer la référence et la signaler — jamais inventer de cible.**

**Liens réparés (cible existante) :**
1. `association` : `[COMPTE RENDU AG 2021.pdf]` **sans cible** → lien réel vers le PDF
   du même bundle ;
2. `association` : destination « `COMPTE RENDU AG 2024.pdf` » (non accentuée) → fichier
   réel « `COMPTE RENDU Assemblée Générale 2024.pdf` » (accentué) ;
3. `oyonnax` : « `COMPTE RENDU AG 2021.pdf` » et « `BILAN 2020.pdf` » (absents du dossier,
   présents dans le bundle parent `association/`) → liens `../…` réparés ;
4. `oyonnax` : « `COMPTE RENDU AG 2018.pdf` » (présent dans `01.home/_news/`, absent
   d'oyonnax) → **copie du PDF dans le bundle oyonnax**, lien conservé tel quel.

**Références supprimées (fichier introuvable dans TOUT le dépôt Grav) :**
5. `oyonnax` : image `enfants.jpg` ;
6. `oyonnax` : lien `[COMPTE RENDU AG 2017.pdf](…)` (PDF absent de tout le dépôt) ;
7. `oyonnax` : crochet orphelin « `[` » isolé (la ligne `----` qui suit est conservée :
   c'est un séparateur de colonnes que Grav rendait en titre setext H2, cf. §6) ;
8. `actions-precedentes` : image `PHOTO-2021-01-07-11-29-49.jpg` ;
9. `diaporama` : images `IMG-20210309-WA0003.jpg` et `IMG-20210309-WA0004.jpg`
   (« lumière pour le dispensaire » — les WA0005/8/9 existantes sont conservées) ;
10. `presse` : image « `2019.10 Cross St Jo Le Progrès.jpg` » (référencée sous Voix de
    l'Ain 2019, jamais uploadée ; cible ambiguë → supprimée, non devinée).

**Markdown dégradé corrigé :**
11. `news` : ligne `****` orpheline supprimée ;
12. `news` : `**Novembre 2024****` → `**Novembre 2024**` ;
13. `actions-precedentes` : `***Novembre 2024****` → `**Novembre 2024**` ;
14. `oyonnax` : titre `## # L'assemblée générale` → `## L'assemblée générale` ;
15. `a-venir` : point parasite `.![DSCN0912…]` → `![DSCN0912…]`.

**Textes alternatifs** : les `%20`/`%C3%A9` des **alt/title** (textes visibles, rendus
nus à l'écran et aux lecteurs d'écran) sont décodés (ex. alt
`DSCN0567%20-%20Copie` → `DSCN0567 - Copie`). Les **destinations** restent URL-encodées
telles dans Grav : c'est du Markdown valide et la résolution est identique (les liens
externes `http(s):`/`mailto:` ne sont pas touchés).

## 6. Points à connaître / décisions documentées

- **Schéma d'URL des médias (constat production)** : Grav sert les images Markdown via
  `/user/pages/<dossier>/<fichier>` (vérifié : `koulenga.com/user/pages/02.le-village/baobab.jpg`
  → 200) et **non** `/fr/<page>/<fichier>` (404). Les page bundles Hugo servent donc les
  images sous une **nouvelle** URL propre `/fr/<slug>/<fichier>` — les hotlinks vers
  `/user/pages/…` casseront (risque R2 du plan, inévitable dans cette architecture).
  En revanche les **liens vers les PDF** étaient déjà servis par Grav en
  `/fr/<page>/<fichier>` (vérifié en production) : **parité d'URLs exacte** pour les
  29 PDF (AG, statuts, journaux, « Nouvelles de Goudrin »).
- **Découpage en colonnes** : le template Grav consomme les `<hr>` (les colonnes
  n'apparaissent pas dans le HTML final). Parité vérifiée page par page
  (colonnes Grav = segments `<hr>`+1 Hugo) : le-village 2/2, le-burkina-faso 2/2,
  teeli-yan 2/2, oyonnax 1/1, adhesions 1/1, actions-precedentes 1/1.
- **`----` dans oyonnax** : collé à la ligne de texte précédente, Grav le rend en
  **titre setext H2** (visible en production : `<h2>…[…</h2>`), pas en `<hr>` — le
  markdown est conservé tel quel, Goldmark produit le même rendu.
- **`_gallery` non migré** (module vide — « à trancher avec l'association », §4.6).
  Squelette prêt à l'emploi : `sections/galerie.md` headless sur le modèle de
  `sections/photos/`.
- **Images sans `alt`** (inventaire A19, à compléter lors de la relecture humaine) :
  **44** (`le-village` 10, `le-burkina-faso` 3, `oyonnax` 2, `teeli-yan` 2,
  `a-venir` 2, `actions-precedentes` 7, `presse` 15, `diaporama` 3).
- **Anomalie conservée volontairement** (hors périmètre « évident », signalée pour la
  relecture) : la presse 2013 de « La voix de l'Ain » affiche l'image
  « `2013.11 Présentation Le Progrès.jpg` » (coupier-coller du bloc « Le Progrès ») ;
  fautes de frappe du contenu laissées telles quelles (« consultés sue », « aux besoin »…).
- **`description` SEO (A11)** : non posée (aucune équivalence Grav ; « ne rien inventer »).
  Le champ est prévu dans `static/admin/config.yml` — à rédiger en relecture.

## 7. Vérifications effectuées (builds réels)

Machine : Hugo **v0.169.0+extended** linux/arm64 (binaire de test dans
`/opt/data/.tools-hugo/`, hors livrable). Deux builds de contrôle :

**(a) config de test minimale** (`/opt/data/.hugo-lab/`, reproduisant l'architecture
cible) puis **(b) build du site complet réel** — `hugo.toml` + `themes/koulenga` +
mon `content/`, sur une **copie** du dépôt (`/opt/data/.hugo-lab/site-copy/`,
aucune pollution du livrable) — **return code 0** :

- **19 pages** rendues, 142 « non-page files », 3 alias, **aucun avertissement de
  chemin** (`--printPathWarnings`), **aucun `/fr/fr/`** ;
- **URLs publiques** (14) : `/fr/`, `/fr/le-village/`, `/fr/le-burkina-faso/`,
  `/fr/association/` (page redirect), `/fr/association/{oyonnax,teeli-yan,adhesions,statuts}/`,
  `/fr/actions/a-venir/`, `/fr/actions/actions-precedentes/`, `/fr/actions/presse/`,
  `/fr/journal/`, `/fr/diaporama/` + 404 rendue ;
- **alias** : `/home` → `/fr/`, `/actions` → `/fr/actions/a-venir/`, `/` → `/fr/`
  (meta-refresh + canonical générés par Hugo) ;
- **redirection A7-a** : `public/fr/association/index.html` émet
  `meta-refresh 0; url=https://koulenga.com/fr/association/oyonnax/` + canonical +
  noindex (via `layouts/redirect.html` du thème et `params.redirect`) ;
  **PDF d'AG publiés** sous `public/fr/association/*.pdf` ;
- **home modulaire** : hero plein écran avec image de fond =
  `/fr/2022-12-17-10-16-12.jpg` (1ʳᵉ image du `media_order` du `_banner` ✓ §2.2.1),
  `hero_text` HelloAsso rendu, contenu propre de la home rendu, bloc photos =
  **4 images `align-right`** (parité production ✓), bloc actualités rendu depuis
  la page headless `sections/news` ;
- **headless** : `sections/news/` et `sections/photos/` non rendues comme pages,
  atteignables par `site.GetPage`, médias **publiés** (15 + 4) ; pas de page
  parasite `/fr/sections/` ;
- **découpage colonnes** (`layouts/columns.html`, `findRE "<hr[^>]*>"`) — parité
  **exacte** avec la production Grav (colonnes comptées dans le HTML des deux
  sites) : le-village **2/2**, le-burkina-faso **2/2**, teeli-yan **2/2**,
  oyonnax **1/1**, adhesions **1/1**, actions-precedentes **1/1** ;
- **liens du rendu final** : **701 URLs relatives** extraites des 18 pages HTML
  construites → **0 non résolue** (images de bundles résolues vers les permaliens
  des ressources, liens `../` vers les PDF du bundle parent OK, médias publiés
  sous leurs noms URL-encodés).

Scripts réexécutables : `/opt/data/.hugo-lab/migrate_koulenga_content.py`
(migration + journal `migration_log.json`), `verify_refs.py` (contrôle des
références), `build_full.py` + `qa_full.py` (build complet et QA), `build_real.py` +
`qa_build.py` (build config de test).

## 8. Actions requises auprès des autres livrables

1. **⚠️ `hugo.toml` — DOUBLON DE MENU (bloquant, constaté par build réel)** : la config
   déclare **7 `[[menus.main]]`** (pageRef) ET mon contenu déclare **les mêmes 7
   entrées en front matter** (avec en plus les enfants `teeli-yan`, `adhesions`,
   `statuts`, `actions-precedentes`, `presse` pour les sous-menus déroulants, comme
   sur le site actuel). Résultat mesuré sur le build complet : **chaque entrée de
   premier niveau apparaît DEUX FOIS** dans la nav (Accueil ×2, Le village ×2, …).
   **Une seule source doit rester.** Recommandation : supprimer les blocs
   `[[menus.main]]` de `hugo.toml` (le front matter porte l'arbre complet avec
   enfants, que la config n'a pas) ; alternative : retirer les clés `menu:` des 13
   pages de `content/fr/` — mais il faudrait alors ajouter les 6 enfants au menu de
   config, sinon les sous-pages deviennent inaccessibles depuis la navigation.
2. **Thème `koulenga`** : contracts vérifiés **compatibles** avec ce contenu —
   `layouts/columns.html` (les 6 pages portent `layout: columns`, découpage
   `<hr>` parité production ✓), `layouts/redirect.html` (lit `params.redirect` :
   rendu vérifié `url=https://koulenga.com/fr/association/oyonnax/` + canonical +
   noindex ✓), `partials/hero-image.html` (`params.banner_images[0].image.src` ✓
   image de fond = 2022-12-17-10-16-12.jpg), `partials/images-block.html`
   (`params.photo_images` + `params.image_align: right` → 4 images align-right,
   parité production ✓), `partials/text-block.html` + `site.GetPage
   "/sections/news"` (actualités rendues ✓). ⚠️ `params.home.heroImages`,
   `params.hero_text` et `params.banner_images` décrivent **le même bandeau**
   (exigence de mission + conventions du thème) : le thème lit `hero_text` +
   `banner_images` — **`params.home.heroImages` est aujourd'hui une donnée
   inerte** (aucun template ne la lit) ; à conserver comme données de référence
   ou à supprimer lors d'une passe de déduplication.
3. **Sveltia (`static/admin/config.yml`)** : l'entrée `actualites` pointe
   `content/fr/sections/news.md` — le contenu réel est le bundle
   **`content/fr/sections/news/index.md`** (médias colocalisés obligatoires pour être
   publiés et résolus, `media_folder: ''` → à côté d'`index.md`) → mettre à jour le
   `file:` de l'entrée. Le bloc photos (`sections/photos/`) n'a **pas d'entrée** dans
   la config actuelle (l'annexe D le prévoyait via `params.photo_images` sur la
   home) : ajouter une entrée `content/fr/sections/photos/index.md` si les éditeurs
   doivent y toucher — sinon l'édition du bloc photos passe par la home
   (`params.photo_images`).
4. **CI/QA** : le test du mapping d'URLs (§10.2) doit couvrir les alias sans slash
   final (`/fr/actions`, `/fr/association`, `/home`), les PDF d'AG sous
   `/fr/association/`, et les médias servis sous leurs noms URL-encodés
   (`/fr/le-village/Jardin%20%C3%A9cole%202024.jpg`).

---
*Migration exécutée le 02/11/2026 depuis le clone Grav (lecture seule, commit du
26/10/2026). Aucun fichier de `hugo.toml`, `themes/` ou `static/` n'a été modifié.*