from flask import Flask, render_template, request
import json
import jsonref
import yaml
from jsonschema import validate, ValidationError

app = Flask(__name__)

# ✅ DEFINE FUNCTION FIRST
def load_schema(file_name):
    with open(file_name) as f:
        return jsonref.replace_refs(yaml.safe_load(f))

# ✅ Load Global (OpenAPI schema)
with open("globalpayments.json") as f:
    raw_schema = yaml.safe_load(f)

resolved_schema = jsonref.replace_refs(raw_schema)
global_schema = resolved_schema["components"]["schemas"]["PaymentInitationDetails"]

# ✅ Load ACH schema
ach_schema = load_schema("achpayments.json")

# ✅ Store schemas
schemas = {
    "global": global_schema,
    "ach": ach_schema
}

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    formatted_json = ""
    user_input = ""
    selected_schema = "global"  # default

    if request.method == "POST":
        user_input = request.form["json_input"]
        selected_schema = request.form.get("schema_type", "global")

        try:
            parsed = json.loads(user_input)

            # ✅ Use selected schema
            validate(instance=parsed, schema=schemas[selected_schema])

            result = "✅ Valid JSON (matches schema)"
            formatted_json = json.dumps(parsed, indent=4)

        except json.JSONDecodeError as e:
            result = f"❌ Invalid JSON format: {e}"
    
        except ValidationError as e:
            result = f"❌ Schema validation error: {e.message}"

    return render_template(
        "index.html",
        result=result,
        formatted_json=formatted_json,
        json_input=user_input,
        selected_schema=selected_schema
    )

if __name__ == "__main__":
    app.run(debug=True)