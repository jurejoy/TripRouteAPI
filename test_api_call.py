import os
import sys

# Set enterprise flag before importing genai
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "True"

print("Environment Variables:")
print(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
print(f"GOOGLE_CLOUD_LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
print(f"GOOGLE_GENAI_USE_ENTERPRISE: {os.environ.get('GOOGLE_GENAI_USE_ENTERPRISE')}")

try:
    from google import genai
    from google.genai import types
except ImportError as e:
    print(f"Failed to import google-genai: {e}")
    sys.exit(1)

def test_grounding():
    # Initialize client. It should pick up project and location from env.
    # We use v1 API version as per docs for maps grounding.
    try:
        client = genai.Client(http_options=types.HttpOptions(api_version="v1"))
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    query = "东京成田机场去佐渡岛交通（分自驾和公共交通两种）"
    print(f"\nRunning query: {query}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(google_maps=types.GoogleMaps())
                ],
            ),
        )
        
        print("\n--- Response Text ---")
        print(response.text)
        print("\n---------------------")
        
        print("\n--- Grounding Metadata ---")
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            print(f"Metadata object: {metadata}")
            # Try to print specific fields if they exist
            # GroundingMetadata in google-genai SDK might have different attribute names.
            # We will print the dir() to see what's available if it's not easily printable as dict.
             # Actually, it should be serializable or have standard fields.
            try:
                 import json
                 # The SDK objects often have a model_dump or to_json method if they are pydantic models
                 if hasattr(metadata, 'model_dump'):
                      print(json.dumps(metadata.model_dump(), indent=2, ensure_ascii=False))
                 elif hasattr(metadata, 'to_json'):
                      print(metadata.to_json())
                 else:
                      print(metadata)
            except Exception as json_err:
                 print(f"Could not serialize metadata to JSON: {json_err}")
                 print(f"Dir of metadata: {dir(metadata)}")
        else:
            print("No grounding metadata found in the response.")
            
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    test_grounding()
