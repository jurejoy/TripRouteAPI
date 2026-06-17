import os
import sys
import argparse
import subprocess
from pdf_generator import generate_pdf_report

# Set enterprise flag before importing genai
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "True"

def get_project_id():
    """Attempts to get the GCP project ID from environment or gcloud config."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id
        
    try:
        # Try to get it from gcloud
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True
        )
        project_id = result.stdout.strip()
        if project_id:
            # Check for the known typo/issue in user's config
            if project_id == "renjie-domo":
                print("Warning: Detected project 'renjie-domo' which might be invalid. Falling back to 'renjie-demo'.")
                return "renjie-demo"
            return project_id
    except Exception as e:
        print(f"Warning: Could not get project from gcloud config: {e}")
        
    return None

def is_chinese(text):
    """Checks if the text contains any CJK characters."""
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def has_cjk(text):
    """Checks if the text contains Chinese, Japanese, or Korean characters."""
    for char in text:
        cp = ord(char)
        if (0x4e00 <= cp <= 0x9fff) or (0x3040 <= cp <= 0x309f) or (0x30a0 <= cp <= 0x30ff) or (0xac00 <= cp <= 0xd7a3):
            return True
    return False

def translate_text(client, text, model="gemini-2.5-pro", target_language="Chinese"):
    """Translates text using Gemini model without tools."""
    prompt = (
        f"Translate the following text into {target_language}. "
        f"Preserve all markdown formatting, links, bold/italic styles, and list structure. "
        f"Do not add any commentary, explanations, or changes other than translation. "
        f"If the text is already in {target_language}, return it unchanged.\n\n"
        f"Text to translate:\n{text}"
    )
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Warning: Translation failed: {e}")
        return text

def main():
    parser = argparse.ArgumentParser(description="Query Gemini with Google Maps grounding and export to PDF.")
    parser.add_argument(
        "--query", 
        type=str, 
        nargs='+',
        help="One or more queries to send to Gemini. Space separated."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a file containing queries, one per line."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-pro",
        help="Gemini model to use. Default is gemini-2.5-pro."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="report.pdf",
        help="The output PDF filename."
    )
    parser.add_argument(
        "--project", 
        type=str, 
        help="GCP Project ID. If not provided, will try to detect."
    )
    
    args = parser.parse_args()
    
    # Collect queries
    queries = []
    if args.query:
        queries.extend(args.query)
    
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        queries.append(line)
        else:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
            
    # Default query if none provided
    if not queries:
        queries = ["东京成田机场去佐渡岛交通（分自驾和公共交通两种）"]
        print(f"No queries provided. Using default query: {queries[0]}")

    project_id = args.project or get_project_id()
    if not project_id:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set, and could not detect from gcloud config.")
        print("Please set GOOGLE_CLOUD_PROJECT environment variable or pass --project.")
        sys.exit(1)
        
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    
    # Set default location to global if not set
    if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

    print(f"Using Project: {project_id}")
    print(f"Using Location: {os.environ['GOOGLE_CLOUD_LOCATION']}")
    print(f"Using Model: {args.model}")
    
    try:
        from google import genai
        from google.genai import types
    except ImportError as e:
        print(f"Error: Failed to import google-genai. Make sure you are in the virtual environment: {e}")
        sys.exit(1)

    print(f"Initializing Gemini Client...")
    try:
        client = genai.Client(http_options=types.HttpOptions(api_version="v1"))
    except Exception as e:
         print(f"Error: Failed to initialize Gemini client: {e}")
         sys.exit(1)
         
    results = []
    
    for i, query in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] Processing query: {query}")
        try:
            response = client.models.generate_content(
                model=args.model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(google_maps=types.GoogleMaps())
                    ],
                    system_instruction=(
                        "You are a helpful travel assistant. Your task is to summarize transport options "
                        "between locations based on Google Maps grounding data. "
                        "For public transportation options (such as buses, trains, ferries), you must "
                        "specifically look for and include their operating hours, schedules, frequency, "
                        "and the last departure times if available in the grounding data. "
                        "Format your response clearly with headings and bullet points. "
                        "CRITICAL: You must ONLY output the synthesized travel guide. "
                        "Do NOT echo, copy, or dump the raw grounding chunks, metadata, URIs, directions, or titles "
                        "that you received from the search tool. Start directly with the guide."
                    ),
                ),
            )
            
            response_text = response.text
            print("Received response from grounding model.")
            print(f"--- RAW GROUNDING RESPONSE ---\n{response_text}\n-----------------------------")
            
            if is_chinese(query):
                print("Query is in Chinese. Translating response...")
                response_text = translate_text(client, response_text, model=args.model, target_language="Chinese")
                print("Translation complete.")
                print(f"--- TRANSLATED RESPONSE ---\n{response_text}\n-----------------------------")
            
            # Extract sources
            sources = []
            if response.candidates and response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        title = None
                        url = None
                        if chunk.maps:
                            title = chunk.maps.title
                            url = chunk.maps.uri
                        elif chunk.web:
                            title = chunk.web.title
                            url = chunk.web.uri
                            
                        if title and url:
                            if has_cjk(title):
                                print(f"Source title '{title}' has CJK. Translating to English...")
                                title = translate_text(client, title, model=args.model, target_language="English")
                                print(f"Translated to: {title}")
                            if {'title': title, 'url': url} not in sources:
                                sources.append({'title': title, 'url': url})
                                
            print(f"Extracted {len(sources)} unique sources.")
            
            results.append({
                'query': query,
                'response_text': response_text,
                'sources': sources
            })
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            # We can choose to continue or abort. Let's continue but log it.
            results.append({
                'query': query,
                'response_text': f"Error: Failed to retrieve response. {e}",
                'sources': []
            })

    import json
    with open("debug_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nGenerating PDF report: {args.output}")
    success = generate_pdf_report(results, args.output)
    
    if success:
        print("Process completed successfully.")
    else:
        print("Failed to generate report.")
        sys.exit(1)

if __name__ == "__main__":
    main()
