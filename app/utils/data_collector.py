import urllib.request
import xml.etree.ElementTree as ET
from app.core.firebase import db
from datetime import datetime

def collect_adhd_youtube_data():
    try:
        # YouTube RSS feed for search query "adhd"
        url = "https://www.youtube.com/feeds/videos.xml?search_query=adhd"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        # Parse XML
        root = ET.fromstring(xml_data)
        
        # Namespaces
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'yt': 'http://www.youtube.com/xml/schemas/2015',
            'media': 'http://search.yahoo.com/mrss/'
        }
        
        count = 0
        for entry in root.findall('atom:entry', ns):
            video_id_el = entry.find('yt:videoId', ns)
            title_el = entry.find('atom:title', ns)
            author_el = entry.find('atom:author/atom:name', ns)
            published_el = entry.find('atom:published', ns)
            
            if video_id_el is None or title_el is None:
                continue
                
            video_id = video_id_el.text
            title = title_el.text
            author = author_el.text if author_el is not None else "Unknown"
            published = published_el.text if published_el is not None else datetime.utcnow().isoformat()
            
            # Categorize based on keywords in title
            title_lower = title.lower()
            if "tips" in title_lower or "hack" in title_lower or "manage" in title_lower or "coping" in title_lower or "strategy" in title_lower:
                category = "ADHD Coping"
            elif "what is" in title_lower or "explain" in title_lower or "science" in title_lower or "symptom" in title_lower or "understand" in title_lower:
                category = "ADHD Education"
            else:
                category = "General ADHD"
                
            # Save or update in Firestore collection "youtube_adhd_videos"
            db.collection("youtube_adhd_videos").document(video_id).set({
                "video_id": video_id,
                "title": title,
                "creator": author,
                "published_at": published,
                "collected_at": datetime.utcnow().isoformat(),
                "category": category
            })
            count += 1
            if count >= 10:  # Limit to top 10 recent videos
                break
                
        return {"success": True, "count": count, "message": f"Berhasil mengumpulkan {count} video ADHD dari YouTube RSS."}
    except Exception as e:
        print("Error collecting YouTube data:", str(e))
        return {"success": False, "error": str(e), "message": "Gagal mengumpulkan data eksternal."}
