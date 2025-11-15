import streamlit as st
import json
from google.oauth2 import service_account
from vertexai import generative_models, init as vertex_init

def setup_vertex_ai():
    try:
        # Load secrets from Streamlit Cloud
        project_id = st.secrets["project_id"]
        location = st.secrets["location"]

        # Load service account JSON from secrets (multiline string)
        service_account_info = json.loads(st.secrets["credentials"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info
        )

        # Initialize Vertex AI
        vertex_init(
            project=project_id,
            location=location,
            credentials=credentials
        )

        # Return the model instance
        return generative_models.GenerativeModel("gemini-2.5-flash")

    except KeyError as e:
        raise Exception(f"Missing secret: {e}")
    except Exception as e:
        raise Exception(f"Failed to setup Vertex AI: {str(e)}")
