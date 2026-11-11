# Cas pratiques (entreprise fictive « Nordlys »)

- `n8n/` : les 4 workflows, à importer dans n8n (Importer depuis un fichier).
- `build_workflows.py` : génère les JSON. `build_pages.py` : génère les pages `cas/*/index.html`.
- `tests/` : `faux-services.js` simule HubSpot, l'API Anthropic, Slack et Google Actualités ;
  `tester.py` importe les workflows dans un vrai n8n, les exécute et vérifie 14 points.
  Lancer : `N8N_BIN=n8n python3 tests/tester.py` (Node 24 requis par n8n 2.x).

Nordlys, ses salariés et ses données sont fictifs. Les workflows sont réels.
