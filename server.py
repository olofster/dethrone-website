#!/usr/bin/env python3
"""
Simple HTTP server with URL rewriting for GitHub Pages site.
Handles clean URLs by automatically appending .html when needed.
"""

import http.server
import socketserver
import os
import urllib.parse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # If path is empty, serve index.html
        if path == '' or path == '/':
            path = 'index.html'
        
        # If path ends with /, remove it
        if path.endswith('/'):
            path = path[:-1]
        
        # Check if file exists
        if os.path.isfile(path):
            # File exists, serve it
            self.path = '/' + path
            return super().do_GET()
        
        # Check if .html version exists
        html_path = path + '.html'
        if os.path.isfile(html_path):
            # Serve the .html version
            self.path = '/' + html_path
            return super().do_GET()
        
        # Check if it's a directory and index.html exists
        if os.path.isdir(path):
            index_path = os.path.join(path, 'index.html')
            if os.path.isfile(index_path):
                self.path = '/' + index_path
                return super().do_GET()
        
        # File not found, return 404
        self.send_error(404, "File not found")

if __name__ == "__main__":
    PORT = 8000
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

