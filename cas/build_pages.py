"""Génère les pages des cas pratiques (cas/<slug>/index.html). Usage : python3 build_pages.py"""
import html, json, os

ICI = os.path.dirname(os.path.abspath(__file__))
E = html.escape

CSS = """
:root{--bg:#f7f7f5;--surface:#fff;--text:#15161a;--muted:#5c606b;--line:#e3e4e8;--accent:#2f5bff;--accent-soft:#e8edff;--fict:#8a5a00;--fict-soft:#fbf0d9;--ok:#12805c;--ok-soft:#e3f4ec;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1013;--surface:#17191e;--text:#ecedf0;--muted:#9a9fab;--line:#2a2d35;--accent:#7d97ff;--accent-soft:#1d2440;--fict:#e7b54f;--fict-soft:#2c2312;--ok:#4cc99a;--ok-soft:#13291f}}
:root[data-theme="dark"]{--bg:#0f1013;--surface:#17191e;--text:#ecedf0;--muted:#9a9fab;--line:#2a2d35;--accent:#7d97ff;--accent-soft:#1d2440;--fict:#e7b54f;--fict-soft:#2c2312;--ok:#4cc99a;--ok-soft:#13291f}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 Inter,system-ui,-apple-system,sans-serif}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:900px;margin:0 auto;padding:0 16px}
nav{border-bottom:1px solid var(--line);background:var(--bg)}nav .wrap{display:flex;justify-content:space-between;align-items:center;height:52px;gap:12px;font-size:14px}
nav b{color:var(--text)}
header{padding:40px 0 24px}
.tag{display:inline-block;font:500 11px/1 var(--mono);letter-spacing:.06em;text-transform:uppercase;padding:6px 9px;border-radius:6px;background:var(--fict-soft);color:var(--fict);margin-bottom:14px}
.tag.ok{background:var(--ok-soft);color:var(--ok)}
h1{font-size:clamp(28px,5vw,40px);line-height:1.12;margin:0 0 12px;letter-spacing:-.02em}
.lead{font-size:18px;color:var(--muted);margin:0;max-width:720px}
.cible{font:500 13px var(--mono);color:var(--accent);margin:0 0 10px}
section{padding:26px 0;border-top:1px solid var(--line)}
h2{font-size:21px;margin:0 0 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.box{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px}
.box h3{font:500 12px var(--mono);text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 8px}
.box p{margin:0}
ol.steps{margin:0;padding-left:22px}ol.steps li{margin-bottom:8px}
ul{margin:0;padding-left:20px}li{margin-bottom:6px}
figure{margin:0}figure img{width:100%;height:auto;display:block;border:1px solid var(--line);border-radius:10px;background:#fafafa}
figcaption{font-size:13px;color:var(--muted);margin-top:6px}
.slack{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:14px 16px;font-size:14.5px;white-space:pre-wrap}
.slack b{font-weight:600}
pre{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto;font:12.5px/1.55 var(--mono);white-space:pre-wrap;margin:0}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.btn{display:inline-flex;align-items:center;padding:10px 16px;border-radius:8px;font-weight:600;font-size:15px;border:1px solid var(--line);background:var(--surface);color:var(--text)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}.btn:hover{text-decoration:none;filter:brightness(1.05)}
.tools{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}.tool{font:12px/1 var(--mono);padding:5px 8px;border-radius:6px;background:var(--accent-soft)}
table{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:9px 12px;border-top:1px solid var(--line);vertical-align:top}th{font:500 12px var(--mono);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);border-top:0;background:var(--bg)}
.tablewrap{overflow-x:auto}
.pipe{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:13.5px}.pipe span{padding:6px 10px;border-radius:999px;border:1px solid var(--line);background:var(--surface)}.pipe span.off{opacity:.55;text-decoration:line-through}
footer{padding:30px 0 50px;border-top:1px solid var(--line);color:var(--muted);font-size:14px}
@media (max-width:700px){.grid{grid-template-columns:1fr}.lead{font-size:17px}}
"""

