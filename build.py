"""Fabrique le site (dossier site/) à partir de contenu/site.json et gabarit.html.

Lancer : python3 build.py
GitHub (fichier .github/workflows/site.yml) lance ce script tout seul à chaque modification faite depuis /admin.
"""
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
        "areaServed": {"@type": "AdministrativeArea", "name": "Cher (18)"},
        "makesOffer": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": p["titre"], "description": p["texte"]}}
            for p in contenu["prestations"]["liste"]
        ],
    }
    tel = contenu["contact"].get("telephone", "").strip()
    if tel:
        fiche["telephone"] = tel
    return json.dumps(fiche, ensure_ascii=False, indent=2).replace("</", "<\\/")


def construire():
    contenu = json.loads((RACINE / "contenu" / "site.json").read_text(encoding="utf-8"))
    gabarit = (RACINE / "gabarit.html").read_text(encoding="utf-8")

    prestations = "\n        ".join(
        f'<li>{icone(p.get("icone"))}<div><h3>{escape(p["titre"])}</h3><p>{escape(p["texte"])}</p></div></li>'
        for p in contenu["prestations"]["liste"]
    )
    realisations = "\n          ".join(
        f'<li><figure tabindex="0"><img src="{escape(r["image"])}" alt="{escape(r["titre"])}" loading="lazy">'
        f'<figcaption>{escape(r["titre"])}</figcaption></figure></li>'
        for r in contenu["realisations"]["liste"]
    )
    tel = contenu["contact"].get("telephone", "").strip()
    telephone = f' · <a href="tel:{escape(tel.replace(" ", ""))}">{escape(tel)}</a>' if tel else ""

    index = remplir(gabarit, contenu, {
        "QUI_PARAGRAPHES": paragraphes(contenu["qui_sommes_nous"]["paragraphes"]),
        "ENTREPRISE_PARAGRAPHES": paragraphes(contenu["entreprise"]["paragraphes"]),
        "PRESTATIONS": prestations,
        "REALISATIONS": realisations,
        "TELEPHONE": telephone,
        "BANDEAU_1": bandeau(contenu["bandeau_1"]),
        "BANDEAU_2": bandeau(contenu["bandeau_2"]),
        "DONNEES_STRUCTUREES": donnees_structurees(contenu),
        "URL": URL,
    })
    (SORTIE / "index.html").write_text(index, encoding="utf-8")

    (SORTIE / "robots.txt").write_text(
        f"User-agent: *\nDisallow: /admin/\n\nSitemap: {URL}/sitemap.xml\n", encoding="utf-8")
    (SORTIE / "sitemap.xml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{URL}/</loc><lastmod>{date.today().isoformat()}</lastmod></url>
</urlset>
""", encoding="utf-8")

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
    <h2>Création du site</h2>
    <p>Com' Pour Vous – contact@com-pour-vous.fr</p>""",
    ), encoding="utf-8")

    print("Site construit dans", SORTIE)


if __name__ == "__main__":
    construire()
