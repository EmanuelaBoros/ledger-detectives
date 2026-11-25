"""Build the data viewer (two files, same app).

viewer/index.html         no data inside; load data/v0.1/*.csv from disk (safe to commit)
viewer/viewer-local.html  all rows embedded (contains corpus and test labels; gitignored)

Usage (repo root): python3 -I viewer/make_viewer.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ann = list(csv.DictReader(open(ROOT / "data/v0.1/annotations_v0.1.csv", encoding="utf-8")))
spans = defaultdict(list)
texts = {}
for a in csv.DictReader(open(ROOT / "data/v0.1/actors_v0.1.csv", encoding="utf-8")):
    spans[a["row_id"]].append([int(a["start"]), int(a["end"])])
    texts[a["row_id"]] = a["text"]

rows = []
for r in ann:
    pre, span, post = r["pre_context"], r["span_text"], r["post_context"]
    text = texts.get(r["row_id"]) or "\n\n".join(p for p in (pre, span, post) if p)
    rows.append({
        "id": r["row_id"], "doc": r["doc_id"], "date": r["doc_date"], "domain": r["domain"],
        "split": r["split"], "sheet": r["source_sheet"], "srow": r["source_row"],
        "pre": pre, "span": span, "post": post, "text": text,
        "e1": r["e1_event"], "e2": r["e2_event"],
        "rel_raw": r["rel_type_raw"], "rel": r["rel_type_v2"],
        "stance_raw": r["stance_raw"], "stance": r["stance_v2"],
        "flags": r["flags"], "p1": bool(r["rel_type_v2"]),
        "p2": r["in_stance_task"] == "True", "p3": r["in_actor_task"] == "True",
        "held": r["held_illegitimate"] == "True", "spans": sorted(spans.get(r["row_id"], [])),
    })

data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
html = TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"><title>Visionneuse des données</title>
<style>
:root{--ink:#1d2433;--mute:#6b7488;--line:#dfe3ec;--bg:#f6f7fb;--navy:#14284b;--gold:#f2c14e}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header{background:var(--navy);color:#fff;padding:12px 20px}header h1{margin:0;font-size:17px}
header small{color:#c8d1e4}
.wrap{display:grid;grid-template-columns:minmax(560px,1.1fr) 1fr;gap:14px;padding:14px 20px;height:calc(100vh - 56px)}
.panel{background:#fff;border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;min-height:0}
.filters{display:flex;flex-wrap:wrap;gap:8px;padding:10px;border-bottom:1px solid var(--line);background:#fafbfe}
.filters select,.filters input{font:inherit;padding:4px 6px;border:1px solid var(--line);border-radius:5px;background:#fff}
.filters input[type=search]{flex:1;min-width:140px}
.count{padding:6px 10px;color:var(--mute);border-bottom:1px solid var(--line);font-size:12px}
.tbl{overflow:auto;flex:1}table{border-collapse:collapse;width:100%}
th{position:sticky;top:0;background:#eef1f8;text-align:left;padding:6px 8px;font-size:12px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:5px 8px;border-bottom:1px solid #eef0f5;vertical-align:top}
tr.row{cursor:pointer}tr.row:hover{background:#f3f6ff}tr.sel{background:#fff6dc!important}
td.sp{max-width:340px;color:#394057}
.b{display:inline-block;padding:0 6px;border-radius:9px;font-size:11px;margin-right:2px;border:1px solid var(--line);background:#f1f3f9}
.b.CAUSES{background:#e3f1ff;border-color:#b9d9f8}.b.IS_CAUSED_BY{background:#ece6ff;border-color:#cdc1f5}
.b.LEGITIMATE{background:#e1f5e6;border-color:#b5e0bf}.b.NA{background:#eee}
.b.ILLEGITIMATE{background:#fde3e3;border-color:#f3b9b9}.b.on{background:var(--gold);border-color:#d9a82f}
.detail{overflow:auto;padding:14px 16px}.detail h2{margin:0 0 4px;font-size:16px}
.meta{color:var(--mute);font-size:12px;margin-bottom:10px}
.text{white-space:pre-wrap;background:#fbfbfd;border:1px solid var(--line);border-radius:6px;padding:10px;line-height:1.6}
.ctx{color:#8a93a6}.spn{background:#fff3c4}mark{background:#9fd8ff;border-radius:3px;padding:0 1px}
dl{display:grid;grid-template-columns:130px 1fr;gap:4px 10px;margin:12px 0}dt{color:var(--mute)}dd{margin:0;word-break:break-word}
.legend{font-size:12px;color:var(--mute);margin:6px 0 12px}.empty{padding:40px;color:var(--mute);text-align:center}
.flag{color:#a05a00}
@media(max-width:1000px){.wrap{grid-template-columns:1fr;height:auto}.panel{max-height:70vh}}
</style></head><body>
<header><h1>Les Détectives du Grand Livre — visionneuse des données <small id="sub"></small></h1></header>
<div id="loader" style="display:none;padding:10px 20px;background:#fff6dc;border-bottom:1px solid var(--line)">
 Chargez les fichiers locaux (ils ne quittent pas votre navigateur) :
 <label>annotations_v0.1.csv <input type="file" id="fann" accept=".csv"></label>
 <label>actors_v0.1.csv <input type="file" id="fact" accept=".csv"></label>
 <button id="fgo">Afficher</button> <span id="fmsg" style="color:#a05a00"></span>
</div>
<div class="wrap">
 <div class="panel">
  <div class="filters">
   <input type="search" id="q" placeholder="Rechercher dans le texte, les événements…">
   <select id="fdoc"><option value="">Document : tous</option></select>
   <select id="fsplit"><option value="">Split : tous</option><option>train</option><option>dev</option><option>test</option></select>
   <select id="fphase"><option value="">Phase : toutes</option><option value="p1">Phase 1 (cause)</option><option value="p2">Phase 2 (stance)</option><option value="p3">Phase 3 (acteurs)</option><option value="none">Dans aucune phase</option></select>
   <select id="frel"><option value="">Relation : toutes</option><option>CAUSES</option><option>IS_CAUSED_BY</option></select>
   <select id="fstance"><option value="">Stance : toutes</option><option>LEGITIMATE</option><option>NA</option><option>ILLEGITIMATE</option></select>
   <select id="fflag"><option value="">Drapeaux : tous</option><option value="any">avec drapeau</option><option value="rel_type_not_v2">rel_type_not_v2</option><option value="stance_unmappable">stance_unmappable</option><option value="window_not_span">window_not_span</option></select>
  </div>
  <div class="count" id="count"></div>
  <div class="tbl"><table><thead><tr><th>ID</th><th>Document</th><th>Split</th><th>Phases</th><th>Relation</th><th>Stance</th><th>Passage</th></tr></thead><tbody id="tb"></tbody></table></div>
 </div>
 <div class="panel"><div class="detail" id="detail"><div class="empty">Cliquez sur une ligne pour voir le texte, les étiquettes et les spans d'acteurs.</div></div></div>
</div>
<script>
let DATA = __DATA__;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const badge = (v, cls) => v ? `<span class="b ${esc(cls||v)}">${esc(v)}</span>` : '<span style="color:#b5bbc9">—</span>';
let selected = null;
function init() {
  const docs = [...new Set(DATA.map(r => r.doc))].sort();
  $('fdoc').innerHTML = '<option value="">Document : tous</option>';
  docs.forEach(d => $('fdoc').insertAdjacentHTML('beforeend', `<option>${esc(d)}</option>`));
  $('sub').textContent = DATA.length ? `· ${DATA.length} lignes · ${docs.length} documents` : '· aucune donnée chargée';
  $('loader').style.display = DATA.length ? 'none' : 'block';
}
// --- loading local CSV files (index.html ships without data) ---
function parseCSV(s) {
  const rows = []; let row = [], f = '', q = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === '"') { if (s[i+1] === '"') { f += '"'; i++; } else q = false; } else f += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(f); f = ''; }
    else if (c === '\n') { row.push(f); rows.push(row); row = []; f = ''; }
    else if (c !== '\r') f += c;
  }
  if (f.length || row.length) { row.push(f); rows.push(row); }
  return rows;
}
function objs(s) { const r = parseCSV(s), h = r[0]; return r.slice(1).filter(x => x.length === h.length).map(x => Object.fromEntries(h.map((k, i) => [k, x[i]]))); }
function build(ann, act) {
  const spans = {}, texts = {};
  act.forEach(a => { (spans[a.row_id] = spans[a.row_id] || []).push([+a.start, +a.end]); texts[a.row_id] = a.text; });
  return ann.map(r => ({
    id: r.row_id, doc: r.doc_id, date: r.doc_date, domain: r.domain, split: r.split,
    sheet: r.source_sheet, srow: r.source_row, pre: r.pre_context, span: r.span_text, post: r.post_context,
    text: texts[r.row_id] || [r.pre_context, r.span_text, r.post_context].filter(Boolean).join('\n\n'),
    e1: r.e1_event, e2: r.e2_event, rel_raw: r.rel_type_raw, rel: r.rel_type_v2,
    stance_raw: r.stance_raw, stance: r.stance_v2, flags: r.flags, p1: !!r.rel_type_v2,
    p2: r.in_stance_task === 'True', p3: r.in_actor_task === 'True', held: r.held_illegitimate === 'True',
    spans: (spans[r.row_id] || []).sort((a, b) => a[0] - b[0] || a[1] - b[1])}));
}
$('fgo').addEventListener('click', async () => {
  const a = $('fann').files[0], b = $('fact').files[0];
  if (!a || !b) { $('fmsg').textContent = 'Choisissez les deux fichiers.'; return; }
  try { DATA = build(objs(await a.text()), objs(await b.text())); $('fmsg').textContent = ''; init(); render(); }
  catch (e) { $('fmsg').textContent = 'Fichiers illisibles : ' + e.message; }
});

function filtered() {
  const q = $('q').value.trim().toLowerCase(), doc = $('fdoc').value, sp = $('fsplit').value,
        ph = $('fphase').value, rel = $('frel').value, st = $('fstance').value, fl = $('fflag').value;
  return DATA.filter(r => {
    if (doc && r.doc !== doc) return false;
    if (sp && r.split !== sp) return false;
    if (ph === 'none' ? (r.p1 || r.p2 || r.p3) : ph && !r[ph]) return false;
    if (rel && r.rel !== rel) return false;
    if (st && r.stance !== st) return false;
    if (fl === 'any' ? !r.flags : fl && !r.flags.split(';').includes(fl)) return false;
    if (q && !(r.text + ' ' + r.e1 + ' ' + r.e2 + ' ' + r.id).toLowerCase().includes(q)) return false;
    return true;
  });
}
function render() {
  const rows = filtered();
  $('count').textContent = `${rows.length} ligne(s) affichée(s) sur ${DATA.length}`;
  $('tb').innerHTML = rows.map(r => {
    const ph = ['p1','p2','p3'].map((p,i) => r[p] ? `<span class="b on">P${i+1}</span>` : '').join('');
    const stance = r.held ? badge('ILLEGITIMATE') : badge(r.p2 ? r.stance : '');
    return `<tr class="row ${selected===r.id?'sel':''}" data-id="${r.id}"><td>${r.id}</td><td>${esc(r.doc)}</td><td>${r.split||'—'}</td><td>${ph||'—'}</td><td>${badge(r.rel)}</td><td>${stance}</td><td class="sp">${esc(r.span.slice(0,150))}${r.span.length>150?'…':''}</td></tr>`;
  }).join('');
}
function highlight(r) {
  // text = [pre \n\n] span [\n\n post]; actor spans are offsets into text.
  const t = r.text, s0 = r.pre ? r.pre.length + 2 : 0, s1 = s0 + r.span.length;
  const marks = new Array(t.length + 1).fill(0);
  r.spans.forEach(([a, b]) => { for (let i = a; i < b && i < t.length; i++) marks[i] = 1; });
  let out = '', i = 0;
  while (i < t.length) {
    const zone = i < s0 ? 'ctx' : i < s1 ? 'spn' : 'ctx', m = marks[i];
    let j = i;
    while (j < t.length && (j < s0 ? 'ctx' : j < s1 ? 'spn' : 'ctx') === zone && marks[j] === m) j++;
    let seg = esc(t.slice(i, j));
    if (m) seg = `<mark>${seg}</mark>`;
    out += `<span class="${zone}">${seg}</span>`;
    i = j;
  }
  return out;
}
function show(id) {
  const r = DATA.find(x => x.id === id); selected = id; render();
  const spanList = r.spans.length ? r.spans.map(([a,b]) => `<div>[${a}–${b}] <mark>${esc(r.text.slice(a,b))}</mark></div>`).join('') : '—';
  $('detail').innerHTML = `
   <h2>${r.id} <small style="color:var(--mute);font-weight:400">· ${esc(r.doc)} · ${esc(r.date)} · ${r.domain}</small></h2>
   <div class="meta">Feuille « ${esc(r.sheet)} », ligne ${r.srow} · split : ${r.split||'—'} · ${['p1','p2','p3'].map((p,i)=>r[p]?'P'+(i+1):'').filter(Boolean).join(' ')||'aucune phase'}${r.held?' · ILLEGITIMATE mise de côté':''}</div>
   <div class="legend">Texte : <span class="ctx">contexte</span> · <span class="spn">passage annoté</span> · <mark>span d'acteur (phase 3)</mark></div>
   <div class="text">${highlight(r)}</div>
   <dl>
    <dt>Événement 1</dt><dd>${esc(r.e1)||'—'}</dd>
    <dt>Événement 2</dt><dd>${esc(r.e2)||'—'}</dd>
    <dt>Relation</dt><dd>${badge(r.rel)} <span style="color:var(--mute)">(valeur d'origine : ${esc(r.rel_raw)||'—'})</span></dd>
    <dt>Stance</dt><dd>${badge(r.stance)} <span style="color:var(--mute)">(valeur d'origine : ${esc(r.stance_raw)||'—'})</span></dd>
    <dt>Drapeaux</dt><dd class="flag">${esc(r.flags)||'—'}</dd>
    <dt>Spans d'acteurs</dt><dd>${spanList}</dd>
   </dl>`;
}
$('tb').addEventListener('click', e => { const tr = e.target.closest('tr.row'); if (tr) show(tr.dataset.id); });
['q','fdoc','fsplit','fphase','frel','fstance','fflag'].forEach(id => $(id).addEventListener('input', render));
init(); render();
</script></body></html>"""
(ROOT / "viewer").mkdir(exist_ok=True)
(ROOT / "viewer/viewer-local.html").write_text(html.replace("__DATA__", data), encoding="utf-8")
(ROOT / "viewer/index.html").write_text(html.replace("__DATA__", "[]"), encoding="utf-8")
print("wrote viewer/viewer-local.html (embedded,", len(rows), "rows) and viewer/index.html (no data)")
