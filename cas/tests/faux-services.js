// Faux HubSpot / Anthropic / Slack / Google Actualités pour tester les workflows.
const http = require('http'); const fs = require('fs');
const LOG = process.env.LOG || 'requetes.jsonl';
const DAY = 864e5, now = Date.now();
const iso = d => new Date(d).toISOString();
const claude = {
  qualification_lead: { score: 82, segment: 'clinique', taille_estimee: '250 salariés', besoin: 'Planning des blocs opératoires', resume: 'Directrice des opérations d\'une clinique de 250 salariés, cherche à remplacer les plannings Excel des blocs. Demande une démo.', action: 'appeler_aujourdhui' },
  compte_rendu_rdv: { resume: 'Clinique intéressée par le module blocs. Planning actuel sous Excel, 3 h perdues par semaine.', besoins: ['Planning des blocs', 'Gestion des remplacements'], objections: ['Intégration avec le logiciel RH'], decideurs: ['Claire Martin, directrice des opérations'], budget: null, prochaine_etape: 'Démo avec le DSI', date_relance: iso(now + 5 * DAY).slice(0, 10), etape_suggeree: 'demo', a_verifier: ['Nom du logiciel RH'] },
  signal_compte: { signal: 'ouverture_de_site', pertinence: 78, preuve: 'Clinique du Parc ouvre un second site à Nanterre', source: 'https://exemple.fr/article', accroche: 'Vous ouvrez un second site à Nanterre : les plannings vont devoir suivre sur deux sites. C\'est exactement ce que Nordlys simplifie.' },
};
const contacts = [
  [{ id: '1', properties: { email: 'a@clinique.fr', firstname: 'Ana', lastname: 'Roy', company: 'Clinique A', hubspot_owner_id: '111', hs_lead_status: 'NEW' } },
   { id: '2', properties: { email: 'A@clinique.fr ', firstname: 'Ana', lastname: 'Roy', company: '', hubspot_owner_id: '', hs_lead_status: '' } },
   { id: '3', properties: { email: 'b@centre.fr', firstname: 'Bo', lastname: 'Li', company: 'Centre B', hubspot_owner_id: '222', hs_lead_status: 'OPEN' } }],
  [{ id: '4', properties: { email: 'c@groupe.fr', firstname: 'Cy', lastname: 'Né', company: 'Groupe C', hubspot_owner_id: '', hs_lead_status: 'NEW' } },
   { id: '5', properties: { email: 'd@x.fr', firstname: 'Bo', lastname: 'Li', company: 'Centre B', hubspot_owner_id: '222', hs_lead_status: 'NEW' } }]];
const deals = [{ id: '10', properties: { dealname: 'Clinique A', dealstage: 'qualifiedtobuy', amount: '12000', closedate: iso(now + 20 * DAY), hs_lastmodifieddate: iso(now - 2 * DAY) } },
  { id: '11', properties: { dealname: 'Centre B', dealstage: 'presentationscheduled', amount: '', closedate: iso(now - 10 * DAY), hs_lastmodifieddate: iso(now - 60 * DAY) } },
  { id: '12', properties: { dealname: 'Groupe C', dealstage: 'appointmentscheduled', amount: '30000', closedate: '', notes_last_updated: iso(now - 45 * DAY) } },
  { id: '13', properties: { dealname: 'Vieux deal gagné', dealstage: 'closedwon', amount: '5000', closedate: iso(now - 90 * DAY), hs_lastmodifieddate: iso(now - 90 * DAY) } }];
const rss = items => `<?xml version="1.0"?><rss><channel><title>t</title>${items.map(t => `<item><title><![CDATA[${t}]]></title><link>https://exemple.fr/article</link><pubDate>${new Date().toUTCString()}</pubDate></item>`).join('')}</channel></rss>`;
http.createServer((req, res) => {
  let b = ''; req.on('data', c => b += c); req.on('end', () => {
    const u = new URL(req.url, 'http://x'); let body = null; try { body = JSON.parse(b); } catch (e) { body = b; }
    fs.appendFileSync(LOG, JSON.stringify({ method: req.method, path: u.pathname, query: Object.fromEntries(u.searchParams), headers: { auth: req.headers.authorization, key: req.headers['x-api-key'], ver: req.headers['anthropic-version'] }, body }) + '\n');
    const send = (o, type = 'application/json') => { res.writeHead(200, { 'content-type': type }); res.end(type.includes('json') ? JSON.stringify(o) : o); };
    const p = u.pathname;
    if (p === '/v1/messages') { if (JSON.stringify(body.messages).includes('PANNE')) { res.writeHead(529); return res.end('{"type":"error"}'); } const t = (body.system.match(/Tâche : (\w+)/) || [])[1]; return send({ content: [{ type: 'text', text: JSON.stringify(claude[t]) }] }); }
    if (p === '/crm/v3/objects/contacts/batch/upsert') return send({ results: [{ id: '901', properties: body.inputs[0].properties }] });
    if (p === '/crm/v3/objects/contacts/search') return send(body.filterGroups[0].filters[0].value.startsWith('claire') ? { total: 1, results: [{ id: '902', properties: { hubspot_owner_id: '333', lifecyclestage: 'customer' } }] } : { total: 0, results: [] });
    if (p === '/crm/v3/objects/contacts') { const pg = u.searchParams.get('after') ? 1 : 0; return send({ results: contacts[pg], ...(pg === 0 ? { paging: { next: { after: '2' } } } : {}) }); }
    if (p === '/crm/v3/objects/deals' && req.method === 'GET') return send({ results: deals });
    if (p === '/crm/v3/objects/companies/search') return send({ results: [{ id: '501', properties: { name: 'Clinique du Parc', domain: 'cliniqueduparc.fr', hubspot_owner_id: '111' } }, { id: '502', properties: { name: 'Centre Calme', domain: 'calme.fr', hubspot_owner_id: '222' } }] });
    if (p === '/rss/search') return send(rss(u.searchParams.get('q').includes('Parc') ? ['Clinique du Parc ouvre un second site à Nanterre'] : []), 'application/rss+xml');
    if (p.startsWith('/crm/v3/objects/')) return send({ id: String(Math.floor(Math.random() * 1e6)) });
    if (p === '/slack') return send('ok', 'text/plain');
    res.writeHead(404); res.end('?');
  });
}).listen(5699, () => console.log('mock ok'));
