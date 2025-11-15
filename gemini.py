import streamlit as st
import json
import base64
from google.oauth2 import service_account
from vertexai import init as vertex_init
from vertexai.generative_models import GenerativeModel

def setup_vertex_ai():
    try:
        project_id = st.secrets["project_id"]
        location = st.secrets["location"]

        # Decode Base64 → JSON dict
        decoded_bytes = base64.b64decode(st.secrets["credentials_b64"])
        credentials_info = json.loads(decoded_bytes.decode("utf-8"))

        credentials = service_account.Credentials.from_service_account_info(
            credentials_info
        )

        # Init Vertex AI
        vertex_init(
            project=project_id,
            location=location,
            credentials=credentials
        )

        return GenerativeModel("gemini-2.5-flash")

    except Exception as e:
        raise Exception(f"Vertex setup failed: {e}")


