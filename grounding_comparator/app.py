import os
import sys
import concurrent.futures
from flask import Flask, request, jsonify, render_template
import requests
import google.auth
import google.auth.transport.requests

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)

# Helper to render template from local folder
@app.route('/')
def index():
    return render_template('index.html')

def call_gemini_raw(project_id, location, model, query, grounding_type="none"):
    """Calls Vertex AI Gemini API via raw REST."""
    try:
        credentials, _ = google.auth.default(
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)
    except Exception as e:
        return {"error": f"Failed to get credentials: {str(e)}"}

    token = credentials.token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"

    payload = {
      "contents": [{
        "role": "user",
        "parts": [{
          "text": query
        }]
      }]
    }

    if grounding_type == "places":
        payload["tools"] = [{
            "googleMaps": {
              "groundingTypes": {
                "places": {}
              }
            }
        }]
    elif grounding_type == "routing":
        payload["tools"] = [{
            "googleMaps": {
              "groundingTypes": {
                "places": {},
                "routing": {}
              }
            }
        }]

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"error": f"API returned status {response.status_code}: {response.text}"}
        
        response_json = response.json()
        candidate = response_json['candidates'][0]
        text = candidate['content']['parts'][0]['text']
        metadata = candidate.get('groundingMetadata', {})
        
        return {
            "text": text,
            "metadata": metadata
        }
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

@app.route('/api/compare', methods=['POST'])
def compare():
    data = request.get_json()
    query = data.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or "renjie-demo"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION") or "us-central1"
    model = "gemini-2.5-pro"

    results = {}

    # Run the three calls in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_off = executor.submit(call_gemini_raw, project_id, location, model, query, "none")
        future_places = executor.submit(call_gemini_raw, project_id, location, model, query, "places")
        future_routing = executor.submit(call_gemini_raw, project_id, location, model, query, "routing")

        results['off'] = future_off.result()
        results['places'] = future_places.result()
        results['routing'] = future_routing.result()

    return jsonify(results)

if __name__ == '__main__':
    # Get port from environment (injected by JetSki) or default to 8080
    port = int(os.environ.get('ANTIGRAVITY_SIDECAR_WEB_PORT', 8080))
    # Run on all interfaces so it can be accessed
    app.run(host='0.0.0.0', port=port, debug=True)
