#!/usr/bin/env python3
"""
Script pour lister les endpoints disponibles sur le serveur FastAPI.
"""

import requests
import json

def list_endpoints():
    try:
        response = requests.get("http://127.0.0.1:8000/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            
            print("=== Endpoints disponibles ===")
            for path, methods in paths.items():
                for method, details in methods.items():
                    summary = details.get("summary", "Pas de description")
                    print(f"{method.upper()} {path} - {summary}")
                    
            print(f"\nTotal: {len(paths)} endpoints")
        else:
            print(f"Erreur: {response.status_code}")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    list_endpoints()