HEAD = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titre} · Aymeric Frelaut</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{titre} · cas pratique">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://afrelaut.github.io/img/og.png">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%232f5bff'/%3E%3Ctext x='16' y='22' font-family='Arial' font-weight='700' font-size='15' fill='white' text-anchor='middle'%3EAF%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<nav><div class="wrap"><a href="../../"><b>Aymeric Frelaut</b></a><a href="../../#cas">← Tous les cas pratiques</a></div></nav>
"""

FOOT = """<footer><div class="wrap">Cas de démonstration : <b>Nordlys</b> est une entreprise fictive, les données et les personnes aussi. Les workflows, eux, sont réels.
<div class="btns" style="margin-top:14px"><a class="btn primary" href="mailto:afrelaut@gmail.com">Me contacter</a><a class="btn" href="https://www.linkedin.com/in/aymeric-frelaut" target="_blank" rel="noopener">LinkedIn</a><a class="btn" href="../../">Retour au portfolio</a></div></div></footer>
</body>
</html>
"""

CONTEXTE = "Nordlys (fictif) édite un logiciel de planning pour cliniques. 40 commerciaux, HubSpot comme CRM, Slack en interne."


def li(items):
    return "".join(f"<li>{x}</li>" for x in items)


def page_workflow(c):
    wf = json.load(open(os.path.join(ICI, "n8n", c["fichier"]), encoding="utf-8"))
    prompt = next(n for n in wf["nodes"] if n["name"].startswith("Claude")) if c.get("prompt") else None
    prompt_txt = ""
    if prompt:
        body = prompt["parameters"]["jsonBody"]
        start = body.index("system: ") + len("system: ")
        prompt_txt = json.loads(body[start:body.index(", messages:")])
    corps = f"""<header><div class="wrap">
