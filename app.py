import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='static')

# ── Configuration ────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

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
    {"id": "backlink-ecosystem", "label": "Backlink Ecosystem", "category": "Marketing & SEO", "notes": "Organic reach and authority."},
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

# ── Database Handshake ────────────────────────────────────────────────────────
def get_db_connection():
    uri = DATABASE_URL
    if not uri:
        return None
    # Standard fix for Postgres URI formatting
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(uri, cursor_factory=RealDictCursor)

def init_db():
    """Builds the ORIGIN schema and seeds initial content."""
    conn = get_db_connection()
    if not conn:
        print("DATABASE_URL not found. Skipping initialization.")
        return
    
    cur = conn.cursor()
    print("Dropping old ORIGIN tables if they exist...")
    cur.execute("DROP TABLE IF EXISTS origin_edges CASCADE;")
    cur.execute("DROP TABLE IF EXISTS origin_nodes CASCADE;")
    
    print("Creating fresh ORIGIN tables...")
    cur.execute('''
        CREATE TABLE origin_nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            category TEXT,
            url TEXT,
            tags TEXT,
            notes TEXT
        );
    ''')
    cur.execute('''
        CREATE TABLE origin_edges (
            id SERIAL PRIMARY KEY,
            source TEXT REFERENCES origin_nodes(id) ON DELETE CASCADE,
            target TEXT
        );
    ''')
    
    print(f"Seeding {len(SEED_NODES)} nodes...")
    for n in SEED_NODES:
        cur.execute("INSERT INTO origin_nodes (id, label, category, url, tags, notes) VALUES (%s, %s, %s, %s, %s, %s)",
            (n['id'], n['label'], n['category'], n.get('url',''), n.get('tags',''), n.get('notes','')))
    
    for e in SEED_EDGES:
        cur.execute("INSERT INTO origin_edges (source, target) VALUES (%s, %s)", (e['source'], e['target']))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database Seeded Successfully!")

# ── API Routes ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM origin_nodes ORDER BY category, label")
    nodes = cur.fetchall()
    cur.execute("SELECT source, target FROM origin_edges")
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
    cur.execute("INSERT INTO origin_nodes (id, label, category, url, tags, notes) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *",
        (node_id, data['label'], data['category'], data.get('url',''), data.get('tags',''), data.get('notes','')))
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
        cur.execute("DELETE FROM origin_nodes WHERE id = %s", (node_id,))
        res = {'status': 'deleted'}
    else:
        data = request.json
        cur.execute("UPDATE origin_nodes SET label=%s, category=%s, url=%s, tags=%s, notes=%s WHERE id=%s RETURNING *",
            (data['label'], data['category'], data.get('url',''), data.get('tags',''), data.get('notes',''), node_id))
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
    cur.execute("INSERT INTO origin_edges (source, target) VALUES (%s, %s) RETURNING *", (data['source'], data['target']))
    new_edge = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_edge)

# ── Startup Execution ────────────────────────────────────────────────────────

# We call this outside the __name__ == '__main__' block so that Render's 
# production server (Gunicorn) executes it immediately upon import.
try:
    init_db()
except Exception as startup_err:
    print(f"Non-critical startup error: {startup_err}")

if __name__ == '__main__':
    app.run(debug=True, port=10000)
