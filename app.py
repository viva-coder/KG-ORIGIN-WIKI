import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='static')

# ── Configuration ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# ── Seed Data (The 29 Pillars of ORIGIN) ──────────────────────────────────────
SEED_NODES = [
    {"id": "origin-event-vision", "label": "ORIGIN Event Vision", "category": "Event Vision & Philosophy", "notes": "The core intentionality of the gathering."},
    {"id": "dr-zach-bush", "label": "Dr. Zach Bush", "category": "Key Figures", "notes": "Keynote speaker on regenerative health and soil."},
    {"id": "synchronized-meditation", "label": "Synchronized Meditation", "category": "Glossary Concepts", "notes": "Global coherence event."},
    {"id": "amazon-basin-venue", "label": "Amazon Basin Venue", "category": "Location Profiles", "notes": "Primary location for the 2026 gathering."},
    {"id": "origin-digital-strategy", "label": "Origin Digital Strategy", "category": "Marketing & SEO", "notes": "The architecture of our online presence."},
    {"id": "sacred-commerce", "label": "Sacred Commerce", "category": "Event Vision & Philosophy"},
    {"id": "chris-deckker", "label": "Chris Deckker", "category": "Key Figures"},
    {"id": "soil-regeneration", "label": "Soil Regeneration", "category": "Glossary Concepts"},
    {"id": "bioluminescent-forest", "label": "Bioluminescent Forest", "category": "Location Profiles"},
    {"id": "social-media-roadmap", "label": "Social Media Roadmap", "category": "Content & Social Media"},
    # ... Add all other 19 nodes following this pattern ...
]

SEED_EDGES = [
    {"source": "dr-zach-bush", "target": "soil-regeneration"},
    {"source": "origin-event-vision", "target": "sacred-commerce"},
    {"source": "origin-digital-strategy", "target": "social-media-roadmap"},
    {"source": "chris-deckker", "target": "origin-event-vision"}
    # ... Add your other mapped connections ...
]

# ── Database Handshake ────────────────────────────────────────────────────────
def get_db_connection():
    uri = DATABASE_URL
    # SQLAlchemy/Postgres standard fix for Render
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(uri, cursor_factory=RealDictCursor)

def init_db():
    """Wipes old structure and seeds the 29 nodes for a fresh deploy."""
    if not DATABASE_URL:
        print("No DATABASE_URL found. Running in-memory mode is not supported in this script version.")
        return

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Clean slate to fix the 'label column does not exist' error
    cur.execute("DROP TABLE IF EXISTS edges CASCADE;")
    cur.execute("DROP TABLE IF EXISTS nodes CASCADE;")
    
    cur.execute('''
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            category TEXT,
            url TEXT,
            tags TEXT,
            notes TEXT
        );
    ''')
    cur.execute('''
        CREATE TABLE edges (
            id SERIAL PRIMARY KEY,
            source TEXT REFERENCES nodes(id) ON DELETE CASCADE,
            target TEXT REFERENCES nodes(id) ON DELETE CASCADE
        );
    ''')
    
    # Insert Seed Nodes
    for n in SEED_NODES:
        cur.execute(
            "INSERT INTO nodes (id, label, category, url, tags, notes) VALUES (%s, %s, %s, %s, %s, %s)",
            (n['id'], n['label'], n['category'], n.get('url',''), n.get('tags',''), n.get('notes',''))
        )
    
    # Insert Seed Edges
    for e in SEED_EDGES:
        cur.execute("INSERT INTO edges (source, target) VALUES (%s, %s)", (e['source'], e['target']))
        
    conn.commit()
    cur.close()
    conn.close()
    print("Database Initialized and Seeded.")

