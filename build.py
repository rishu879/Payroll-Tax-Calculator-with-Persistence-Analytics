import os
import shutil

def build():
    # Remove existing dist directory
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    os.makedirs("dist")
    
    # Copy index.html from templates to dist root
    shutil.copy("templates/index.html", "dist/index.html")
    
    # Copy static assets folder
    shutil.copytree("static", "dist/static")
    
    # Generate _redirects dynamically based on env variable for backend URL
    backend_url = os.environ.get("BACKEND_API_URL", "http://localhost:5000").rstrip('/')
    
    # First match API proxy, then fall back to SPA root
    redirects_content = f"/api/*  {backend_url}/api/:splat  200!\n"
    redirects_content += "/*      /index.html               200\n"
    
    with open("dist/_redirects", "w", encoding="utf-8") as f:
        f.write(redirects_content)
        
    print(f"Static build compiled successfully in 'dist/' directory.")
    print(f"Proxied '/api/*' to '{backend_url}/api/*'")
    print("Added fallback routing for SPA index.html mapping.")

if __name__ == "__main__":
    build()
