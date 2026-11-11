# Sveltia CMS — mise en service (site Hugo Koulenga)

> Préparation issue du **plan de migration v2** (02/11/2026), §8 et annexes C à F.
> Ce dossier (`static/admin/`) est copié tel quel par Hugo dans `public/admin/` et
> servi sur **`https://dev.koulenga.com/admin/`**.

## Fichiers de ce dossier

| Fichier             | Rôle                                                                                                                                                                                                                         |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `index.html`        | Page admin (SPA Sveltia CMS chargée depuis le CDN unpkg, **version épinglée** `@sveltia/cms@0.256.1`, `noindex`, pas de stylesheet externe, pas de `type="module"`)                                                          |
| `config.yml`        | Configuration complète : backend GitHub, 5 file collections couvrant les 18 pages, médias colocalisés (`media_folder: ''` / `public_folder: ''` par fichier), workflow éditorial 2 étapes. **PUBLIC — aucun secret dedans.** |
| `README-SVELTIA.md` | Ce document                                                                                                                                                                                                                  |

**Périmètre** : ces 3 fichiers ne touchent ni `hugo.toml`, ni `themes/`, ni `content/`.

## ⚠️ Règle absolue — les secrets ne vont JAMAIS dans le dépôt

Le Client Secret GitHub (et tout autre credential) vit **uniquement en variable
chiffrée du Worker Cloudflare** (bouton *Encrypt*). `config.yml` est public une
fois le site déployé : il ne contient volontairement que `repo`, `branch`,
`base_url` et les collections — aucune donnée sensible (§8.4 du plan).

## URLs configurées

Le site de préproduction et le Worker d'authentification sont configurés dans
`config.yml` :

```yaml
site_url: https://dev.koulenga.com
base_url: https://sveltia-cms-auth.koulenga.workers.dev
```

## Étapes de mise en service

### 1. Déployer le Worker « Sveltia CMS Authenticator » (Cloudflare)

- Compte Cloudflare **gratuit** suffisant. Depuis le dépôt officiel
  `https://github.com/sveltia/sveltia-cms-auth` : bouton « Deploy to Cloudflare
  Workers », ou `git clone … && wrangler deploy`.
- URL configurée : `https://sveltia-cms-auth.koulenga.workers.dev`.

### 2. Créer l'OAuth app GitHub — sous l'organisation Association-Koulenga

*Settings de l'org → Developer settings → OAuth Apps → Register a new OAuth app*
(**pas** depuis un compte personnel, §8.5) :

- Application name : `Koulenga — CMS`
- Homepage URL : `https://dev.koulenga.com`
- **Authorization callback URL :
  `https://sveltia-cms-auth.koulenga.workers.dev/callback`**
- Noter le **Client ID** ; « Generate a new client secret » → copier le
  **Client Secret** (affiché une seule fois) → **directement en variable chiffrée
  du Worker** (étape 3), jamais dans le dépôt.

Flux OAuth attendu : clic « Se connecter avec GitHub » → GitHub (consentement
des scopes) → callback du Worker (`/callback`) → retour navigateur sur
`/admin/` avec le jeton en session. Le Worker sert sa page d'autorisation sur
`<WORKER_URL>/auth`.

### 3. Configurer les variables du Worker (dashboard Cloudflare → Settings → Variables)

