"""Fabrique le site (dossier site/) à partir de contenu/site.json et gabarit.html.

Lancer : python3 build.py
GitHub (fichier .github/workflows/site.yml) lance ce script tout seul à chaque modification faite depuis /admin.
"""
import hashlib
import json
import re
from datetime import date
from html import escape
from pathlib import Path

RACINE = Path(__file__).parent
SORTIE = RACINE / "site"
URL = "https://olivier-audry.fr"

ICONES = {
    "maison": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "outils": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
    "cle": '<path d="M15 4a5 5 0 0 0-4.6 6.9L3 18.3V21h2.7l.8-.8v-1.9h1.9l1.1-1.1v-1.9h1.9l1.1-1.1A5 5 0 1 0 15 4z"/><circle cx="16" cy="8" r="1"/>',
    "ancien": '<path d="M3 21h18"/><path d="M5 21V9l7-5 7 5v12"/><path d="M9 21v-5a3 3 0 0 1 6 0v5"/><path d="M9 10h6"/>',
    "goutte": '<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z"/>',
    "fenetre": '<path d="M4 20 12 4l8 16z"/><path d="M9.5 13h5v5h-5z"/><path d="M12 13v5M9.5 15.5h5"/>',
    "isolation": '<path d="M3 20h18"/><path d="M4 16c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2"/><path d="M4 11c2 0 2-2 4-2s2 2 4 2 2-2 4-2 2 2 4 2"/>',
    "nettoyage": '<path d="M14 3v6"/><path d="M10 9h8v3h-8z"/><path d="M11 12l-1 9h8l-1-9"/><path d="M4 14h3M3 18h4"/>',
    "calendrier": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="m9 15 2 2 4-4"/>',
    "gouttiere": '<path d="M3 6h16v3H3z"/><path d="M15 9v8a3 3 0 0 0 3 3h3"/><path d="M8 13s-1.5 1.8-1.5 2.8a1.5 1.5 0 0 0 3 0C9.5 14.8 8 13 8 13z"/>',
}


def icone(nom):
    trace = ICONES.get(nom, ICONES["maison"])
    return (
        '<svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" '
        f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{trace}</svg>'
    )


def paragraphes(liste):
    return "\n        ".join(f"<p>{escape(p)}</p>" for p in liste if p.strip())


def bandeau(texte):
    mots = [m.strip() for m in texte.split("•") if m.strip()]
    return '<span class="sep">•</span>'.join(f"<span>{escape(m)}</span>" for m in mots)


def valeur(contenu, chemin):
    for cle in chemin.split("."):
        contenu = contenu[cle]
    return contenu


def remplir(gabarit, contenu, blocs):
    for nom, html in blocs.items():
        gabarit = gabarit.replace("{{" + nom + "}}", html)
    return re.sub(r"\{\{([a-z_0-9.]+)\}\}", lambda m: escape(str(valeur(contenu, m.group(1)))), gabarit)


def page_simple(contenu, titre, corps):
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(titre)} – O. Audry</title>
  <meta name="robots" content="noindex">
  <link rel="icon" href="/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Instrument+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
</head>
<body class="page-simple">
<main class="section">
  <div class="conteneur conteneur-etroit">
    <a href="/" class="logo"><img src="/images/logo.png" alt="O. Audry – Couverture Zinguerie" width="160" height="78"></a>
    <h1>{escape(titre)}</h1>
    {corps}
    <p><a href="/" class="bouton">Retour à l'accueil</a></p>
  </div>
</main>
</body>
</html>
"""


def version_fichiers():
    """Empreinte du CSS et du JS : force les navigateurs à recharger après une modification."""
    h = hashlib.sha1()
    for f in ("css/style.css", "js/main.js"):
        h.update((SORTIE / f).read_bytes())
    return h.hexdigest()[:8]


def taille_jpeg(chemin):
    """Largeur et hauteur d'une photo JPEG (pour éviter que la page « saute » au chargement)."""
    try:
        with open(SORTIE / chemin.lstrip("/"), "rb") as f:
            data = f.read()
    except OSError:
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marqueur = data[i + 1]
        if marqueur in (0xC0, 0xC1, 0xC2):
            return int.from_bytes(data[i + 7:i + 9], "big"), int.from_bytes(data[i + 5:i + 7], "big")
        i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
    return None


def attributs_taille(chemin):
    t = taille_jpeg(chemin)
    return f' width="{t[0]}" height="{t[1]}"' if t else ""


def faq_html(liste):
    return "\n      ".join(
        f'<details class="faq-item"><summary>{escape(q["question"])}</summary><p>{escape(q["reponse"])}</p></details>'
        for q in liste
    )


