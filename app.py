import os, json, re
from flask import Flask, jsonify, request, send_from_directory, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, static_folder='static')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# ── All 29 wiki pages as seed nodes ──────────────────────────────────────────
SEED_NODES = [
  # Event Vision & Philosophy
  {"id":"complete-ai-system","label":"Complete AI System","category":"Event Vision & Philosophy","url":"","tags":"ai,system,infrastructure","notes":"Full AI system architecture for ORIGIN"},
  {"id":"content-strategy-overview","label":"Content Strategy Overview","category":"Event Vision & Philosophy","url":"","tags":"content,strategy","notes":"High-level overview of ORIGIN content plan"},
  {"id":"dashboard","label":"Dashboard","category":"Event Vision & Philosophy","url":"","tags":"dashboard,metrics","notes":"ORIGIN metrics and coordination dashboard"},
  {"id":"dr-zach-bush","label":"Dr. Zach Bush (Vision)","category":"Event Vision & Philosophy","url":"","tags":"science,regeneration,medicine","notes":"Scientific foundation for ORIGIN's mission"},
  {"id":"handoff","label":"Handoff","category":"Event Vision & Philosophy","url":"","tags":"operations,handoff","notes":"Project handoff and continuity documentation"},
  {"id":"keystone-species","label":"Keystone Species","category":"Event Vision & Philosophy","url":"","tags":"ecology,trophic,keystone","notes":"Humanity as regenerative keystone species"},
  {"id":"kg-public","label":"Knowledge Graph (Public)","category":"Event Vision & Philosophy","url":"","tags":"knowledge,graph,public","notes":"Public-facing knowledge graph"},
  {"id":"origin-knowledge-graph","label":"ORIGIN Knowledge Graph","category":"Event Vision & Philosophy","url":"","tags":"knowledge,graph,internal","notes":"Internal knowledge mapping system"},
  {"id":"origin-claude-handoff","label":"Claude Handoff","category":"Event Vision & Philosophy","url":"","tags":"ai,claude,handoff","notes":"Instructions for Claude AI vault assistant"},
  {"id":"pillars","label":"ORIGIN Pillars","category":"Event Vision & Philosophy","url":"","tags":"pillars,vision,philosophy","notes":"Core pillars of the ORIGIN movement"},
  {"id":"project-biome-regen-landing","label":"Project Biome Regeneration (LP)","category":"Event Vision & Philosophy","url":"","tags":"biome,regeneration,fundraising","notes":"Landing page for biome regeneration fundraising"},
  {"id":"project-biome-regen","label":"Project Biome Regeneration","category":"Event Vision & Philosophy","url":"","tags":"biome,regeneration,ecology","notes":"Full biome regeneration project documentation"},
  # Key Figures
  {"id":"chris-deckker","label":"Chris Deckker","category":"Key Figures","url":"","tags":"founder,earthdance,guide","notes":"ORIGIN founder. Trusted guide. Earthdance legacy."},
  {"id":"dr-zach-bush-landingpage","label":"Dr. Zach Bush MD (Profile)","category":"Key Figures","url":"","tags":"medicine,regeneration,science","notes":"Biology of Connection. Primary scientific authority."},
  {"id":"elder-ailton-krenak","label":"Elder Ailton Krenak","category":"Key Figures","url":"","tags":"indigenous,elder,brazil","notes":"Indigenous wisdom. South American elder voice."},
  # Glossary Concepts
  {"id":"earthdance-legacy","label":"Earthdance Legacy","category":"Glossary Concepts","url":"","tags":"earthdance,history,1996","notes":"Proven track record of synchronised global events"},
  {"id":"global-consciousness-project","label":"Global Consciousness Project","category":"Glossary Concepts","url":"","tags":"consciousness,science,GCP","notes":"Scientific basis for collective human attention effects"},
  # Location Profiles
  {"id":"cradle-of-humankind","label":"Cradle of Humankind","category":"Location Profiles","url":"https://ourorigin.earth","tags":"south africa,sacred,birthplace","notes":"Sacred anchor. Birthplace of humanity. October 17 2026 site."},
  # Marketing & SEO
  {"id":"brand","label":"Brand Guidelines","category":"Marketing & SEO","url":"","tags":"brand,identity,voice","notes":"ORIGIN brand voice and identity guidelines"},
  {"id":"earthdance-cathedral","label":"Earthdance 96 — Digital Cathedral","category":"Marketing & SEO","url":"","tags":"earthdance,seo,authority","notes":"How Earthdance 96 functions as authority anchor"},
  {"id":"glossary-pages","label":"Glossary Pages Strategy","category":"Marketing & SEO","url":"","tags":"glossary,seo,traffic","notes":"Powerhouse glossary pages for organic traffic"},
  {"id":"master-content-strategy","label":"Master Content Strategy","category":"Marketing & SEO","url":"","tags":"content,seo,strategy","notes":"Full content strategy framework"},
  {"id":"origin-digital-strategy","label":"Sacred Infrastructure Strategy","category":"Marketing & SEO","url":"","tags":"digital,authority,EEAT","notes":"Building digital authority through sacred infrastructure"},
  {"id":"origin-global-movement","label":"Global Movement Strategy","category":"Marketing & SEO","url":"","tags":"marketing,movement,framework","notes":"Complete marketing strategy and content framework"},
  {"id":"regenerative-agriculture","label":"Regenerative Agriculture","category":"Marketing & SEO","url":"","tags":"agriculture,soil,regeneration","notes":"Dr. Zach Bush's core expertise area"},
  {"id":"seo-keystone-species","label":"SEO: Keystone Species","category":"Marketing & SEO","url":"","tags":"seo,keystone,keywords","notes":"SEO strategy for keystone species content"},
  {"id":"website-origin-kg","label":"Website Knowledge Graph","category":"Marketing & SEO","url":"https://ourorigin.earth","tags":"website,knowledge,graph","notes":"Digital presence knowledge graph strategy"},
  # Content & Social Media
  {"id":"menu-youtube-playlists","label":"Menu & YouTube Playlists","category":"Content & Social Media","url":"","tags":"youtube,playlists,content","notes":"YouTube content organisation and menus"},
  {"id":"social-media-hook-guide","label":"Social Media Hook Guide","category":"Content & Social Media","url":"","tags":"social,hooks,copywriting","notes":"Proven hook formulas for social media posts"},
]

