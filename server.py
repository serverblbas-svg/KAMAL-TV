import sqlite3
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 9000
DB_PATH = "channels.db"

class ChannelServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_channels':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            
            channels = []
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # لێرەدا بە دوای هەموو خشتەکاندا دەگەڕێین
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # گەڕان بەدوای خشتەی دروست (کە ناوی سیستماتیك نییە)
                target_table = None
                for table in tables:
                    t_name = table[0]
                    if t_name.lower() not in ['sqlite_sequence', 'sqlite_stat1']:
                        target_table = t_name
                        break
                
                if target_table:
                    # خوێندنەوەی هەموو دێڕەکانی ناو خشتەکە
                    cursor.execute(f"SELECT * FROM {target_table}")
                    rows = cursor.fetchall()
                    
                    # وەرگرتنی ناوی ستوونەکان
                    columns = [desc[0].lower() for desc in cursor.description]
                    
                    for row in rows:
                        ch_dict = {}
                        for i, col in enumerate(columns):
                            # دڵنیابوونەوە لەوەی داتاکە بە دەقی کوردی یان عەرەبی بە دروستی دەگوازرێتەوە
                            val = row[i]
                            ch_dict[col] = val
                        channels.append(ch_dict)
                        
                conn.close()
            except Exception as e:
                print(f"Error reading DB: {e}")
            
            # ناردنی داتاکان
            self.wfile.write(json.dumps(channels, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

print(f"🚀 ماڵپەڕەکەت بە سەرکەوتوویی نوێکرایەوە! سەردانی ئەم بەستەرە بکە: http://localhost:{PORT}")
server = HTTPServer(('0.0.0.0', PORT), ChannelServer)
server.serve_forever()
