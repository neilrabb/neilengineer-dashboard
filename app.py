# app.py
from flask import Flask, render_template, request, jsonify, redirect
import os
import time
import requests
from langchain.prompts import PromptTemplate
from langchain_community.chat_models.perplexity import ChatPerplexity
import base64
import json

# Initialize Flask app
app = Flask(__name__)

# Configuration
MAIN_DOMAIN = "https://neilengineer.online"
WEBSITE_DOMAIN = "https://softwareapp.site"

# GitHub configuration
GITHUB_REPO = "neilrabb/softwareapp-site"  # Your actual GitHub repo
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # Your GitHub Personal Access Token
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"

# Initialize AI model
PPLX_API_KEY = os.environ.get('PPLX_API_KEY', "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")
llm = ChatPerplexity(model="sonar-reasoning", temperature=0.5, pplx_api_key=PPLX_API_KEY)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["current_html", "request"],
    template=(
        "You are an expert web developer AI assistant. You will be given the current HTML of a website "
        "and a request to modify it. Generate the new HTML that incorporates the requested changes.\n\n"
        "Current Website HTML:\n```html\n{current_html}\n```\n\n"
        "Request: {request}\n\n"
        "Generate only the complete HTML code for the updated website without any explanations:"
    )
)

# Create modern chain using LCEL
web_dev_chain = prompt | llm

# Function to get current website HTML from GitHub
def get_current_html():
    try:
        # Try to get the index.html from GitHub
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get(f"{GITHUB_API_URL}/index.html", headers=headers)
        
        if response.status_code == 200:
            # File exists, get its content
            content_data = response.json()
            decoded_content = base64.b64decode(content_data["content"]).decode("utf-8")
            return decoded_content
        else:
            # File doesn't exist, create default HTML
            default_html = '<html><body><h1>Welcome to your AI-generated website</h1></body></html>'
            upload_to_github(default_html, 'index.html')
            return default_html
            
    except Exception as e:
        print(f"Error getting HTML from GitHub: {e}")
        # Return default HTML if any error occurs
        default_html = '<html><body><h1>Welcome to your AI-generated website</h1></body></html>'
        return default_html

# Function to upload content to GitHub
def upload_to_github(html_content, filename='index.html'):
    try:
        # Check if file already exists to get the SHA
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check if file exists
        response = requests.get(f"{GITHUB_API_URL}/{filename}", headers=headers)
        
        # Prepare the upload data
        upload_data = {
            "message": f"Update {filename} via AI Web Developer",
            "content": base64.b64encode(html_content.encode()).decode()
        }
        
        # If file exists, we need the SHA to update it
        if response.status_code == 200:
            sha = response.json()["sha"]
            upload_data["sha"] = sha
            
        # Create or update the file
        response = requests.put(
            f"{GITHUB_API_URL}/{filename}",
            headers=headers,
            json=upload_data
        )
        
        return response.status_code in (200, 201)
        
    except Exception as e:
        print(f"Error uploading to GitHub: {e}")
        return False

# Routes for the control interface
@app.route('/')
def control_panel():
    return render_template('control_panel.html', website_url=WEBSITE_DOMAIN)

@app.route('/submit_prompt', methods=['POST'])
def submit_prompt():
    try:
        prompt_text = request.form['prompt']
        
        # Get current website HTML
        current_html = get_current_html()
        
        # Process with AI
        result = web_dev_chain.invoke({"current_html": current_html, "request": prompt_text})
        
        # Extract the string content from the AIMessage object
        if hasattr(result, 'content'):
            new_html = result.content
        elif isinstance(result, dict) and 'content' in result:
            new_html = result['content']
        elif isinstance(result, str):
            new_html = result
        else:
            # Last resort - try string conversion
            new_html = str(result)
            # If it still contains AIMessage in the string, extract just the content
            if "AIMessage" in new_html and "content=" in new_html:
                start = new_html.find("content=") + 9  # +9 to skip "content='"
                end = new_html.rfind("'")
                if start > 9 and end > start:
                    new_html = new_html[start:end]
        
        # Update the website by uploading to GitHub
        upload_success = upload_to_github(new_html)
        
        if upload_success:
            return jsonify({
                "status": "success", 
                "message": "Website updated successfully!",
                "website_url": WEBSITE_DOMAIN
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to update the website on GitHub"
            }), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in submit_prompt: {error_details}")
        
        # Return errors as JSON
        return jsonify({
            "status": "error",
            "message": f"Error: {str(e)}"
        }), 500

@app.route('/test-api-keys', methods=['GET'])
def test_api_keys():
    """Test API keys and connections"""
    results = {
        "github_token": {
            "is_set": bool(GITHUB_TOKEN),
            "value_preview": GITHUB_TOKEN[:4] + "..." if GITHUB_TOKEN else None
        },
        "pplx_api_key": {
            "is_set": bool(PPLX_API_KEY),
            "value_preview": PPLX_API_KEY[:4] + "..." if PPLX_API_KEY else None
        }
    }
    
    # Test GitHub connection if token is set
    if GITHUB_TOKEN:
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get("https://api.github.com/user", headers=headers)
            results["github_api_test"] = {
                "status_code": response.status_code,
                "user_login": response.json().get("login") if response.status_code == 200 else None
            }
        except Exception as e:
            results["github_api_test"] = {"error": str(e)}
    
    # Test Perplexity API if key is set
    if PPLX_API_KEY:
        try:
            test_llm = ChatPerplexity(model="sonar-small-chat", temperature=0, pplx_api_key=PPLX_API_KEY)
            response = test_llm.invoke("Say hello")
            results["pplx_api_test"] = {
                "success": True,
                "response_preview": str(response)[:100] + "..." if response else None
            }
        except Exception as e:
            results["pplx_api_test"] = {"error": str(e)}
    
    return jsonify(results)

# For Vercel serverless function compatibility
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    # For local development only
    app.run(debug=True, port=5050)