SEED_EDGES = [
  # October 17 2026 as temporal anchor (connects to everything)
  ("pillars","cradle-of-humankind"),
  ("pillars","project-biome-regen"),
  ("pillars","global-consciousness-project"),
  ("pillars","chris-deckker"),
  # Regenerative systems
  ("project-biome-regen","dr-zach-bush-landingpage"),
  ("project-biome-regen","keystone-species"),
  ("project-biome-regen","regenerative-agriculture"),
  ("project-biome-regen-landing","project-biome-regen"),
  ("project-biome-regen-landing","dr-zach-bush-landingpage"),
  # Dr Zach Bush science cluster
  ("dr-zach-bush","dr-zach-bush-landingpage"),
  ("dr-zach-bush-landingpage","regenerative-agriculture"),
  ("dr-zach-bush-landingpage","keystone-species"),
  # Chris Deckker + Earthdance
  ("chris-deckker","earthdance-legacy"),
  ("chris-deckker","earthdance-cathedral"),
  ("earthdance-legacy","content-strategy-overview"),
  ("earthdance-legacy","global-consciousness-project"),
  # Global consciousness
  ("global-consciousness-project","dashboard"),
  ("global-consciousness-project","cradle-of-humankind"),
  # Digital strategy cluster
  ("origin-digital-strategy","website-origin-kg"),
  ("origin-digital-strategy","master-content-strategy"),
  ("origin-digital-strategy","origin-global-movement"),
  ("origin-digital-strategy","glossary-pages"),
  ("origin-digital-strategy","elder-ailton-krenak"),
  ("origin-digital-strategy","dr-zach-bush-landingpage"),
  # SEO cluster
  ("seo-keystone-species","keystone-species"),
  ("glossary-pages","global-consciousness-project"),
  ("glossary-pages","cradle-of-humankind"),
  ("glossary-pages","keystone-species"),
  ("master-content-strategy","content-strategy-overview"),
  ("master-content-strategy","origin-global-movement"),
  # Knowledge graph cluster
  ("origin-knowledge-graph","kg-public"),
  ("origin-knowledge-graph","origin-claude-handoff"),
  ("origin-claude-handoff","complete-ai-system"),
  ("handoff","origin-claude-handoff"),
  # Elder voices
  ("elder-ailton-krenak","pillars"),
  ("elder-ailton-krenak","cradle-of-humankind"),
  # Content / social
  ("social-media-hook-guide","master-content-strategy"),
  ("menu-youtube-playlists","content-strategy-overview"),
  ("brand","origin-digital-strategy"),
  ("brand","master-content-strategy"),
]