# ── All 29 wiki pages as seed nodes ──────────────────────────────────────────
SEED_NODES = [
    {"id": "origin-event-vision", "label": "ORIGIN Event Vision", "category": "Event Vision & Philosophy", "notes": "Core intentionality and spiritual foundation."},
    {"id": "sacred-commerce", "label": "Sacred Commerce", "category": "Event Vision & Philosophy", "notes": "New paradigm of exchange."},
    {"id": "ancient-future-tech", "label": "Ancient-Future Technology", "category": "Event Vision & Philosophy", "notes": "Bridging ancestral wisdom with modern tools."},
    {"id": "collective-coherence", "label": "Collective Coherence", "category": "Event Vision & Philosophy", "notes": "The science of group meditation."},
    {"id": "dr-zach-bush", "label": "Dr. Zach Bush", "category": "Key Figures", "notes": "Regenerative health and soil expert."},
    {"id": "chris-deckker", "label": "Chris Deckker", "category": "Key Figures", "notes": "Founder and Visionary."},
    {"id": "aubrey-marcus", "label": "Aubrey Marcus", "category": "Key Figures", "notes": "Philosopher and community builder."},
    {"id": "charles-eisenstein", "label": "Charles Eisenstein", "category": "Key Figures", "notes": "Author of Sacred Economics."},
    {"id": "synchronized-meditation", "label": "Synchronized Meditation", "category": "Glossary Concepts", "notes": "Global coherence event."},
    {"id": "soil-regeneration", "label": "Soil Regeneration", "category": "Glossary Concepts", "notes": "The literal 'Origin' of life."},
    {"id": "bioregionalism", "label": "Bioregionalism", "category": "Glossary Concepts", "notes": "Living within the natural boundaries of land."},
    {"id": "mycelial-networking", "label": "Mycelial Networking", "category": "Glossary Concepts", "notes": "Organic structure of communication."},
    {"id": "amazon-basin-venue", "label": "Amazon Basin Venue", "category": "Location Profiles", "notes": "Primary sacred site."},
    {"id": "costa-rica-sanctuary", "label": "Costa Rica Sanctuary", "category": "Location Profiles", "notes": "Secondary retreat site."},
    {"id": "bioluminescent-forest", "label": "Bioluminescent Forest", "category": "Location Profiles", "notes": "Immersive nature experience."},
    {"id": "high-altitude-temple", "label": "High Altitude Temple", "category": "Location Profiles", "notes": "Sky-based meditation space."},
    {"id": "origin-digital-strategy", "label": "Origin Digital Strategy", "category": "Marketing & SEO", "notes": "SEO and digital growth architecture."},
    {"id": "keyword-clusters", "label": "Keyword Clusters", "category": "Marketing & SEO", "notes": "Regen-ag and spirituality SEO."},
    {"id": "backlink-ecosystem", "label": "Backlink Ecosystem", "notes": "Organic reach and authority."},
    {"id": "content-pillar-pages", "label": "Content Pillar Pages", "category": "Marketing & SEO"},
    {"id": "social-media-roadmap", "label": "Social Media Roadmap", "category": "Content & Social Media"},
    {"id": "visual-storytelling", "label": "Visual Storytelling", "category": "Content & Social Media"},
    {"id": "influencer-alignments", "label": "Influencer Alignments", "category": "Content & Social Media"},
    {"id": "community-spotlights", "label": "Community Spotlights", "category": "Content & Social Media"},
    {"id": "podcast-synergy", "label": "Podcast Synergy", "category": "Content & Social Media"},
    {"id": "newsletter-architecture", "label": "Newsletter Architecture", "category": "Content & Social Media"},
    {"id": "user-generated-wisdom", "label": "User Generated Wisdom", "category": "Content & Social Media"},
    {"id": "impact-reporting", "label": "Impact Reporting", "category": "Event Vision & Philosophy"},
    {"id": "global-village-model", "label": "Global Village Model", "category": "Glossary Concepts"}
]

SEED_EDGES = [
    {"source": "dr-zach-bush", "target": "soil-regeneration"},
    {"source": "chris-deckker", "target": "origin-event-vision"},
    {"source": "origin-event-vision", "target": "sacred-commerce"},
    {"source": "sacred-commerce", "target": "charles-eisenstein"},
    {"source": "origin-digital-strategy", "target": "content-pillar-pages"},
    {"source": "origin-digital-strategy", "target": "social-media-roadmap"},
    {"source": "synchronized-meditation", "target": "collective-coherence"},
    {"source": "amazon-basin-venue", "target": "bioluminescent-forest"},
    {"source": "soil-regeneration", "target": "bioregionalism"},
    {"source": "aubrey-marcus", "target": "podcast-synergy"},
    {"source": "origin-event-vision", "target": "impact-reporting"}
]

# ── API Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM nodes")
    nodes = cur.fetchall()
    cur.execute("SELECT source, target FROM edges")
    edges = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({'nodes': nodes, 'edges': edges})

@app.route('/api/nodes', methods=['POST'])
def add_node():
    data = request.json
    node_id = re.sub(r'[^a-z0-9]+', '-', data['label'].lower()).strip('-')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nodes (id, label, category, url, tags, notes) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
        (node_id, data['label'], data['category'], data.get('url',''), data.get('tags',''), data.get('notes',''))
    )
    new_node = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_node)

@app.route('/api/nodes/<node_id>', methods=['PUT', 'DELETE'])
def handle_node(node_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'DELETE':
        cur.execute("DELETE FROM nodes WHERE id = %s", (node_id,))
        res = {'status': 'deleted'}
    else:
        data = request.json
        cur.execute(
            "UPDATE nodes SET label=%s, category=%s, url=%s, tags=%s, notes=%s WHERE id=%s RETURNING *",
            (data['label'], data['category'], data.get('url',''), data.get('tags',''), data.get('notes',''), node_id)
        )
        res = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(res)

@app.route('/api/edges', methods=['POST'])
def add_edge():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO edges (source, target) VALUES (%s, %s) RETURNING *", (data['source'], data['target']))
    new_edge = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_edge)

# ── Execution ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # On first run or when structure changes, uncomment the next line:
    init_db() 
    app.run(debug=True, port=10000)
