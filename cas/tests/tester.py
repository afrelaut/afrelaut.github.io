"""Teste les 4 workflows dans un vrai n8n, avec de faux HubSpot / Claude / Slack / Google Actualités.

Prérequis : Node 24 et n8n installés (N8N_BIN = chemin du binaire n8n). Usage : python3 tester.py
"""
import glob, json, os, shutil, subprocess, sys, tempfile, time, urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
N8N = os.environ.get("N8N_BIN", "n8n").split()
PORT_FAUX, PORT_N8N = 5699, 5678
tmp = tempfile.mkdtemp(prefix="nordlys-")
LOG = os.path.join(tmp, "requetes.jsonl")
env = dict(os.environ, N8N_USER_FOLDER=tmp, N8N_ENCRYPTION_KEY="test", N8N_DIAGNOSTICS_ENABLED="false",
           N8N_LISTEN_ADDRESS="127.0.0.1", N8N_PORT=str(PORT_N8N), LOG=LOG)
faux = f"http://127.0.0.1:{PORT_FAUX}"

os.makedirs(os.path.join(tmp, "wf"))
for i, f in enumerate(sorted(glob.glob(os.path.join(ICI, "..", "n8n", "*.json")))):
    s = open(f, encoding="utf-8").read()
    for a, b in [("https://api.hubapi.com", faux), ("https://api.anthropic.com", faux),
                 ("https://hooks.slack.com/services/A_REMPLACER", faux + "/slack"),
                 ("https://news.google.com/rss/search", faux + "/rss/search")]:
        s = s.replace(a, b)
    w = json.loads(s); w["id"] = os.path.basename(f)[8:-5].replace("-", "")[:16].ljust(16, "x")
    json.dump(w, open(os.path.join(tmp, "wf", os.path.basename(f)), "w"), ensure_ascii=False)
json.dump([{"id": "nordlys-anthropic", "name": "Anthropic (clé API)", "type": "httpHeaderAuth", "data": {"name": "x-api-key", "value": "cle-test"}},
           {"id": "nordlys-hubspot", "name": "HubSpot (app privée)", "type": "httpHeaderAuth", "data": {"name": "Authorization", "value": "Bearer jeton-test"}}],
          open(os.path.join(tmp, "creds.json"), "w"))

run = lambda *a: subprocess.run(N8N + list(a), env=env, capture_output=True, text=True, timeout=300)
run("import:credentials", "--input=" + os.path.join(tmp, "creds.json"))
run("import:workflow", "--separate", "--input=" + os.path.join(tmp, "wf"))
ids = {os.path.basename(f): json.load(open(f))["id"] for f in glob.glob(os.path.join(tmp, "wf", "*.json"))}
mock = subprocess.Popen(["node", os.path.join(ICI, "faux-services.js")], env=dict(env), stdout=subprocess.DEVNULL)
time.sleep(1)

def requetes():
    return [json.loads(l) for l in open(LOG)] if os.path.exists(LOG) else []

def vider():
    open(LOG, "w").close()

echecs = []
def verifier(nom, cond):
    print(("OK   " if cond else "ÉCHEC"), nom)
    if not cond: echecs.append(nom)

# Workflows planifiés : lancés à la main par la CLI.
for fichier, nom in [("nordlys-hygiene-crm.json", "hygiène"), ("nordlys-signaux-comptes.json", "signaux")]:
    vider()
    r = run("execute", "--id=" + ids[fichier], "--rawOutput")
    verifier(f"{nom} : exécution réussie", '"status": "success"' in r.stdout)
    rq = requetes()
    slack = [x for x in rq if x["path"] == "/slack"]
    if nom == "hygiène":
        verifier("hygiène : 2 pages de contacts lues (pagination)", sum(x["path"] == "/crm/v3/objects/contacts" for x in rq) == 2)
        verifier("hygiène : rapport Slack avec 2 doublons et 60 %", bool(slack) and "2 doublons" in slack[0]["body"]["text"] and "60 %" in slack[0]["body"]["text"])
    else:
        verifier("signaux : Claude appelé seulement pour le compte qui a des articles", sum(x["path"] == "/v1/messages" for x in rq) == 1)
        verifier("signaux : tâche HubSpot liée à l'entreprise", any(x["path"] == "/crm/v3/objects/tasks" and x["body"]["associations"][0]["types"][0]["associationTypeId"] == 192 for x in rq))
        verifier("signaux : résumé Slack", bool(slack) and "Clinique du Parc" in slack[0]["body"]["text"])

