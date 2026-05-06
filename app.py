from flask import Flask, render_template, request
import json
import jsonref
import yaml
from jsonschema import validate, ValidationError

app = Flask(__name__)

# ✅ Load YAML schema correctly
with open("schema.json") as f:
    raw_schema = yaml.safe_load(f)

resolved_schema = jsonref.replace_refs(raw_schema)

# 🔥 Extract the real schema from OpenAPI
schema = resolved_schema["components"]["schemas"]["PaymentInitationDetails"]

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    formatted_json = ""
    
    if request.method == "POST":
        user_input = request.form["json_input"]
        
        try:
            parsed = json.loads(user_input)

            # ✅ Validate against schema
            validate(instance=parsed, schema=schema)

            result = "✅ Valid JSON (matches schema)"
            formatted_json = json.dumps(parsed, indent=4)

        except json.JSONDecodeError as e:
            result = f"❌ Invalid JSON format: {e}"

        except ValidationError as e:
            result = f"❌ Schema validation error: {e.message}"

    return render_template("index.html", result=result, formatted_json=formatted_json)

if __name__ == "__main__":
    app.run(debug=True)