<span class="tag">Cas de démonstration · entreprise fictive</span>
<p class="cible">{c['cible']}</p>
<h1>{c['titre']}</h1>
<p class="lead">{c['accroche']}</p>
<div class="tools">{''.join(f'<span class="tool">{t}</span>' for t in c['outils'])}</div>
</div></header>
<main class="wrap">
<section><div class="grid">
<div class="box"><h3>Le problème</h3><p>{c['probleme']}</p></div>
<div class="box"><h3>Ce que ça change</h3><p>{c['change']}</p></div>
</div></section>
<section><h2>Le workflow dans n8n</h2>
<figure><a href="../../img/cas/{c['image']}" target="_blank" rel="noopener" title="Ouvrir en grand"><img src="../../img/cas/{c['image']}" alt="Le workflow « {E(c['titre'])} » dans l'éditeur n8n" width="2400" height="745" loading="lazy"></a><figcaption>Capture de l'éditeur n8n, workflow importé tel quel. Cliquer pour agrandir.</figcaption></figure>
<ol class="steps" style="margin-top:18px">{li(c['etapes'])}</ol>
</section>
<section><h2>Ce que reçoit l'équipe</h2>
<div class="slack">{c['sortie']}</div>
<p style="color:var(--muted);font-size:14px;margin:8px 0 0">Message réel produit pendant le test, avec des données fictives.</p>
</section>
<section><h2>Mes choix</h2><ul>{li(c['choix'])}</ul></section>
""" + (f"""<section><h2>La consigne donnée à Claude</h2><pre>{E(prompt_txt)}</pre></section>""" if prompt_txt else "") + f"""
<section><h2>Le récupérer</h2>
<div class="grid">
<div class="box"><h3>Installer en 3 étapes</h3><ol class="steps"><li>Dans n8n : Importer depuis un fichier, choisir le JSON.</li><li>Créer les identifiants demandés ({c['identifiants']}).</li><li>Adapter le nœud <b>Paramètres</b>, puis activer.</li></ol></div>
<div class="box"><h3>Testé</h3><p>Importé et exécuté dans n8n 2.47, avec de faux services HubSpot, Claude et Slack. Les tests automatiques sont dans le dépôt.</p></div>
</div>
<div class="btns" style="margin-top:16px"><a class="btn primary" href="../n8n/{c['fichier']}" download>Télécharger le workflow (JSON)</a><a class="btn" href="https://github.com/afrelaut/afrelaut.github.io/tree/main/cas" target="_blank" rel="noopener">Code et tests</a></div>
</section>
</main>
"""
    return HEAD.format(titre=E(c["titre"]), desc=E(c["accroche"]), css=CSS) + corps + FOOT


CAS = [
    dict(slug="lead-entrant", fichier="nordlys-lead-entrant.json", image="n8n-lead-entrant.webp",
         cible="Sales Ops · CRM · n8n · Claude",
         titre="Lead entrant : du formulaire à HubSpot, qualifié par Claude",
         accroche="Chaque demande du site est nettoyée, notée par Claude, rangée dans HubSpot sans doublon, et le bon commercial est prévenu en quelques secondes.",
         outils=["n8n", "HubSpot API", "Claude (API Anthropic)", "Slack"],
         probleme="Les demandes du site arrivent par email, sont ressaisies à la main dans HubSpot, et les commerciaux rappellent souvent le lendemain. Les bons leads attendent autant que les mauvais.",
         change="Zéro ressaisie, des fiches HubSpot propres (clé unique : l'email), et les leads chauds traités en premier par le commercial du bon segment.",
         etapes=["Le formulaire du site envoie la demande au <b>webhook</b>.",
                 "Le lead est <b>nettoyé</b> : email en minuscules, téléphone normalisé, adresses perso repérées (Gmail, Orange…), emails invalides écartés.",
                 "<b>Claude</b> note le lead de 0 à 100 selon le client idéal et écrit un résumé de 2 phrases pour le commercial.",
                 "Le contact est <b>créé ou mis à jour</b> dans HubSpot (upsert sur l'email : jamais de doublon), avec le score et le résumé.",
                 "Lead chaud (score ≥ 70) : <b>transaction</b> créée et <b>alerte Slack</b> au commercial du segment. Sinon : nurturing, sans alerte."],
         sortie="🔥 Lead chaud pour <b>Léa</b> (score 82/100)\n<b>Claire Martin</b>, Directrice des opérations chez Clinique du Parc\nDirectrice des opérations d'une clinique de 250 salariés, cherche à remplacer les plannings Excel des blocs. Demande une démo.\nFiche : https://app.hubspot.com/contacts/…/record/0-1/901",
         choix=["L'IA propose, des règles encadrent : un email perso plafonne le score à 40, quoi que dise Claude.",
                "Si Claude ne répond pas, le lead entre quand même dans HubSpot, marqué « à qualifier à la main ». On ne perd jamais un lead.",
                "Le routage (petits comptes / grands comptes) et les seuils sont dans un seul nœud <b>Paramètres</b> : un Sales Ops peut les changer sans toucher au reste."],
         identifiants="clé API Anthropic, jeton d'app privée HubSpot ; un webhook Slack", prompt=True),
    dict(slug="compte-rendu-rdv", fichier="nordlys-compte-rendu-rdv.json", image="n8n-compte-rendu-rdv.webp",
         cible="Consultant IA · adoption de Claude · CRM",
         titre="Compte rendu de RDV : de la transcription au CRM",
         accroche="Après un rendez-vous, Claude rédige le compte rendu, le workflow le range dans HubSpot et crée la relance. Le commercial n'a plus qu'à relire.",
         outils=["n8n", "Claude (API Anthropic)", "HubSpot API", "Slack"],
         probleme="Les comptes rendus sont écrits tard, ou pas du tout. Le CRM ne dit plus où en est chaque affaire, et les relances se perdent.",
         change="Chaque RDV laisse une note structurée (besoins, objections, décideurs, prochaine étape) et une tâche de relance datée, sans effort de saisie.",
         etapes=["L'outil d'enregistrement d'appels (Modjo, Fireflies, Teams…) envoie la <b>transcription</b> et l'email du contact.",
                 "<b>Claude</b> en tire un compte rendu structuré, sans rien inventer, avec la liste des points à vérifier.",
                 "Le workflow <b>retrouve le contact</b> dans HubSpot par son email.",
                 "Il ajoute la <b>note</b> sur la fiche et crée la <b>tâche de relance</b> à la date dite pendant l'appel (7 jours par défaut).",
                 "Le commercial reçoit un <b>résumé Slack</b>. Contact introuvable : rien n'est écrit, le CR part en alerte pour être classé à la main."],
         sortie="📝 CR du RDV avec claire@… ajouté dans HubSpot, relance le 2026-11-16.\nClinique intéressée par le module blocs. Planning actuel sous Excel, 3 h perdues par semaine.\nÉtape suggérée : <b>demo</b> (à valider par toi, rien n'est changé automatiquement).\nÀ vérifier : Nom du logiciel RH",
         choix=["L'étape du pipeline est <b>suggérée</b>, jamais changée seule : le commercial reste maître de son forecast.",
                "Claude liste ce qui est flou (« à vérifier ») au lieu de deviner. C'est ce qui rend l'outil digne de confiance pour l'équipe.",
                "Aucune écriture dans HubSpot si le contact n'est pas certain : mieux vaut une alerte qu'une note sur la mauvaise fiche."],
         identifiants="clé API Anthropic, jeton d'app privée HubSpot ; un webhook Slack", prompt=True),
    dict(slug="hygiene-crm", fichier="nordlys-hygiene-crm.json", image="n8n-hygiene-crm.webp",
         cible="RevOps · Sales Ops · qualité des données",
         titre="Hygiène CRM du lundi : le rapport qualité automatique",
         accroche="Chaque lundi à 8 h, le workflow passe tout HubSpot au crible et envoie au manager ce qu'il faut corriger, fiche par fiche.",
         outils=["n8n", "HubSpot API", "Slack"],
         probleme="Doublons, fiches sans propriétaire, transactions oubliées depuis des mois, dates de closing dépassées : le forecast n'est plus crédible et personne ne sait par où commencer.",
         change="Un indicateur suivi chaque semaine (% de fiches complètes) et une liste courte d'actions, avec un lien direct vers chaque fiche.",
         etapes=["Déclenchement <b>chaque lundi à 8 h</b> (ou à la main).",
                 "Lecture de <b>tous les contacts et transactions</b> HubSpot, page par page (100 par page).",
                 "Contrôles : <b>doublons</b> (même email, ou même nom + entreprise), contacts sans propriétaire, sans entreprise, sans statut.",
                 "Transactions ouvertes <b>sans activité depuis 30 jours</b>, date de closing dépassée ou absente, montant manquant.",
                 "<b>Rapport Slack</b> au manager avec les chiffres et les premières fiches à traiter."],
         sortie="🧹 <b>Hygiène CRM du lundi</b> : 5 contacts, 3 transactions ouvertes. Contacts complets : <b>60 %</b>.\n<b>Contacts</b> : 2 doublons probables, 2 sans propriétaire, 1 sans entreprise, 1 sans statut de lead.\n<b>Transactions</b> : 2 sans activité depuis 30 jours, 1 avec une date de closing dépassée, 1 sans date de closing, 1 sans montant.",
         choix=["Rien n'est corrigé ni fusionné automatiquement : une fusion de doublons se décide, elle ne s'automatise pas à l'aveugle.",
                "Pas d'IA ici, volontairement : des règles simples suffisent et sont vérifiables par n'importe qui.",
                "Le seuil d'inactivité et les champs contrôlés se changent dans <b>Paramètres</b>."],
         identifiants="jeton d'app privée HubSpot ; un webhook Slack", prompt=False),
    dict(slug="signaux-comptes", fichier="nordlys-signaux-comptes.json", image="n8n-signaux-comptes.webp",
         cible="BDR avec ops · prospection · Claude",
         titre="Signaux sur comptes cibles : le bon moment pour appeler",
         accroche="Chaque matin, le workflow lit l'actualité des comptes cibles, Claude repère les vrais signaux d'achat et le SDR reçoit une tâche avec une accroche et sa source.",
         outils=["n8n", "HubSpot API", "Google Actualités (RSS)", "Claude (API Anthropic)", "Slack"],
         probleme="Les SDR prospectent leurs comptes cibles à froid, sans raison de les appeler maintenant. La veille à la main prend du temps et n'est jamais faite.",
         change="Chaque matin, une courte liste de comptes avec une vraie raison d'appeler (ouverture de site, levée, recrutement, nouveau dirigeant) et une première phrase prête.",
         etapes=["Chaque matin en semaine, lecture des entreprises marquées <b>« compte cible »</b> dans HubSpot.",
                 "Pour chacune, les <b>actualités des 2 derniers jours</b> (Google Actualités).",
                 "<b>Claude</b> classe le signal, note sa pertinence et propose une accroche de 2 phrases, en citant l'article.",
                 "Signal utile (≥ 60/100) : <b>tâche HubSpot</b> liée à l'entreprise, pour le propriétaire du compte.",
                 "<b>Résumé Slack</b> des signaux du jour."],
         sortie="📡 <b>1 signal(s) ce matin</b> sur les comptes cibles :\n• <b>Clinique du Parc</b> : ouverture de site (78/100). Clinique du Parc ouvre un second site à Nanterre",
         choix=["Claude n'est appelé que pour les comptes qui ont des articles : pas de coût inutile.",
                "La source est toujours citée : le SDR vérifie avant d'écrire, l'IA ne parle jamais seule au prospect.",
                "Les comptes cibles se gèrent dans HubSpot (une case à cocher), pas dans n8n : l'équipe commerciale garde la main."],
         identifiants="clé API Anthropic, jeton d'app privée HubSpot ; un webhook Slack", prompt=True),
]


def page_audit():
    corps = """<header><div class="wrap">