# Workflows à webhook : n8n démarré, puis appels HTTP.
for fichier in ["nordlys-lead-entrant.json", "nordlys-compte-rendu-rdv.json"]:
    run("publish:workflow", "--id=" + ids[fichier])
srv = subprocess.Popen(N8N + ["start"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(90):
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT_N8N}/healthz", timeout=2); break
    except Exception:
        time.sleep(2)
time.sleep(5)

def poster(chemin, data):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT_N8N}/webhook/{chemin}", json.dumps(data).encode(), {"content-type": "application/json"})
    urllib.request.urlopen(req, timeout=20).read(); time.sleep(4)

vider(); poster("nordlys-lead", {"nom_complet": "Claire Martin", "email": " Claire.Martin@CliniqueDuParc.fr ", "entreprise": "Clinique du Parc", "poste": "Directrice des opérations", "message": "Démo SVP"})
rq = requetes(); up = [x for x in rq if x["path"].endswith("batch/upsert")]
verifier("lead : contact créé avec email nettoyé", bool(up) and up[0]["body"]["inputs"][0]["id"] == "claire.martin@cliniqueduparc.fr")
verifier("lead : 250 salariés → petits comptes (Léa)", bool(up) and up[0]["body"]["inputs"][0]["properties"]["hubspot_owner_id"] == "111")
verifier("lead chaud : transaction + alerte Slack", any(x["path"] == "/crm/v3/objects/deals" for x in rq) and any(x["path"] == "/slack" for x in rq))
vider(); poster("nordlys-lead", {"nom_complet": "Paul Panne", "email": "paul@clinique.fr", "entreprise": "PANNE"})
rq = requetes(); up = [x for x in rq if x["path"].endswith("batch/upsert")]
verifier("lead : Claude en panne → contact créé quand même, à qualifier à la main", bool(up) and "à la main" in up[0]["body"]["inputs"][0]["properties"]["nordlys_resume_ia"])
vider(); poster("nordlys-lead", {"nom_complet": "Test", "email": "pas-un-email"})
verifier("lead : email invalide rejeté sans appel externe", requetes() == [])

transcription = "Léa : bonjour Claire. Claire : nos plannings de bloc sont sur Excel. " * 10
vider(); poster("nordlys-compte-rendu", {"email_contact": "claire@connu.fr", "commercial": "Léa", "date_rdv": "2026-11-10", "transcription": transcription})
rq = requetes()
verifier("compte rendu : note + tâche de relance dans HubSpot", any(x["path"] == "/crm/v3/objects/notes" for x in rq) and any(x["path"] == "/crm/v3/objects/tasks" for x in rq))
vider(); poster("nordlys-compte-rendu", {"email_contact": "inconnu@exemple.fr", "transcription": transcription})
rq = requetes()
verifier("compte rendu : contact inconnu → alerte, rien écrit dans HubSpot", not any(x["path"] in ("/crm/v3/objects/notes", "/crm/v3/objects/tasks") for x in rq) and any("Aucun contact" in x["body"].get("text", "") for x in rq if x["path"] == "/slack"))

srv.terminate(); mock.terminate(); shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{'Tous les tests passent' if not echecs else str(len(echecs)) + ' échec(s)'}")
sys.exit(1 if echecs else 0)
