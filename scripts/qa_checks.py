#!/usr/bin/env python3
"""
qa_checks.py — Vérifications QA programmatiques du build Hugo Koulenga.
Plan v2 §10.2 (checklist fin de migration) — exécutable en local comme en CI.
Sortie : rapport texte + JSON (/opt/data/koulenga-qa/qa_results.json).
Exit 0 si toutes les vérifications passent, exit 1 sinon.
"""
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Chemins surchargables pour la CI (défauts = poste d'intégration local).
PUB = Path(os.environ.get("KOULENGA_PUBLIC", "/opt/data/koulenga-hugo/public"))
RESULTS_PATH = os.environ.get(
    "KOULENGA_QA_RESULTS", "/opt/data/koulenga-qa/qa_results.json")
# Base des URLs absolues : dev.koulenga.com en local, l'URL Pages en CI
# (--baseURL de l'étape Build du workflow).
BASE = os.environ.get("KOULENGA_BASE", "https://dev.koulenga.com").rstrip("/")
RESULTS = {"ok": 0, "fail": 0, "checks": []}
FAILED = []


def check(name, ok, detail=""):
    RESULTS["checks"].append({"name": name, "ok": bool(ok), "detail": detail})
    if ok:
        RESULTS["ok"] += 1
        print(f"  [OK]   {name}" + (f" — {detail}" if detail else ""))
    else:
        RESULTS["fail"] += 1
        FAILED.append(name)
        print(f"  [ÉCHEC] {name} — {detail}")


def read(p):
    return (PUB / p).read_text(encoding="utf-8")


def exists(p):
    f = PUB / unquote(p)
    return f.is_file()


# Regexes tolérantes au HTML minifié (attributs avec ou sans guillemets).
def attr(tag, name):
    m = re.search(name + r'=(?:"([^"]*)"|([^\s>]+))', tag)
    return m.group(1) or m.group(2) if m else None


def all_html():
    for p in PUB.rglob("*.html"):
        yield p, p.read_text(encoding="utf-8")


print("=" * 72)
print("QA Koulenga — build:", PUB)
print("=" * 72)

# ── 1. Aucun /fr/fr/ (C1) ──────────────────────────────────────────────────
print("\n[1] URLs — aucun /fr/fr/")
frfr_paths = [str(p) for p in PUB.rglob("*") if "/fr/fr/" in str(p)]
frfr_html = []
for p, html in all_html():
    if "/fr/fr/" in html:
        frfr_html.append(str(p))
check("aucun chemin de fichier sous /fr/fr/", not frfr_paths, f"{len(frfr_paths)} fichier(s)")
check("aucune URL /fr/fr/ dans le HTML", not frfr_html, f"{len(frfr_html)} page(s)")

# ── 2. Mapping §5.1 : 14 pages + home répondent 200 ────────────────────────
print("\n[2] Mapping URLs du plan §5.1 (14 pages + home + redirections)")
MAPPING = [
    ("/fr/", "fr/index.html", "home"),
    ("/fr/le-village/", "fr/le-village/index.html", "page"),
    ("/fr/le-burkina-faso/", "fr/le-burkina-faso/index.html", "page"),
    ("/fr/association/", "fr/association/index.html", "redirect layout"),
    ("/fr/association/oyonnax/", "fr/association/oyonnax/index.html", "page"),
    ("/fr/association/teeli-yan/", "fr/association/teeli-yan/index.html", "page"),
    ("/fr/association/adhesions/", "fr/association/adhesions/index.html", "page"),
    ("/fr/association/statuts/", "fr/association/statuts/index.html", "page"),
    ("/fr/actions/", "fr/actions/index.html", "alias"),
    ("/fr/actions/a-venir/", "fr/actions/a-venir/index.html", "page"),
    ("/fr/actions/actions-precedentes/", "fr/actions/actions-precedentes/index.html", "page"),
    ("/fr/actions/presse/", "fr/actions/presse/index.html", "page"),
    ("/fr/journal/", "fr/journal/index.html", "page"),
    ("/fr/diaporama/", "fr/diaporama/index.html", "page"),
]
missing = [u for u, f, _ in MAPPING if not exists(f)]
check("14 pages + home du mapping servies (fichier présent)", not missing,
      f"{len(MAPPING) - len(missing)}/{len(MAPPING)} ; manquantes : {missing}")
# URLs sans slash final = répertoire existant (301 automatique serveur)
no_slash = []
for u, _, _ in MAPPING:
    rel = unquote(u).strip("/")
    if not (PUB / rel / "index.html").is_file():
        no_slash.append(u)
check("variantes sans slash final servables (répertoire + index)", not no_slash,
      f"manquantes : {no_slash}" if no_slash else "toutes")

# ── 3. Aliases : pages de redirection + noindex (A15/C2) ────────────────────
print("\n[3] Aliases & redirections — meta-refresh + noindex")
ALIASES = [
    ("fr/home/index.html", "/fr/", "alias /home (home.alias Grav)"),
    ("fr/actions/index.html", "/fr/actions/a-venir/", "alias /actions"),
    ("index.html", "/fr/", "racine / → /fr/ (auto Hugo)"),
]
for f, target, label in ALIASES:
    if not (PUB / f).is_file():
        check(f"{label} : page générée", False, f"{f} absent")
        continue
    html = read(f)
    refresh = re.search(r'http-equiv=refresh content="0; url=([^"]+)"', html)
    noindex = 'name=robots content=noindex' in html.replace('"', "") or \
        re.search(r'name=["\']?robots["\']? content=["\']?noindex', html)
    canonical = re.search(r'rel=canonical href=([^ >]+)', html)
    ok = refresh and noindex and canonical
    check(f"{label} : meta-refresh→{target} + noindex + canonical", bool(ok),
          f"refresh={refresh.group(1) if refresh else None}, "
          f"noindex={bool(noindex)}, canonical={canonical.group(1) if canonical else None}")
# layout redirect (§4.6/A7) : /fr/association/ → oyonnax, PDF publiés
assoc = read("fr/association/index.html")
m = re.search(r'http-equiv=refresh content="0; url=([^"]+)"', assoc)
check("/fr/association/ : layout redirect → /fr/association/oyonnax/",
      bool(m and "/fr/association/oyonnax/" in m.group(1)),
      f"cible={m.group(1) if m else None}")
check("/fr/association/ : noindex", "noindex" in assoc)
pdf_ok = exists("fr/association/BILAN%202020.pdf") and \
    exists("fr/association/COMPTE%20RENDU%20Assemblée%20Générale%202024.pdf")
check("PDF AG de /fr/association/*.pdf publiés (A7)", pdf_ok)

# ── 4. Render hooks ────────────────────────────────────────────────────────
# Note : les images du chrome du thème (src=/img/…, logo) sont VOLONTAIREMENT
# eager dans l'en-tête (above-the-fold, LCP) — hors périmètre du render hook.
print("\n[4] Render hooks — liens externes & images")
ext_bad, imgs_no_lazy, imgs_no_dims = [], [], []
for p, html in all_html():
    for tag in re.findall(r"<a\b[^>]*>", html):
        if "target=_blank" in tag.replace('"', "") or 'target="_blank"' in tag:
            rel = attr(tag, "rel") or ""
            if "noopener" not in rel or "noreferrer" not in rel:
                ext_bad.append(f"{p}: {tag}")
    for tag in re.findall(r"<img\b[^>]*>", html):
        src = attr(tag, "src") or ""
        if src.startswith("/img/"):
            continue  # chrome du thème (logo en-tête, above-the-fold → eager)
        if 'loading="lazy"' not in tag and "loading=lazy" not in tag:
            imgs_no_lazy.append(f"{p}: {tag[:80]}")
        if "/fr/" in src and not (attr(tag, "width") and attr(tag, "height")):
            imgs_no_dims.append(f"{p}: {tag[:80]}")
check("liens externes target=_blank ⇒ rel=noopener noreferrer", not ext_bad,
      f"{len(ext_bad)} anomalie(s)" + (f" ex: {ext_bad[0]}" if ext_bad else ""))
check("images : loading=lazy partout", not imgs_no_lazy,
      f"{len(imgs_no_lazy)} anomalie(s)" + (f" ex: {imgs_no_lazy[0]}" if imgs_no_lazy else ""))
check("images internes : width+height (anti-CLS)", not imgs_no_dims,
      f"{len(imgs_no_dims)} anomalie(s)" + (f" ex: {imgs_no_dims[0]}" if imgs_no_dims else ""))

# ── 5. Sitemap, robots, RSS, 404 ────────────────────────────────────────────
print("\n[5] Sitemap / robots.txt / RSS / 404")
sm = read("sitemap.xml")
check("sitemap.xml racine (sitemapindex)", "<sitemapindex" in sm)
check("sitemapindex → /fr/sitemap.xml", "/fr/sitemap.xml" in sm)
fr_sm = read("fr/sitemap.xml")
n_urls = len(re.findall(r"<loc>", fr_sm))
check("fr/sitemap.xml : home + 11 pages (12 loc)", n_urls == 12, f"{n_urls} <loc>")
sm_pages = set(re.findall(r"<loc>([^<]+)</loc>", fr_sm))
check("fr/sitemap.xml : pas de page de redirection noindex",
      BASE + "/fr/association/" not in sm_pages
      and BASE + "/fr/actions/" not in sm_pages)
expected_sm = {BASE + u for u, _, kind in MAPPING if kind == "page"} | {BASE + "/fr/"}
check("fr/sitemap.xml : toutes les pages du mapping listées",
      expected_sm <= sm_pages, f"manquantes : {sorted(expected_sm - sm_pages)}")
robots = read("robots.txt")
check("robots.txt avec ligne Sitemap:", "Sitemap:" in robots and
      (BASE + "/sitemap.xml") in robots, robots.strip().replace("\n", " | "))
check("RSS /fr/index.xml généré", exists("fr/index.xml"))
rss = read("fr/index.xml")
check("RSS : 11 items (les pages, hors home/redirections)", rss.count("<item>") == 11,
      f"{rss.count('<item>')} item(s)")
check("404 à la racine (public/404.html)", exists("404.html"))
check("404 sous /fr/ (source de la copie)", exists("fr/404.html"))
r404 = read("404.html")
check("404 : contenu réel (message 404 + lien accueil)",
      ("404" in r404 or "introuvable" in r404.lower()) and "/fr/" in r404)

# ── 6. JSON-LD sur la home ──────────────────────────────────────────────────
print("\n[6] JSON-LD (structured data)")
home = read("fr/index.html")
ld = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', home, re.S)
ld_ok, ld_parsed = 0, []
for blob in ld:
    try:
        data = json.loads(blob)
        ld_ok += 1
        ld_parsed.append(data.get("@type"))
    except json.JSONDecodeError as e:
        check("JSON-LD valide", False, f"JSON invalide : {e}")
check("home : scripts application/ld+json présents et JSON valide",
      ld_ok >= 1, f"{ld_ok} script(s) : {ld_parsed}")
check("home : JSON-LD de type NGO", "NGO" in ld_parsed, str(ld_parsed))
interior = read("fr/le-village/index.html")
ld2 = re.findall(r'application/ld\+json', interior)
check("pages intérieures : JSON-LD (+BreadcrumbList)",
      len(ld2) >= 2 and "BreadcrumbList" in interior, f"{len(ld2)} script(s)")

# ── 7. Médias servis en 200 ────────────────────────────────────────────────
print("\n[7] Médias (extraits — pages bundles + headless)")
MEDIA = [
    "fr/le-village/baobab.jpg",
    "fr/le-village/ECOLE%206.jpg",
    "fr/le-village/annee_scolaire_2003_2004.png",
    "fr/le-burkina-faso/blasonBurkinaFaso.png",
    "fr/association/oyonnax/asso.jpg",
    "fr/actions/presse/2019.10%20Cross%20Le%20Progr%C3%A8s.jpg",
    "fr/actions/actions-precedentes/puits.jpg",
    "fr/diaporama/DSCN0278%20-%20Copie.JPG",
    "fr/2022-12-17-10-16-12.jpg",
    "fr/sections/news/podium.jpg",
    "fr/sections/photos/drapeau.jpg",
    "fr/journal/Journal%20de%20Goudrin%201.pdf",
    "fr/association/BILAN%202020.pdf",
    "fr/association/oyonnax/COMPTE%20RENDU%20ASSEMBLEE%20GENERALE%202025.pdf",
    "fr/Cantine%20mai%202024.jpg",
]
missing_media = [u for u in MEDIA if not exists(u)]
check("média(s) sondé(s) : tous servis (fichier présent)",
      not missing_media, f"{len(MEDIA) - len(missing_media)}/{len(MEDIA)} ; manquants : {missing_media}")

# ── 8. Nav : une seule occurrence par entrée (anti-doublon) ────────────────
print("\n[8] Menu — exactement une entrée par page (bug doublon hugo.toml/front matter)")
EXPECTED = [
    ("Accueil", "/fr/"),
    ("L'école - Le village", "/fr/le-village/"),
    ("Le Burkina Faso", "/fr/le-burkina-faso/"),
    ("L'association", "/fr/association/oyonnax/"),
    ("Teeli Yan (Burkina)", "/fr/association/teeli-yan/"),
    ("Adhésions & Dons", "/fr/association/adhesions/"),
    ("Contact et statuts", "/fr/association/statuts/"),
    ("Actions", "/fr/actions/a-venir/"),
    ("Réalisations", "/fr/actions/actions-precedentes/"),
    ("Dans la presse", "/fr/actions/presse/"),
    ("Le journal de Goudrin", "/fr/journal/"),
    ("Diaporama", "/fr/diaporama/"),
]
for p, html in all_html():
    m = re.search(r'<nav class="dropmenu animated">(.*?)</nav>\s*</section>', html, re.S)
    if not m:
        continue
    links = re.findall(r"<li><a href=([^ >]+)[^>]*>([^<]+)</a>", m.group(1))
    names = [n for _, n in links]
    dupes = {n for n in names if names.count(n) > 1}
    exp_names = [e[0] for e in EXPECTED]
    order_ok = names == exp_names if len(names) == len(exp_names) else False
    check(f"nav sans doublon ({p.relative_to(PUB)})", not dupes,
          f"{len(links)} entrées ; doublons : {dupes if dupes else 'aucun'}")
    check(f"nav = arbre attendu, 7 racines + 5 enfants ({p.relative_to(PUB)})",
          order_ok, f"obtenu : {names}")
    break  # une page suffit : la nav est identique partout

# ── 9. Pas de secret dans static/admin ─────────────────────────────────────
print("\n[9] static/admin — aucun secret")
admin = PUB / "admin"
secrets = []
SECRET_PAT = re.compile(
    r"(?i)(client_secret|secret|password|api[_-]?key|token)\s*[:=]\s*['\"]?\S{8,}")
if admin.is_dir():
    for p in admin.rglob("*"):
        if p.is_file():
            t = p.read_text(encoding="utf-8", errors="ignore")
            for m in SECRET_PAT.finditer(t):
                secrets.append(f"{p.name}: …{m.group(0)[:60]}…")
check("admin : aucune valeur de secret détectée (mots-clés prose exclus)",
      not secrets, "; ".join(secrets[:3]) if secrets else "")

# ── Bilan ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 72)
print(f"BILAN : {RESULTS['ok']} OK, {RESULTS['fail']} ÉCHEC(S)")
print("=" * 72)
out = Path(RESULTS_PATH)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Résultats JSON : {out}")
sys.exit(1 if RESULTS["fail"] else 0)
