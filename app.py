from flask import Flask, jsonify, render_template
import os
import psycopg2

app = Flask(__name__)

# Fetch the URL from Render Environment Variables
DATABASE_URL = os.environ.get('DATABASE_URL')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/graph')
def get_graph():
    try:
        # Check if URL exists
        if not DATABASE_URL:
            return jsonify({"error": "DATABASE_URL is missing from environment variables"}), 500
            
        # Ensure SSL is required for Neon
        conn_url = DATABASE_URL
        if "sslmode=" not in conn_url:
            conn_url += "?sslmode=require"

        conn = psycopg2.connect(conn_url)
        cur = conn.cursor()
        
        # Pull nodes
        cur.execute("SELECT id, label, category, notes FROM origin_nodes")
        nodes = [{"id": r[0], "label": r[1], "category": r[2], "notes": r[3]} for r in cur.fetchall()]
        
        # Pull edges
        cur.execute("SELECT source, target FROM origin_edges")
        edges = [{"source": r[0], "target": r[1]} for r in cur.fetchall()]
        
        cur.close()
        conn.close()
        return jsonify({"nodes": nodes, "edges": edges})
        
    except Exception as e:
        # This will print the SPECIFIC error in your browser so we can fix it
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
