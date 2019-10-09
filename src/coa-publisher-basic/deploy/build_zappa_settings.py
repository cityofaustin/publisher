import os, json

# Constructs and writes the zappa_settings.json object used by zappa command in deploy.sh

zappa_settings = {
    "pr": {
        "app_function": "main.app",
        "profile_name": None,
        "project_name": "coa-publisher-basic",
        "runtime": "python3.7",
        "log_level": "ERROR",
        "environment_variables": {
        },
    }
}

config = zappa_settings["pr"]

# Add Environment variables to your zappa function
# These are sourced from your .env file
vars_to_add = [
    "NETLIFY_AUTH_TOKEN",
    "NETLIFY_GITHUB_INSTALLATION_ID",
]
config["environment_variables"] = {v: os.getenv(v, "") for v in vars_to_add}

# Write zappa_settings to zappa_settings.json at root level
zappa_settings_file = os.path.join(os.path.dirname(__file__), '../zappa_settings.json')
with open(zappa_settings_file, 'w', encoding='utf-8') as outfile:
    json.dump(zappa_settings, outfile, ensure_ascii=False, indent=4)