| Où | Variable | Valeur | Secret ? |
|---|---|---|---|
| Worker `sveltia-cms-auth` | `GITHUB_CLIENT_ID` | Client ID de l'OAuth app (org Association-Koulenga) | Non (identifiant public), mais à garder dans le Worker |
| Worker `sveltia-cms-auth` | `GITHUB_CLIENT_SECRET` | Client Secret de l'OAuth app | **OUI — variable chiffrée (« Encrypt ») ; JAMAIS dans le dépôt** |
| Worker `sveltia-cms-auth` | `ALLOWED_DOMAINS` | `dev.koulenga.com` | Non — limite les connexions au domaine de préproduction |
| Worker `sveltia-cms-auth` | `GITHUB_HOSTNAME` | *(vide — github.com public ; ne remplir qu'en GitHub Enterprise)* | — |
| Worker `sveltia-cms-auth` | `GITHUB_ALLOW_WORKFLOW_SCOPE` | *(absent/false — ne pas activer, §8.3)* | — |
| GitHub Actions | *(aucune variable nécessaire)* | le `GITHUB_TOKEN` natif suffit pour le build + Pages | — |
| `config.yml` (public) | `backend.base_url` | URL publique du Worker | — |

### 4. Vérifier les URL configurées

Vérifier que `site_url` et `backend.base_url` dans `config.yml` correspondent
aux domaines indiqués ci-dessus.

### 5. Vérifier la version du CMS

`index.html` charge `@sveltia/cms@0.256.1` (épinglée au 02/11/2026). Avant la
bascule : vérifier les release notes sur `https://github.com/sveltia/sveltia-cms/releases`
et mettre à jour **volontairement** si une version plus récente est jugée stable
(le projet est en bêta, §8.9-S1). Ne jamais retirer l'épinglage.

### 6. Tester en local (mainteneur)

Workflow local : `hugo server` → ouvrir `http://localhost:1313/admin/` — le CMS
écrit directement dans le clone local, sans authentification. Tester :
modification d'une page, upload d'une image (vérifier qu'elle atterrit dans le
dossier de la page — colocalisée), upload d'un PDF. Valider aussi le schéma
JSON dans VS Code (lien `yaml-language-server` en tête de `config.yml`).

### 7. Tester la connexion OAuth de bout en bout (préprod)

Déployer sur la préprod (`dev.koulenga.com`), se connecter avec un compte
ayant un accès en **écriture** au dépôt (les comptes en lecture seule sont
refusés à la connexion), et dérouler la boucle complète :
brouillon → revue → publier → build GitHub Actions → en ligne.

## Checklist de mise en place (annexe F du plan — à cocher au lancement)

- [ ] Créer le dépôt `Association-Koulenga/koulenga-hugo` (public, branche `master`) et migrer le contenu selon le plan.
- [ ] Déployer le Worker `sveltia-cms-auth` sur Cloudflare avec l'URL configurée ci-dessus.
- [ ] Créer l'**OAuth app GitHub sous l'org** avec le callback
  `https://sveltia-cms-auth.koulenga.workers.dev/callback` ; copier Client ID / Secret.
- [ ] Renseigner les variables du Worker (tableau ci-dessus) avec le Secret **chiffré**.
- [ ] Vérifier `static/admin/index.html` (version CDN épinglée à jour) et `static/admin/config.yml` ; valider le schéma JSON et tester la **connexion OAuth de bout en bout** sur la préprod.
- [ ] Tester en local (workflow local : `hugo server` → `/admin/`) la modification d'une page, l'upload d'une image (colocalisée) et d'un PDF.
- [ ] Configurer l'équipe GitHub `éditeurs-site` (Write) ; inviter les bénévoles ; activer les restrictions d'apps OAuth de l'org.
- [ ] Protéger `master` (PR obligatoires) — compatible avec le workflow éditorial (§8.8).
- [ ] Vérifier la boucle complète : brouillon → revue → publier → build Actions → en ligne sur `dev.koulenga.com`.
- [ ] Rédiger/imprimer le guide d'une page (§8.8) ; animer la session de formation d'1 h ; prévoir l'accompagnement 2–3 semaines.
- [ ] Mettre à jour le README du dépôt : URL `/admin/`, rôles, procédure de mise à jour de la version du CMS.

## Recette des éditeurs (rappel, §8.7)

1. Aller sur `https://dev.koulenga.com/admin/` → « Se connecter avec GitHub » → autoriser (une fois).
2. Choisir la page dans la liste (ex. *L'association → Adhésions & Dons*).
3. Modifier le texte ; téléverser/choisir une image dans le champ prévu ; renseigner le texte alternatif si demandé.
4. « Enregistrer » → la modification est en **Brouillon** ; « Envoyer en revue » quand c'est prêt.
5. Le relecteur voit la carte dans la colonne « En revue », ouvre, vérifie dans l'aperçu, clique **Publier** → le site est reconstruit automatiquement quelques minutes plus tard.
6. Pour une typo urgente : « Enregistrer et publier » (direct).

## Points de conception à conserver (§8.6-8.9)

- **5 file collections** (accueil, decouverte/Le village & le pays, association, actions, medias/Journal & diaporama) : aucune création/suppression de page par les éditeurs ; les slugs et URLs ne sont pas modifiables depuis le CMS.
- **Médias colocalisés** (`media_folder: ''` + `public_folder: ''` par fichier) : chaque upload atterrit dans le page bundle de la page — les URLs `/fr/<page>/<fichier>` sont préservées.
- `max_file_size: 20 Mo` + `slugify_filename: true` : garde-fous (pas de Git LFS, noms ASCII pour les nouveaux fichiers).
- `params.media_order` (hérité de Grav) est exposé avec un bandeau « ne pas modifier » : l'ordre réel se règle en réordonnant les listes d'images (glisser-déposer).
- `weight` : laisser vide, les menus sont gérés dans `hugo.toml`.
- `publish_mode: editorial_workflow` à 2 étapes (`draft`, `pending_review`) + `direct_publish: true` ; `auth_methods: [oauth]` et `auth_scope: public_repo`.
- Ancres YAML volontairement absentes du `config.yml` : non supportées nativement par Sveltia — les blocs `fields` sont dupliqués.

## Références

- Plan de migration v2 : §8 (Sveltia CMS), annexes C (index.html), D (config.yml), E (variables d'environnement), F (checklist).
- Documentation Sveltia CMS : `https://github.com/sveltia/sveltia-cms/wiki`
- Authenticator officiel : `https://github.com/sveltia/sveltia-cms-auth`