def faq_schema(liste):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["question"],
             "acceptedAnswer": {"@type": "Answer", "text": q["reponse"]}}
            for q in liste
        ],
    }


def json_ld(donnees):
    return json.dumps(donnees, ensure_ascii=False, indent=2).replace("</", "<\\/")


def donnees_structurees(contenu):
    """Fiche entreprise lisible par Google (schema.org) : nom, adresse, prestations..."""
    s = contenu["societe"]
    rue, cp_ville = [x.strip() for x in s["adresse"].split(",")[:2]]
    cp, ville = cp_ville.split(" ", 1)
    fiche = {
        "@context": "https://schema.org",
        "@type": "RoofingContractor",
        "@id": URL + "/#entreprise",
        "name": "O. Audry – Couverture Zinguerie",
        "legalName": s["nom"],
        "description": contenu["seo"]["description"],
        "url": URL + "/",
        "logo": URL + "/images/logo.png",
        "image": URL + contenu["accueil"]["image"],
        "email": contenu["contact"]["email"],
        "vatID": s["tva"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": rue,
            "postalCode": cp,
            "addressLocality": ville,
            "addressRegion": "Centre-Val de Loire",
            "addressCountry": "FR",
        },
        "areaServed": [{
            "@type": "GeoCircle",
            "geoMidpoint": {"@type": "GeoCoordinates", "latitude": contenu["zone"]["centre"][0],
                            "longitude": contenu["zone"]["centre"][1]},
            "geoRadius": int(float(contenu["zone"]["rayon_km"]) * 1000),
        }] + [{"@type": "City", "name": c} for c in contenu["zone"]["communes"] if c.strip()],
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": p["titre"], "description": p["texte"]}}
            for p in contenu["prestations"]["liste"]
        ],
    }
    tel = contenu["contact"].get("telephone", "").strip()
    if tel:
        fiche["telephone"] = tel
    fiche["geo"] = {"@type": "GeoCoordinates", "latitude": contenu["zone"]["centre"][0],
                    "longitude": contenu["zone"]["centre"][1]}
    del fiche["@context"]
    return json_ld({"@context": "https://schema.org", "@graph": [fiche, faq_schema(contenu["faq"]["liste"])]})


def pages_ville(contenu, v, prestations):
    """Page « Couvreur à <ville> » : texte propre à la ville, prestations, photos, FAQ. Renvoie son adresse."""
    gabarit = (RACINE / "gabarit-ville.html").read_text(encoding="utf-8")
    url_page = f"{URL}/{v['slug']}/"
    tel = contenu["contact"].get("telephone", "").strip()
    entreprise = {"@id": URL + "/#entreprise"}
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Service", "name": f"Couvreur à {v['ville']}", "serviceType": "Couverture et zinguerie",
         "url": url_page, "provider": entreprise, "areaServed": {"@type": "City", "name": v["ville"]},
         "description": v["description_seo"]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": URL + "/"},
            {"@type": "ListItem", "position": 2, "name": v["h1"], "item": url_page}]},
        faq_schema(v["faq"]),
    ]}
    titres = {r["image"]: r["titre"] for r in contenu["realisations"]["liste"]}
    photos = "\n        ".join(
        f'<li><figure><img src="{escape(ph)}" alt="{escape(titres.get(ph, "Toiture réalisée par O. Audry"))}"'
        f'{attributs_taille(ph)} loading="lazy"><figcaption>{escape(titres.get(ph, ""))}</figcaption></figure></li>'
        for ph in v["photos"])
    html = remplir(gabarit, contenu, {
        "TITRE_SEO": escape(v["titre_seo"]),
        "DESCRIPTION_SEO": escape(v["description_seo"]),
        "URL_PAGE": url_page,
        "IMAGE": escape(v["photos"][0] if v["photos"] else contenu["accueil"]["image"]),
        "H1": escape(v["h1"]),
        "SOUS_TITRE": escape(v["sous_titre"]),
        "VILLE": escape(v["ville"]),
        "PARAGRAPHES": paragraphes(v["paragraphes"]),
        "PRESTATIONS": prestations,
        "PHOTOS": photos,
        "FAQ": faq_html(v["faq"]),
        "BOUTON_TEL": (f'<a href="tel:{escape(tel.replace(" ", ""))}" class="bouton">Appeler le {escape(tel)}</a>'
                       if tel else ""),
        "ANNEE": escape(contenu["societe"]["annee"]),
        "DONNEES_STRUCTUREES": json_ld(schema),
        "URL": URL,
        "VERSION": version_fichiers(),
    })
    dossier = SORTIE / v["slug"]
    dossier.mkdir(exist_ok=True)
    (dossier / "index.html").write_text(html, encoding="utf-8")
    return url_page


