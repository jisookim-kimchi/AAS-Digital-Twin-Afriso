import os
import json
import tempfile
import pandas as pd
import requests
from flask import Flask, render_template, request, send_file
from basyx.aas.adapter.json import read_aas_json_file
from basyx.aas.adapter import aasx
from basyx.aas.model import DictIdentifiableStore

app = Flask(__name__)

def process_aas_data(excel_file_stream, template_json_stream):
    """Core logic extracted from your script to process streams in memory."""
    
    # 1. Read Excel sheets
    excel_data = pd.read_excel(excel_file_stream, sheet_name=None, header=4)
    value_map = {}
    lang_map = {}

    for _, table_data in excel_data.items():
        if 'Element Name (idShort)' in table_data.columns and 'Actual Value' in table_data.columns:
            for _, row in table_data.iterrows():
                id_short = row['Element Name (idShort)']
                val = row['Actual Value']

                if pd.notna(id_short) and pd.notna(val):
                    if isinstance(val, str):
                        if '@de' in val:
                            val = val.split('@')[0]
                            lang_map[str(id_short)] = "de"
                        elif '@en' in val:
                            val = val.split('@')[0]
                            lang_map[str(id_short)] = "en"
                    value_map[str(id_short)] = val

    # 2. Read JSON Template
    aas_data = json.load(template_json_stream)

    # 3. Recursively replace values
    def replace_values(node):
        if isinstance(node, dict):
            if "idShort" in node and "value" in node and "modelType" in node:
                key = node["idShort"]
                model_type = node["modelType"]
                
                if key in value_map:
                    if model_type in ["Property", "File"]:
                        node["value"] = str(value_map[key])
                    elif model_type == "MultiLanguageProperty":
                        if isinstance(node["value"], list) and len(node["value"]) > 0 and isinstance(node["value"][0], dict) and "text" in node["value"][0]:
                            node["value"][0]["text"] = str(value_map[key])
                            if key in lang_map:
                                node["value"][0]["language"] = lang_map[key]
                else:
                    if model_type in ["Property", "File", "MultiLanguageProperty"]:
                        if "value" in node:
                            del node["value"]
                
            for k, v in node.items():
                replace_values(v)
            
        elif isinstance(node, list):
            for item in node:
                replace_values(item)

    replace_values(aas_data)

    # 4. Save intermediate JSON to a temp file for BaSyx adapter
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json", delete=False) as tmp_json:
        json.dump(aas_data, tmp_json, ensure_ascii=False, indent=2)
        tmp_json_path = tmp_json.name

    # 5. Build AASX file
    try:
        with open(tmp_json_path, "r", encoding="utf-8") as f:
            object_store = DictIdentifiableStore(read_aas_json_file(f))

        file_store = aasx.DictSupplementaryFileContainer()
        
        # Temp AASX file
        temp_aasx = tempfile.NamedTemporaryFile(delete=False, suffix=".aasx")
        temp_aasx_path = temp_aasx.name
        temp_aasx.close()

        with aasx.AASXWriter(temp_aasx_path) as writer:
            writer.write_aas_objects(
                part_name="/aasx/data.json",
                object_ids=[obj.id for obj in object_store],
                file_store=file_store,
                object_store=object_store,
                write_json=True
            )

        # Optional Server Upload step from your original script
        upload_url = "http://localhost:8081/upload"
        try:
            with open(temp_aasx_path, "rb") as f:
                requests.post(upload_url, files={"file": f}, timeout=2)
        except Exception:
            pass # Silently continue if external server isn't active

        return temp_aasx_path

    finally:
        if os.path.exists(tmp_json_path):
            os.remove(tmp_json_path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        excel_file = request.files.get("excel_file")
        json_file = request.files.get("json_file")

        if not excel_file or not json_file:
            return "Please select both files.", 400

        output_aasx_path = process_aas_data(excel_file, json_file)
        out_filename = os.path.splitext(excel_file.filename)[0] + ".aasx"

        return send_file(
            output_aasx_path,
            as_attachment=True,
            download_name=out_filename,
            mimetype="application/octet-stream"
        )

    return render_template("index.html")


if __name__ == "__main__":
    # Ensure standard Flask folder layout: /templates/index.html
    app.run(debug=True, port=5000)