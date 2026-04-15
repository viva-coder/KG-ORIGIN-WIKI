from flask import Flask, jsonify, render_template
import os
import psycopg2

app = Flask(__name__)

# This pulls the connection string from your Render Environment Variables
DATABASE_URL = os.environ.get('DATABASE_URL')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph')
def get_graph():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. Fetch the 32+ Wiki Nodes
        cur.execute("SELECT id, label, category, notes FROM origin_nodes")
        nodes = [{"id": r[0], "label": r[1], "category": r[2], "notes": r[3]} for r in cur.fetchall()]
        
        # 2. Fetch any connections (edges)
        cur.execute("SELECT source, target FROM origin_edges")
        edges = [{"source": r[0], "target": r[1]} for r in cur.fetchall()]
        
        cur.close()
        conn.close()
        return jsonify({"nodes": nodes, "edges": edges})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Local testing use only; Render uses Gunicorn
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
