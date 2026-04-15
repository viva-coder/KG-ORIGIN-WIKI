# ORIGIN Knowledge Graph

Interactive force-directed knowledge graph for all 29 ORIGIN wiki pages — drag, zoom, filter, edit, connect.

## Features
- 🌿 Force-directed D3 graph — drag, zoom, pan
- 🔍 Search + filter by category
- 🖱️ Click any node to open its side panel
- ✏️ Edit label, category, URL, tags, notes in-browser
- 🔗 "Link pages" mode — click two nodes to connect them
- ➕ Add new nodes (sidebar button or double-click canvas)
- 🗑️ Delete nodes
- 💾 All data saved to PostgreSQL (persists forever)
- Works without a database too (in-memory fallback with all 29 pages pre-loaded)

## Deploy to Render (one-click Blueprint)

1. Push all these files to your GitHub repo root
2. Go to [render.com](https://render.com) → New → **Blueprint**
3. Connect your GitHub repo
4. Click **Apply** — creates both web service AND PostgreSQL database automatically
5. Wait ~3 minutes → your URL is live

## Manual Render setup

### Step 1: Create PostgreSQL database
- Render dashboard → New → PostgreSQL
- Name: `origin-kg-db`  
- Plan: Free
- Copy the **Internal Database URL**

### Step 2: Create Web Service

| Field | Value |
|-------|-------|
| **Name** | `origin-knowledge-graph` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| **Plan** | Free |

### Step 3: Add environment variable
- Key: `DATABASE_URL`
- Value: Internal Database URL from Step 1

### Step 4: Deploy
Click **Create Web Service** — done!

## Local development

```bash
pip install -r requirements.txt
# With database:
export DATABASE_URL="postgresql://user:pass@localhost/origin_kg"
# Without database (in-memory, all 29 pages pre-loaded):
python app.py
# → open http://localhost:5000
```

## Navigation

- **Drag** nodes to rearrange
- **Scroll** to zoom in/out
- **Click** a node to open its detail panel
- **Double-click** canvas to add a new page
- **F key** to zoom-fit all nodes
- **Escape** to close panels
- **Link pages** button → click source node, then target node to draw a connection
- Category chips in sidebar filter the graph

## ORIGIN Wiki Categories

| Category | Colour |
|----------|--------|
| Event Vision & Philosophy | Gold |
| Key Figures | Sage green |
| Glossary Concepts | Purple |
| Location Profiles | Blue |
| Marketing & SEO | Coral |
| Content & Social Media | Amber |

---

*ourorigin.earth · October 17, 2026 · Ancient + Future · Hopeful · Grounded*