<span class="tag">Cas de démonstration · entreprise fictive</span>
<p class="cible">Consultant CRM · RevOps</p>
<h1>Audit HubSpot et plan à 30 jours</h1>
<p class="lead">Le livrable qu'un consultant rend à un client : ce qui ne va pas, pourquoi, et ce qu'on fait semaine par semaine. Une page, lisible par le directeur commercial.</p>
<div class="tools"><span class="tool">HubSpot</span><span class="tool">Audit de données</span><span class="tool">Entretiens</span><span class="tool">Conduite du changement</span></div>
</div></header>
<main class="wrap">
<section><div class="grid">
<div class="box"><h3>Le contexte</h3><p>Nordlys (fictif) : éditeur SaaS B2B, 40 commerciaux. HubSpot a été installé il y a 3 ans, sans règles communes. Le directeur commercial ne croit plus au forecast.</p></div>
<div class="box"><h3>La demande</h3><p>« Rendez-moi un CRM fiable en un mois, sans changer d'outil et sans bloquer les commerciaux. »</p></div>
</div></section>

<section><h2>1. Le diagnostic (semaine 1)</h2>
<p>Export complet, contrôle qualité automatique (voir le cas <a href="../hygiene-crm/">Hygiène CRM</a>) et 6 entretiens de 30 minutes avec des commerciaux et le management.</p>
<div class="tablewrap"><table>
<tr><th>Constat (données fictives)</th><th>Conséquence</th><th>Priorité</th></tr>
<tr><td>31 % des contacts sans source de lead</td><td>Impossible de savoir quel canal rapporte</td><td>Haute</td></tr>
<tr><td>18 % de doublons</td><td>Deux commerciaux sur le même prospect, relances en double</td><td>Haute</td></tr>
<tr><td>9 étapes de pipeline, dont 3 jamais utilisées</td><td>Chacun interprète les étapes à sa façon</td><td>Haute</td></tr>
<tr><td>Transactions « en cours » depuis plus de 180 jours</td><td>Le forecast gonfle artificiellement</td><td>Moyenne</td></tr>
<tr><td>Aucune propriété obligatoire</td><td>Fiches vides, reporting impossible</td><td>Moyenne</td></tr>
</table></div>
</section>

