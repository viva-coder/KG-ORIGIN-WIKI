import os
import re
import psycopg2

# 1. Get your Neon URL from your Environment Variables
DATABASE_URL = os.environ.get('DATABASE_URL')

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def import_markdown_files(folder_path):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print(f"Scanning folder: {folder_path}")
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract Title (Assuming first line is # Title)
                title_match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
                title = title_match.group(1) if title_match else filename.replace(".md", "")
                
                # Extract Category (Assuming Category: X line exists)
                cat_match = re.search(r'\*\*Category:\*\*\s*(.*)', content)
                category = cat_match.group(1) if cat_match else "General"
                
                node_id = slugify(title)
                
                # Insert into Neon
                try:
                    cur.execute("""
                        INSERT INTO origin_nodes (id, label, category, notes)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET notes = EXCLUDED.notes;
                    """, (node_id, title, category, content[:500])) # Saving first 500 chars as notes
                    print(f"✅ Imported: {title}")
                except Exception as e:
                    print(f"❌ Failed {title}: {e}")
                    conn.rollback()
                else:
                    conn.commit()

    cur.close()
    conn.close()
    print("Import Complete!")

if __name__ == "__main__":
    # Point this to your wiki folder path
    import_markdown_files('./wiki')
