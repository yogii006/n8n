from flask import Flask, render_template, request
import requests
from requests.auth import HTTPBasicAuth
import datetime
import os
app = Flask(__name__)

WEBHOOK_URL = "http://localhost:5678/webhook-test/4151a4d9-a106-4be4-99c3-3b45f81aae94"

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        filename = request.form.get("filename")
        directory = request.form.get("directory")
        description = request.form.get("description")
        username = request.form.get("username")
        password = request.form.get("password")

        # ✅ Fallback logic
        if not directory or directory.strip() == "":
            directory = "/home/node/.n8n-files/videos"
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "name": name,
                    "email": email,
                    "filename": filename,
                    "directory": directory,
                    "description": description,
                    "time": datetime.datetime.now().isoformat()
                },
                auth=HTTPBasicAuth(username, password),   
            )
            print(response.status_code)
            if response.status_code == 200:
                message = "Workflow triggered successfully!"
            elif response.status_code in [401, 403]:
                message = "Invalid credentials. Access denied."
            else:
                message = "something went wrong"
        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)