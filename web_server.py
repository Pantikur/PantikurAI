"""
Простой веб-сервер для Wuglarst AI
- Раздаёт HTML/CSS/JS с порта 3000
- Пробрасывает API на localhost:8000
"""
import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import os
from pathlib import Path

PORT = 3000
API_PORT = 8000
PUBLIC_DIR = Path(__file__).parent / "public"

class WebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def do_POST(self):
        # Пробрасываем все POST-запросы на API
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else None
        
        headers = {
            'Content-Type': self.headers.get('Content-Type', ''),
        }
        
        try:
            req = urllib.request.Request(
                f'http://localhost:{API_PORT}{self.path}',
                data=post_data,
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=300) as response:
                response_data = response.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_data)
        except Exception as e:
            self.send_error(500, f"API Error: {str(e)}")

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WebHandler) as httpd:
        print(f"🚀 Сервер запущен на http://localhost:{PORT}")
        print(f"📁 Статика: {PUBLIC_DIR}")
        print(f"🔗 API проброс: localhost:{API_PORT}")
        print("⏹  Для остановки нажми Ctrl+C")
        httpd.serve_forever()