# ── DB helpers ────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    if not DATABASE_URL:
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            category TEXT,
            url TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS edges (
            id SERIAL PRIMARY KEY,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            UNIQUE(source, target)
        );
    """)
    # Seed nodes
    for n in SEED_NODES:
        cur.execute("""
            INSERT INTO nodes (id,label,category,url,tags,notes)
            VALUES (%(id)s,%(label)s,%(category)s,%(url)s,%(tags)s,%(notes)s)
            ON CONFLICT (id) DO NOTHING
        """, n)
    # Seed edges
    for s,t in SEED_EDGES:
        cur.execute("""
            INSERT INTO edges (source,target) VALUES (%s,%s)
            ON CONFLICT DO NOTHING
        """, (s,t))
    conn.commit()
    cur.close()
    conn.close()

# ── In-memory fallback (no DB) ────────────────────────────────────────────────
mem_nodes = {n['id']: n.copy() for n in SEED_NODES}
mem_edges = list(SEED_EDGES)

def get_all_nodes():
    if not DATABASE_URL:
        return list(mem_nodes.values())
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM nodes ORDER BY category, label")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows

def get_all_edges():
    if not DATABASE_URL:
        return [{"source":s,"target":t} for s,t in mem_edges]
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT source, target FROM edges")
    rows = [dict(r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return rows

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/graph')
def api_graph():
    return jsonify({"nodes": get_all_nodes(), "edges": get_all_edges()})

@app.route('/api/nodes', methods=['POST'])
def add_node():
    data = request.json
    nid = re.sub(r'[^a-z0-9-]', '-', data.get('label','').lower()).strip('-') or 'node'
    node = {"id":nid,"label":data.get('label',''),"category":data.get('category',''),"url":data.get('url',''),"tags":data.get('tags',''),"notes":data.get('notes','')}
    if DATABASE_URL:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("INSERT INTO nodes (id,label,category,url,tags,notes) VALUES (%(id)s,%(label)s,%(category)s,%(url)s,%(tags)s,%(notes)s) ON CONFLICT (id) DO UPDATE SET label=%(label)s,category=%(category)s,url=%(url)s,tags=%(tags)s,notes=%(notes)s,updated_at=NOW()", node)
        conn.commit(); cur.close(); conn.close()
    else:
        mem_nodes[nid] = node
    return jsonify(node)

@app.route('/api/nodes/<node_id>', methods=['PUT'])
def update_node(node_id):
    data = request.json
    if DATABASE_URL:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("UPDATE nodes SET label=%(label)s,category=%(category)s,url=%(url)s,tags=%(tags)s,notes=%(notes)s,updated_at=NOW() WHERE id=%(id)s", {**data,"id":node_id})
        conn.commit(); cur.close(); conn.close()
    else:
        if node_id in mem_nodes: mem_nodes[node_id].update(data)
    return jsonify({"ok":True})

@app.route('/api/nodes/<node_id>', methods=['DELETE'])
def delete_node(node_id):
    if DATABASE_URL:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("DELETE FROM edges WHERE source=%s OR target=%s",(node_id,node_id))
        cur.execute("DELETE FROM nodes WHERE id=%s",(node_id,))
        conn.commit(); cur.close(); conn.close()
    else:
        mem_nodes.pop(node_id, None)
        mem_edges[:] = [(s,t) for s,t in mem_edges if s!=node_id and t!=node_id]
    return jsonify({"ok":True})

@app.route('/api/edges', methods=['POST'])
def add_edge():
    data = request.json
    s,t = data.get('source',''), data.get('target','')
    if DATABASE_URL:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("INSERT INTO edges (source,target) VALUES (%s,%s) ON CONFLICT DO NOTHING",(s,t))
        conn.commit(); cur.close(); conn.close()
    else:
        if (s,t) not in mem_edges: mem_edges.append((s,t))
    return jsonify({"ok":True})

@app.route('/api/edges', methods=['DELETE'])
def delete_edge():
    data = request.json
    s,t = data.get('source',''), data.get('target','')
    if DATABASE_URL:
        conn=get_conn(); cur=conn.cursor()
        cur.execute("DELETE FROM edges WHERE source=%s AND target=%s",(s,t))
        conn.commit(); cur.close(); conn.close()
    else:
        mem_edges[:] = [(a,b) for a,b in mem_edges if not (a==s and b==t)]
    return jsonify({"ok":True})

if __name__ == '__main__':
    try: init_db()
    except Exception as e: print(f"DB init skipped: {e}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
