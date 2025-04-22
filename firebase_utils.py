import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# === Firebase Initialization ===

def initialize_firebase():
    if not firebase_admin._apps:
        try:
            firebase_key_raw = st.secrets["FIREBASE_KEY"]
            firebase_key_json = json.loads(firebase_key_raw)
            firebase_key_json["private_key"] = firebase_key_json["private_key"].replace("\\n", "\n")

            key_path = "temp_firebase_key.json"
            with open(key_path, "w") as f:
                json.dump(firebase_key_json, f)

            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://esp-os-project-74989-default-rtdb.firebaseio.com"
            })

        except KeyError:
            st.error("FIREBASE_KEY not found in Streamlit secrets.")
        except json.JSONDecodeError:
            st.error("Failed to parse FIREBASE_KEY. Ensure it's valid JSON with escaped newlines.")
        except Exception as e:
            st.error(f"Failed to initialize Firebase: {e}")

# Call initializer once
initialize_firebase()

# === Firebase Read and Write Functions ===

def get_device_credentials(device_id="Device_001"):
    try:
        ref = db.reference(f"{device_id}/Esp32_configure")
        data = ref.get()
        if data:
            return data.get("DeviceName"), data.get("Password")
        else:
            return None, None
    except Exception as e:
        st.error(f"Error fetching device credentials: {e}")
        return None, None

def validate_login(input_device_name, input_password, device_id="Device_001"):
    stored_name, stored_password = get_device_credentials(device_id)
    return input_device_name == stored_name and input_password == stored_password

def get_value(path, device_id="Device_001"):
    try:
        ref = db.reference(f"{device_id}/{path}")
        return ref.get()
    except Exception as e:
        st.error(f"Failed to read from Firebase: {e}")
        return None

def update_value(path, value, device_id="Device_001"):
    try:
        ref = db.reference(f"{device_id}/{path}")
        ref.set(value)
        return True
    except Exception as e:
        st.error(f"Failed to update Firebase: {e}")
        return False

def get_power_status():
    try:
        ref = db.reference("Device_001/led/state")
        state = ref.get()
        return state == 1
    except Exception as e:
        print("Error reading power status:", e)
        return False
