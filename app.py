#!/usr/bin/env python3
import os
import sys
import json
import glob
import requests
from flask import Flask, render_template, request, jsonify

# Auto-add local .venv site-packages if present
_venv_site_pkgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
if os.path.exists(_venv_site_pkgs) and _venv_site_pkgs not in sys.path:
    sys.path.insert(0, _venv_site_pkgs)

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    """Enable CORS so frontend can communicate smoothly across ports/hosts."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return response

def load_local_products():
    """Load all product AAS models from output_json directory as offline/local fallback."""
    local_products = []
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_json")
    
    if os.path.exists(output_dir):
        for json_path in glob.glob(os.path.join(output_dir, "*.json")):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Extract shells
                    shells = data.get("assetAdministrationShells", [])
                    submodels = data.get("submodels", [])
                    
                    for shell in shells:
                        shell["source"] = f"Local Template ({os.path.basename(json_path)})"
                        # Tag submodels with parent product name
                        tagged_submodels = []
                        for sm in submodels:
                            sm_copy = dict(sm)
                            sm_copy["parentProduct"] = shell.get("idShort", "Product")
                            tagged_submodels.append(sm_copy)
                        shell["attachedSubmodels"] = tagged_submodels
                        local_products.append(shell)
            except Exception:
                pass
    return local_products

@app.route("/")
def index():
    """Render the main Product & AAS Explorer web application."""
    return render_template("index.html")

@app.route("/api/fetch-partner-data", methods=["POST"])
def fetch_partner_data():
    """API endpoint to request AAS product data from partner Keycloak, Nginx Gateway, and Machine AAS endpoints."""
    req_data = request.get_json() or {}
    partner_ip = req_data.get("partner_ip", "").strip() or "127.0.0.1"
    username = req_data.get("username", "").strip() or "user"
    password = req_data.get("password", "").strip() or "1234"

    keycloak_url = f"http://{partner_ip}:9999/realms/basyx/protocol/openid-connect/token"
    
    endpoints_to_query = [
        ("Nginx Gateway (8080)", f"http://{partner_ip}:8080/shells"),
        ("Machine 1 AAS (8081)", f"http://{partner_ip}:8081/shells"),
        ("Machine 2 AAS (8082)", f"http://{partner_ip}:8082/shells"),
        ("AAS Registry (8083)", f"http://{partner_ip}:8083/shells"),
    ]

    submodel_endpoints = [
        ("Nginx Gateway Submodels", f"http://{partner_ip}:8080/submodels"),
        ("Machine 1 Submodels", f"http://{partner_ip}:8081/submodels"),
        ("Machine 2 Submodels", f"http://{partner_ip}:8082/submodels"),
    ]

    token_payload = {
        "client_id": "basyx-client",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    all_shells = []
    all_submodels = []
    seen_shell_ids = set()
    seen_submodel_ids = set()
    auth_success = False

    try:
        # 1. Acquire Token from Keycloak
        r_token = requests.post(keycloak_url, data=token_payload, timeout=4)
        if r_token.status_code == 200:
            auth_success = True
            token_data = r_token.json()
            access_token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {}

        # 2. Query ALL machine endpoints & gateway to aggregate ALL products/shells
        for ep_name, ep_url in endpoints_to_query:
            try:
                r = requests.get(ep_url, headers=headers, timeout=3)
                if r.status_code == 200:
                    res_data = r.json()
                    items = res_data.get("result", []) if isinstance(res_data, dict) else (res_data if isinstance(res_data, list) else [])
                    for item in items:
                        item_id = item.get("id") or item.get("idShort")
                        if item_id and item_id not in seen_shell_ids:
                            seen_shell_ids.add(item_id)
                            item["source_endpoint"] = ep_name
                            all_shells.append(item)
            except Exception:
                pass

        # 3. Query submodel endpoints to aggregate submodels
        for ep_name, ep_url in submodel_endpoints:
            try:
                r = requests.get(ep_url, headers=headers, timeout=3)
                if r.status_code == 200:
                    res_data = r.json()
                    items = res_data.get("result", []) if isinstance(res_data, dict) else (res_data if isinstance(res_data, list) else [])
                    for item in items:
                        item_id = item.get("id") or item.get("idShort")
                        if item_id and item_id not in seen_submodel_ids:
                            seen_submodel_ids.add(item_id)
                            item["source_endpoint"] = ep_name
                            all_submodels.append(item)
            except Exception:
                pass

        # 4. If live endpoints returned empty, merge local JSON product models (LAG14ER, PrimoVent)
        local_models = load_local_products()
        for loc_shell in local_models:
            item_id = loc_shell.get("id") or loc_shell.get("idShort")
            if item_id and item_id not in seen_shell_ids:
                seen_shell_ids.add(item_id)
                all_shells.append(loc_shell)

        # 5. Link full submodel objects to each product shell
        submodels_by_id = {sm.get("id"): sm for sm in all_submodels if sm.get("id")}
        for shell in all_shells:
            if "attachedSubmodels" not in shell or not shell["attachedSubmodels"]:
                submodel_list = []
                for sm_ref in shell.get("submodels", []):
                    keys = sm_ref.get("keys", [])
                    if keys:
                        sm_id = keys[0].get("value")
                        if sm_id in submodels_by_id:
                            sm_obj = dict(submodels_by_id[sm_id])
                            sm_obj["parentProduct"] = shell.get("idShort", "Product")
                            submodel_list.append(sm_obj)
                        else:
                            submodel_list.append({"idShort": sm_id.split("/")[-1], "id": sm_id, "parentProduct": shell.get("idShort")})
                shell["attachedSubmodels"] = submodel_list

        return jsonify({
            "success": True,
            "partner_ip": partner_ip,
            "authenticated": auth_success,
            "total_products": len(all_shells),
            "total_submodels": len(all_submodels),
            "shells": all_shells,
            "submodels": all_submodels
        })

    except Exception as e:
        # Fallback to local product models if network fails completely
        local_models = load_local_products()
        return jsonify({
            "success": True,
            "partner_ip": partner_ip,
            "authenticated": False,
            "offline_mode": True,
            "error_note": f"Live connection note: {str(e)}",
            "total_products": len(local_models),
            "total_submodels": 0,
            "shells": local_models,
            "submodels": []
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
