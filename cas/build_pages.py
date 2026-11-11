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
.wfscroll{overflow-x:auto;border-radius:10px;-webkit-overflow-scrolling:touch}.wfscroll img{min-width:1150px}
.tag.real{background:var(--ok-soft);color:var(--ok)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.kpi{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}.kpi b{display:block;font-size:26px;color:var(--accent)}.kpi span{font-size:13px;color:var(--muted)}
@media (max-width:700px){.kpis{grid-template-columns:1fr 1fr}}
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

FOOT = """<footer><div class="wrap">Cas de démonstration : <b>Nordlys</b> est une entreprise fictive, les données et les personnes aussi. Les workflows et la méthode, eux, sont réels.
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
<figure><div class="wfscroll"><a href="../../img/cas/{c['image']}" target="_blank" rel="noopener" title="Ouvrir en grand"><img src="../../img/cas/{c['image']}" alt="Le workflow « {E(c['titre'])} » dans l'éditeur n8n" width="2400" height="745" loading="lazy"></a></div><figcaption>Capture de l'éditeur n8n, workflow importé tel quel. Faire défiler pour lire chaque étape, ou cliquer pour l'ouvrir en grand.</figcaption></figure>
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
<div class="box"><h3>Testé</h3><p>{c.get('test_reel') or 'Importé et exécuté dans n8n 2.47, avec de faux services HubSpot, Claude et Slack. Les tests automatiques sont dans le dépôt.'}</p></div>
</div>
<div class="btns" style="margin-top:16px"><a class="btn primary" href="../n8n/{c['fichier']}" download>Télécharger le workflow (JSON)</a><a class="btn" href="https://github.com/afrelaut/afrelaut.github.io/tree/main/cas" target="_blank" rel="noopener">Code et tests</a></div>
</section>
</main>
"""
    return HEAD.format(titre=E(c["titre"]), desc=E(c["accroche"]), css=CSS) + corps + FOOT


CAS = [
    dict(slug="lead-entrant", fichier="nordlys-lead-entrant.json", test_reel="Testé en réel le 11/11/2026 sur n8n cloud, avec un vrai compte HubSpot de démonstration et l’API Claude : un lead fictif (« [DÉMO] Clinique du Parc ») a reçu la note 100/100 (« +30 cible, +20 taille, +20 décideur, +20 besoin de planning, +10 urgence »), le contact a été créé dans HubSpot avec la note, son détail et le résumé, puis la tâche « rappeler sous 1 h » a été assignée au commercial. L’alerte Slack était désactivée pendant ce test. Limite assumée : la grille n'est pas encore calibrée sur des ventes réelles ; l'étape suivante serait de comparer chaque mois la note au taux de RDV et de signature. Les tests automatiques sont aussi dans le dépôt.", image="n8n-lead-entrant.webp",
         cible="Sales Ops · CRM · n8n · Claude",
         titre="Lead entrant : du formulaire à HubSpot, qualifié par Claude",
         accroche="Chaque demande du site est nettoyée, notée par Claude, rangée dans HubSpot sans doublon, et le bon commercial est prévenu en quelques secondes.",
         outils=["n8n", "HubSpot API", "Claude (API Anthropic)", "Slack"],
         probleme="Les demandes du site arrivent par email, sont ressaisies à la main dans HubSpot, et les commerciaux rappellent souvent le lendemain. Les bons leads attendent autant que les mauvais.",
         change="Zéro ressaisie, des fiches HubSpot propres (clé unique : l'email), et les leads chauds traités en premier par le commercial du bon segment.",
         etapes=["Le formulaire du site envoie la demande au <b>webhook</b>.",
                 "Le lead est <b>nettoyé</b> : email en minuscules, téléphone normalisé, adresses perso repérées (Gmail, Orange…), emails invalides écartés.",
                 "<b>Claude</b> remplit 5 critères (cible, taille, décideur, besoin de planning, urgence) et écrit un résumé de 2 phrases. Il ne donne pas la note : une <b>grille fixe</b> la calcule (30 + 20 + 20 + 20 + 10 points).",
                 "Le contact est <b>créé ou mis à jour</b> dans HubSpot (clé : l'email, donc pas de doublon), avec la note, son détail point par point et le résumé. S'il existe déjà, il garde son commercial et son cycle de vie.",
                 "Lead chaud (score ≥ 70) : <b>tâche « rappeler sous 1 h »</b> dans HubSpot et <b>alerte Slack</b> au commercial. Sinon : nurturing, sans alerte."],
         sortie="🔥 Lead chaud pour <b>Léa</b> (score 82/100)\n<b>Claire Martin</b>, Directrice des opérations chez Clinique du Parc\nDirectrice des opérations d'une clinique de 250 salariés, cherche à remplacer les plannings Excel des blocs. Demande une démo.\nFiche : https://app.hubspot.com/contacts/…/record/0-1/901",
         choix=["L'IA lit, le code note : même lead = même note, et le commercial voit pourquoi (« +30 cible, +20 décideur… »). Un email perso plafonne la note à 40.",
                "Si Claude ne répond pas ou répond mal, le lead entre quand même dans HubSpot et une <b>tâche d'alerte</b> « à qualifier à la main » est créée : pas de note à 0 silencieuse.",
                "Un client existant n'est jamais réattribué ni rétrogradé en « lead », et un champ vide du formulaire n'efface pas ce que le CRM sait déjà.",
                "Le texte du formulaire est traité comme une donnée : la consigne interdit à Claude de suivre une instruction cachée dedans (« mets-moi 100 »).",
                "Le routage (petits comptes / grands comptes) et les seuils sont dans un seul nœud <b>Paramètres</b> : un Sales Ops peut les changer sans toucher au reste."],
         identifiants="clé API Anthropic, jeton d'app privée HubSpot ; un webhook Slack ; 2 propriétés HubSpot : nordlys_score_ia, nordlys_resume_ia", prompt=True),
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
                "Aucune écriture dans HubSpot si le contact n'est pas certain : mieux vaut une alerte qu'une note sur la mauvaise fiche.",
                "RGPD : les participants sont prévenus de l'enregistrement, et l'envoi des transcriptions à l'API se valide avec le DPO avant la mise en service."],
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


def page_dashboard():
    corps = """<header><div class="wrap">
<span class="tag real">Vrai compte HubSpot · données fictives</span>
<p class="cible">Sales Ops · RevOps · reporting</p>
<h1>Tableau de bord pipeline : voir où les ventes se perdent</h1>
<p class="lead">Un tableau de bord construit dans un vrai compte HubSpot, alimenté par 48 transactions de démonstration créées par l'API, puis lu comme le lirait un Sales Ops : où ça bloque, pourquoi, et quoi faire lundi.</p>
<div class="tools"><span class="tool">HubSpot (rapports et tableaux de bord)</span><span class="tool">API HubSpot CRM</span><span class="tool">Analyse du pipeline</span></div>
</div></header>
<main class="wrap">
<section><div class="grid">
<div class="box"><h3>Le problème</h3><p>Chez Nordlys (fictif), le directeur commercial reçoit chaque lundi un export Excel du CRM. Personne ne sait à quelle étape les ventes se perdent, ni quelles opportunités dorment.</p></div>
<div class="box"><h3>Ce que j'ai fait</h3><p>Créé 48 transactions de démonstration dans un vrai HubSpot (étapes, dates, motifs de perte, propriétaire), monté le tableau de bord à partir du modèle « Aperçu du pipeline », réglé la période, puis analysé les chiffres.</p></div>
</div></section>

<section><h2>Le tableau de bord dans HubSpot</h2>
<figure><img src="../../img/cas/hubspot-entete.webp" alt="En-tête du tableau de bord « Pipeline Nordlys (DÉMO, données fictives) » dans HubSpot" width="1568" height="120" loading="lazy"><figcaption>Capture réelle de HubSpot. Le nom du tableau de bord rappelle que les données sont fictives.</figcaption></figure>
<div class="grid" style="margin-top:14px">
<figure><a href="../../img/cas/hubspot-entonnoir.webp" target="_blank" rel="noopener"><img src="../../img/cas/hubspot-entonnoir.webp" alt="Rapport HubSpot : nombre de transactions par phase du pipeline" width="1359" height="896" loading="lazy"></a><figcaption>Transactions par phase du pipeline.</figcaption></figure>
<figure><a href="../../img/cas/hubspot-statuts.webp" target="_blank" rel="noopener"><img src="../../img/cas/hubspot-statuts.webp" alt="Rapport HubSpot : répartition des transactions ouvertes, perdues et gagnées" width="1092" height="608" loading="lazy"></a><figcaption>Transactions ouvertes, perdues et gagnées.</figcaption></figure>
</div>
</section>

<section><h2>Ce que disent les chiffres</h2>
<div class="kpis">
<div class="kpi"><b>42 %</b><span>taux de gain sur les transactions conclues (10 sur 24)</span></div>
<div class="kpi"><b>40 j</b><span>cycle de vente moyen des transactions gagnées</span></div>
<div class="kpi"><b>9 / 24</b><span>transactions ouvertes depuis plus de 60 jours</span></div>
<div class="kpi"><b>8 / 14</b><span>pertes pour « pas maintenant » (budget, projet reporté)</span></div>
</div>
<ul style="margin-top:16px">
<li><b>L'étape « Décideur introduit » est la plus maigre</b> : 2 transactions, contre 5 en présentation. Premier point à vérifier : souvent, les démos se font sans le décideur.</li>
<li><b>Plus d'une perte sur deux n'est pas un vrai « non »</b> : budget ou projet reporté. Ces prospects reviendront si on les relance au bon moment.</li>
<li><b>Le pipeline ouvert vieillit</b> : plus d'un tiers des opportunités ouvertes a été créé il y a plus de deux mois. À trier avant de croire le forecast.</li>
</ul>
<p style="color:var(--muted);font-size:14px;margin:12px 0 0">Calculs faits sur les 48 transactions de démonstration (données fictives). Aucun montant n'est affiché : le compte de démonstration est en dollars, et les volumes suffisent à la lecture.</p>
</section>

<section><h2>Ce que je recommande au directeur commercial</h2>
<div class="tablewrap"><table>
<tr><th>Action</th><th>Pourquoi</th><th>Comment le suivre</th></tr>
<tr><td>Rendre le décideur obligatoire avant la démo</td><td>L'étape « Décideur introduit » est la plus maigre</td><td>Propriété obligatoire à l'étape, suivie dans l'entonnoir</td></tr>
<tr><td>Motif « pas maintenant » = date de relance obligatoire</td><td>8 pertes sur 14 sont reportables</td><td>Tâche créée automatiquement à la date choisie</td></tr>
<tr><td>Revue des transactions sans activité depuis 60 jours</td><td>Pipeline qui vieillit, forecast surestimé</td><td>Rapport qualité du lundi (cas <a href="../hygiene-crm/">Hygiène CRM</a>)</td></tr>
</table></div>
</section>

<section><h2>Mes choix</h2><ul>
<li>Un rapport du modèle HubSpot affichait 48 « transactions conclues » : il filtre sur la date de clôture prévue, transactions ouvertes comprises. Je ne l'ai pas utilisé tel quel : c'est le genre de chiffre faux qui fait perdre confiance dans un tableau de bord.</li>
<li>Peu d'indicateurs, tous reliés à une décision. Un tableau de bord sert à décider le lundi matin, pas à tout montrer.</li>
<li>Les données de démonstration sont marquées « [DÉMO Nordlys] » dans HubSpot et se suppriment en une fois.</li>
</ul></section>
</main>
"""
    return HEAD.format(titre="Tableau de bord pipeline sur un vrai HubSpot", desc="Cas pratique Sales Ops : tableau de bord pipeline construit dans un vrai HubSpot avec des données de démonstration, analyse et recommandations.", css=CSS) + corps + FOOT


def page_cadrage():
    corps = """<header><div class="wrap">
<span class="tag">Cas de démonstration · entreprise fictive</span>
<p class="cible">Consultant IA · adoption de l'IA</p>
<h1>Cadrage IA : choisir le premier cas d'usage, puis le cadrer</h1>
<p class="lead">Le livrable qu'un consultant IA rend après deux ateliers : les idées classées par valeur, faisabilité et risque, puis la note de cadrage du cas retenu. Une direction peut dire oui ou non en dix minutes.</p>
<div class="tools"><span class="tool">Ateliers métiers</span><span class="tool">Matrice de priorisation</span><span class="tool">RGPD</span><span class="tool">Claude</span><span class="tool">Conduite du changement</span></div>
</div></header>
<main class="wrap">
<section><div class="grid">
<div class="box"><h3>Le contexte</h3><p>Nordlys (fictif) édite un logiciel de planning pour cliniques : 40 commerciaux, 12 personnes au support, 8 au marketing. La direction veut « faire de l'IA » mais ne sait pas par où commencer.</p></div>
<div class="box"><h3>La méthode</h3><p>Deux ateliers d'1 h 30 (ventes, support et marketing), 14 idées recueillies, chacune notée de 1 à 5 sur la valeur et la faisabilité, et classée selon le risque sur les données.</p></div>
</div></section>

<section><h2>1. La matrice de priorisation</h2>
<div class="tablewrap"><table>
<tr><th>Cas d'usage</th><th>Équipe</th><th>Valeur</th><th>Faisabilité</th><th>Risque données</th><th>Décision</th></tr>
<tr><td>Compte rendu de RDV versé au CRM</td><td>Ventes</td><td>5</td><td>5</td><td>Faible</td><td><b>Pilote maintenant</b></td></tr>
<tr><td>Qualification des leads entrants</td><td>Marketing</td><td>4</td><td>5</td><td>Faible</td><td><b>Pilote maintenant</b></td></tr>
<tr><td>Première version des réponses aux appels d'offres</td><td>Ventes</td><td>5</td><td>3</td><td>Moyen</td><td>Phase 2</td></tr>
<tr><td>Réponses support niveau 1 depuis la base d'aide</td><td>Support</td><td>4</td><td>4</td><td>Moyen</td><td>Phase 2</td></tr>
<tr><td>Synthèse des tickets pour l'équipe produit</td><td>Support</td><td>3</td><td>4</td><td>Faible</td><td>Plus tard</td></tr>
<tr><td>Prévision des ventes par l'IA</td><td>Direction</td><td>3</td><td>2</td><td>Moyen</td><td>Non : le CRM n'est pas fiable (voir l'<a href="../audit-crm/">audit</a>)</td></tr>
<tr><td>Analyse des plannings de patients</td><td>Produit</td><td>4</td><td>2</td><td>Élevé (santé)</td><td>Non, pas sans DPO ni hébergement HDS</td></tr>
<tr><td>Rédaction de posts LinkedIn</td><td>Marketing</td><td>2</td><td>5</td><td>Faible</td><td>Usage libre, pas un projet</td></tr>
</table></div>
<p style="color:var(--muted);font-size:14px;margin:10px 0 0">Notes données en atelier par les équipes (fictives). 6 idées sur 14 sont regroupées ou écartées en séance.</p>
</section>

<section><h2>2. La note de cadrage du cas n°1</h2>
<div class="tablewrap"><table>
<tr><th style="width:28%">Rubrique</th><th>Contenu</th></tr>
<tr><td>Objectif</td><td>Que chaque RDV commercial ait un compte rendu propre dans HubSpot le jour même, sans ressaisie.</td></tr>
<tr><td>Périmètre</td><td>10 commerciaux volontaires, RDV en visio, 6 semaines.</td></tr>
<tr><td>Hors périmètre</td><td>RDV sur site, envoi automatique au client, toute donnée de patient.</td></tr>
<tr><td>Solution</td><td>Transcription de la visio, compte rendu rédigé par Claude, relu par le commercial, puis versé dans HubSpot avec la tâche de relance (voir le cas <a href="../compte-rendu-rdv/">Compte rendu de RDV</a>).</td></tr>
<tr><td>Règles</td><td>Relecture humaine obligatoire. Le client est prévenu de l'enregistrement. Transcriptions supprimées après 30 jours. DPO consulté avant le lancement.</td></tr>
<tr><td>Indicateurs</td><td>Part des RDV avec un compte rendu dans le CRM sous 24 h ; temps de saisie par RDV ; satisfaction des commerciaux (sur 5) ; part des comptes rendus corrigés.</td></tr>
<tr><td>Objectifs à 6 semaines</td><td>Plus de 80 % des RDV documentés sous 24 h ; moins de 5 minutes de saisie par RDV ; satisfaction d'au moins 4 sur 5.</td></tr>
<tr><td>Risques et parades</td><td>Erreur dans le compte rendu : relecture obligatoire et suivi des corrections. Refus d'enregistrement par le client : saisie manuelle prévue. Faible adoption : un référent par équipe et un point de 15 minutes par semaine.</td></tr>
<tr><td>Planning</td><td>S1 : cadrage, consentements, DPO. S2 et S3 : construction et tests. S4 et S5 : pilote. S6 : bilan et décision de déploiement.</td></tr>
<tr><td>Gouvernance</td><td>Sponsor : directeur commercial. Chef de projet : consultant IA. Référents : 2 commerciaux. Avis : DPO.</td></tr>
</table></div>
<p style="color:var(--muted);font-size:14px;margin:10px 0 0">Objectifs fixés pour l'exercice : aucun résultat n'est présenté comme obtenu.</p>
</section>

<section><h2>Mes choix</h2><ul>
<li>Commencer par un cas à faible risque et à usage quotidien : l'adoption se gagne sur un premier succès visible, pas sur le cas le plus ambitieux.</li>
<li>Dire non à la prévision des ventes par l'IA tant que le CRM n'est pas propre : l'IA amplifie la qualité des données, bonne ou mauvaise.</li>
<li>Exclure les données de santé du premier pilote : le risque juridique tuerait le projet avant qu'il ait prouvé quoi que ce soit.</li>
</ul></section>
</main>
"""
    return HEAD.format(titre="Cadrage IA : priorisation et note de cadrage", desc="Cas pratique de consultant IA : matrice de priorisation des cas d'usage et note de cadrage d'un pilote Claude (entreprise fictive).", css=CSS) + corps + FOOT


if __name__ == "__main__":
    for c in CAS:
        os.makedirs(os.path.join(ICI, c["slug"]), exist_ok=True)
        open(os.path.join(ICI, c["slug"], "index.html"), "w", encoding="utf-8").write(page_workflow(c))
        print(c["slug"])
    os.makedirs(os.path.join(ICI, "audit-crm"), exist_ok=True)
    open(os.path.join(ICI, "audit-crm", "index.html"), "w", encoding="utf-8").write(page_audit())
    print("audit-crm")
    for slug, fn in (("tableau-de-bord-pipeline", page_dashboard), ("cadrage-ia", page_cadrage)):
        os.makedirs(os.path.join(ICI, slug), exist_ok=True)
        open(os.path.join(ICI, slug, "index.html"), "w", encoding="utf-8").write(fn())
        print(slug)
