import os
import json
#print(dir(json))
import pandas as panda
from basyx.aas.adapter.json import read_aas_json_file
#print(help(read_aas_json_file))
from basyx.aas.adapter import aasx
from basyx.aas.model import DictIdentifiableStore
#print(help(DictObjectStore))

def process_excel(excel_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = os.path.basename(excel_path).replace(".xlsx", "")
    
    #to read empty template json file
    template_json_path = os.path.join(base_dir, "..", "json_template", f"{file_name}_Template.json")
    output_json_path = os.path.join(base_dir, "..","output_json", f"{file_name}_output.json")

    excel_data = panda.read_excel(excel_path, sheet_name=None, header=4)
    value_map = {}
    lang_map = {}
     
    for sheets, table_data in excel_data.items():
        #print(table_data.columns.tolist())
        
        if 'Element Name (idShort)' in table_data.columns and 'Actual Value' in table_data.columns:
            for index, row in table_data.iterrows():
                #print(f"index: {index}\n")
                #print(f"row: {row}\n")
                id_short = row['Element Name (idShort)']
                val = row['Actual Value']
                #print(f"\nid_short: {id_short}\n")
                #print(f"\nval: {val}\n")

                # if id_short and val is not empty
                if panda.notna(id_short) and panda.notna(val):
                    # val is a instance of str class and '@de', '@en' eliminating if it exists
                    if isinstance(val, str):
                        if '@de' in val:
                            val = val.split('@')[0]
                            lang_map[str(id_short)] = "de"
                        elif '@en' in val:
                            val = val.split('@')[0]
                            lang_map[str(id_short)] = "en"
                    value_map[str(id_short)] = val

    print(f"Number of data from excel: {len(value_map)}")
    for v in value_map:
        print(f"{v}:{value_map[v]}\n")

    with open(template_json_path, "r", encoding="utf-8") as f:
        aas_data = json.load(f)

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

    # converting to json file
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(aas_data, f, ensure_ascii=False, indent=2)

    # reading json file and make object store
    with open(output_json_path, "r", encoding="utf-8") as f:
        object_store = DictIdentifiableStore(read_aas_json_file(f))

    file_store = aasx.DictSupplementaryFileContainer()
    aasx_path = os.path.join(base_dir, "..", "aasx", f"{file_name}.aasx")

    with aasx.AASXWriter(aasx_path) as writer:
        writer.write_aas_objects(
            part_name="/aasx/data.json",
            object_ids=[obj.id for obj in object_store],
            file_store=file_store,
            object_store=object_store,
            write_json=True
        )

    print(f"----------------------------------------- aasx created : ----------------------------------------- {aasx_path}")

    import requests
    upload_url = "http://localhost:8081/upload"
    
    try:
        with open(aasx_path, "rb") as f:
            file_tuple = (os.path.basename(aasx_path), f, "application/asset-administration-shell-package")
            res = requests.post(upload_url, files={"file": file_tuple})
            print(f"server upload result: {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        print(f"Warning: Failed to connect to server at {upload_url}. Is the server running?")
    except Exception as e:
        print(f"Warning: Failed to upload file to {upload_url} - {e}")

if __name__ == '__main__':
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_excel = os.path.join(base_dir, "..", "xlsx", "LAG14ER.xlsx")
    if os.path.exists(default_excel):
        process_excel(default_excel)