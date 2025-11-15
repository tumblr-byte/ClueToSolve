import json
import google.auth
from google.cloud import aiplatform
from google.generativeai import GenerativeModel
from google.auth import service_account

def setup_vertex_ai():
    try:
        # Load config from config.json
        with open('config.json', 'r') as f:
            config = json.load(f)

        project_id = config['project_id']
        location = config['location']
        credentials_path = config['credentials_path']

        # Load credentials from the file path
        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        # Initialize Vertex AI / Gemini
        aiplatform.init(
            project=project_id,
            location=location,
            credentials=credentials
        )

        # Return a Gemini model instance
        return GenerativeModel("gemini-2.5-flash")
    except FileNotFoundError:
        raise Exception("config.json not found. Please create it with your Vertex AI credentials.")
    except Exception as e:
        raise Exception(f"Failed to setup Vertex AI: {str(e)}")