<section><h2>2. Le pipeline, avant et après</h2>
<p style="margin:0 0 8px;color:var(--muted)">Avant : 9 étapes</p>
<div class="pipe"><span>Nouveau</span><span>Contacté</span><span class="off">Intéressé</span><span>RDV</span><span class="off">Qualifié</span><span>Démo</span><span>Proposition</span><span class="off">Validation</span><span>Négociation</span></div>
<p style="margin:16px 0 8px;color:var(--muted)">Après : 6 étapes, chacune avec un critère de passage écrit</p>
<div class="tablewrap"><table>
<tr><th>Étape</th><th>On y passe quand…</th><th>Champs obligatoires</th></tr>
<tr><td>1. Découverte</td><td>Premier RDV tenu avec un interlocuteur identifié</td><td>Source, propriétaire</td></tr>
<tr><td>2. Qualifiée</td><td>Besoin, décideur et calendrier connus</td><td>Décideur, besoin, date de closing</td></tr>
<tr><td>3. Démo faite</td><td>Démo réalisée avec le décideur présent</td><td>Nombre de sites, montant estimé</td></tr>
<tr><td>4. Proposition</td><td>Proposition envoyée</td><td>Montant, date d'envoi</td></tr>
<tr><td>5. Négociation</td><td>Retour écrit du client sur la proposition</td><td>Objections principales</td></tr>
<tr><td>6. Gagnée / Perdue</td><td>Signature, ou refus</td><td>Motif de perte (liste fermée)</td></tr>
</table></div>
</section>