def construire():
    contenu = json.loads((RACINE / "contenu" / "site.json").read_text(encoding="utf-8"))
    gabarit = (RACINE / "gabarit.html").read_text(encoding="utf-8")

    prestations = "\n        ".join(
        f'<li>{icone(p.get("icone"))}<div><h3>{escape(p["titre"])}</h3><p>{escape(p["texte"])}</p></div></li>'
        for p in contenu["prestations"]["liste"]
    )
    realisations = "\n          ".join(
        f'<li><figure tabindex="0"><img src="{escape(r["image"])}" alt="{escape(r["titre"])}"{attributs_taille(r["image"])} loading="lazy">'
        f'<figcaption>{escape(r["titre"])}</figcaption></figure></li>'
        for r in contenu["realisations"]["liste"]
    )
    z = contenu["zone"]
    carte = json.dumps({"centre": z["centre"], "rayon_km": float(z["rayon_km"]), "nom": z["nom_centre"]}, ensure_ascii=False)
    tel = contenu["contact"].get("telephone", "").strip()
    telephone = f' · <a href="tel:{escape(tel.replace(" ", ""))}">{escape(tel)}</a>' if tel else ""

    index = remplir(gabarit, contenu, {
        "QUI_PARAGRAPHES": paragraphes(contenu["qui_sommes_nous"]["paragraphes"]),
        "ENTREPRISE_PARAGRAPHES": paragraphes(contenu["entreprise"]["paragraphes"]),
        "PRESTATIONS": prestations,
        "REALISATIONS": realisations,
        "TELEPHONE": telephone,
        "CARTE": escape(carte),
        "FAQ": faq_html(contenu["faq"]["liste"]),
        "TAILLE_QUI_1": attributs_taille(contenu["qui_sommes_nous"]["image_1"]),
        "TAILLE_QUI_2": attributs_taille(contenu["qui_sommes_nous"]["image_2"]),
        "TAILLE_ENTREPRISE": attributs_taille(contenu["entreprise"]["image"]),
        "PAGES_VILLES": "".join(
            f'<a href="/{escape(v["slug"])}/">Couvreur à {escape(v["ville"])}</a>' for v in contenu.get("pages_villes", [])),
        "BANDEAU_1": bandeau(contenu["bandeau_1"]),
        "BANDEAU_2": bandeau(contenu["bandeau_2"]),
        "DONNEES_STRUCTUREES": donnees_structurees(contenu),
        "URL": URL,
        "VERSION": version_fichiers(),
    })
    (SORTIE / "index.html").write_text(index, encoding="utf-8")

    (SORTIE / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /admin/\n\nSitemap: {URL}/sitemap.xml\n", encoding="utf-8")
    villes = [pages_ville(contenu, v, prestations) for v in contenu.get("pages_villes", [])]
    urls = [URL + "/"] + villes
    (SORTIE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")

    (SORTIE / "merci.html").write_text(page_simple(
        contenu, "Message envoyé",
        "<p>Merci, votre message a bien été envoyé. Nous vous répondrons dans les meilleurs délais.</p>",
    ), encoding="utf-8")

    s = contenu["societe"]
    responsable = s.get("responsable_publication", "").strip() or "Le gérant de la société"
    (SORTIE / "mentions-legales.html").write_text(page_simple(
        contenu, "Mentions légales",
        f"""<h2>Éditeur du site</h2>
    <p>{escape(s["nom"])}<br>{escape(s["adresse"])}<br>
    SIRET : {escape(s["siret"])}<br>N° TVA intracommunautaire : {escape(s["tva"])}<br>
    Email : <a href="mailto:{escape(contenu["contact"]["email"])}">{escape(contenu["contact"]["email"])}</a></p>
    <p>Responsable de la publication : {escape(responsable)}</p>
    <h2>Hébergement</h2>
    <p>GitHub, Inc. – 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis – pages.github.com</p>
    <h2>Données personnelles</h2>
    <p>Les informations envoyées via le formulaire de contact servent uniquement à répondre à votre demande.
    Elles sont acheminées par e-mail via le service FormSubmit (formsubmit.co), puis ne sont ni revendues
    ni transmises à d'autres tiers. Vous pouvez demander leur suppression à tout moment
    en écrivant à l'adresse ci-dessus.</p>
    <p>La carte de la zone d'intervention affiche des fonds de carte OpenStreetMap (openstreetmap.org),
    chargés directement depuis leurs serveurs. Aucun cookie n'est déposé par le site.</p>
    <h2>Création du site</h2>
    <p>Com' Pour Vous – contact@com-pour-vous.fr</p>""",
    ), encoding="utf-8")

    print("Site construit dans", SORTIE)


if __name__ == "__main__":
    construire()