<section><h2>3. Le plan à 30 jours</h2>
<div class="tablewrap"><table>
<tr><th>Semaine</th><th>Actions</th><th>Livrable</th></tr>
<tr><td>S1 · Diagnostic</td><td>Export, contrôles qualité, 6 entretiens, priorisation avec le directeur commercial</td><td>Ce document</td></tr>
<tr><td>S2 · Nettoyage</td><td>Fusion des doublons (validée par échantillon), clôture des transactions mortes avec motif, source renseignée en masse quand c'est possible</td><td>Base propre, journal des modifications</td></tr>
<tr><td>S3 · Règles</td><td>Nouveau pipeline, propriétés obligatoires par étape, règles anti-doublons, lead scoring simple (profil + engagement)</td><td>Pipeline et propriétés en production</td></tr>
<tr><td>S4 · Adoption</td><td>Formation de 45 min par équipe, guide d'une page, dashboard hebdo, rapport qualité automatique du lundi</td><td>Guide, dashboard, rituel du lundi</td></tr>
</table></div>
</section>

<section><h2>4. Comment on saura que ça marche</h2>
<div class="grid">
<div class="box"><h3>Objectifs à 30 jours</h3><ul><li>Doublons sous 2 %</li><li>100 % des transactions ouvertes avec une date de closing</li><li>Plus aucune transaction sans activité depuis 90 jours</li></ul></div>
<div class="box"><h3>Le suivi</h3><p>Le rapport qualité du lundi donne les chiffres chaque semaine. Point de 15 minutes avec le directeur commercial à J+30, puis à J+60.</p></div>
</div>
<p style="color:var(--muted);font-size:14px;margin:12px 0 0">Objectifs fixés pour l'exercice : aucun résultat n'est présenté comme obtenu.</p>
</section>

<section><h2>Mes choix</h2><ul>
<li>Pas de nouvel outil : le problème vient des règles, pas de HubSpot.</li>
<li>Les commerciaux sont interrogés avant de toucher au pipeline : un CRM que l'équipe n'adopte pas redevient sale en trois mois.</li>
<li>Rien n'est supprimé sans échantillon validé et journal des modifications.</li>
</ul></section>
</main>
"""
    return HEAD.format(titre="Audit HubSpot et plan à 30 jours", desc="Cas pratique de consultant CRM : diagnostic HubSpot, pipeline refait avec critères de passage et plan à 30 jours (entreprise fictive).", css=CSS) + corps + FOOT


if __name__ == "__main__":
    for c in CAS:
        os.makedirs(os.path.join(ICI, c["slug"]), exist_ok=True)
        open(os.path.join(ICI, c["slug"], "index.html"), "w", encoding="utf-8").write(page_workflow(c))
        print(c["slug"])
    os.makedirs(os.path.join(ICI, "audit-crm"), exist_ok=True)
    open(os.path.join(ICI, "audit-crm", "index.html"), "w", encoding="utf-8").write(page_audit())
    print("audit-crm")
