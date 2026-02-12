from flask import Flask, render_template, request
from supabase import create_client, Client
import requests
from requests.auth import HTTPBasicAuth
import datetime
import os
import time
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "videos"

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        description = request.form.get("description")
        username = request.form.get("username")
        password = request.form.get("password")

        if "video" not in request.files:
            return render_template("index.html", message="No video uploaded")

        file = request.files["video"]

        if file.filename == "":
            return render_template("index.html", message="Empty filename")

        try:
            filename = file.filename  # keep original filename

            # -------------------------
            # 1️⃣ Upload To Supabase
            # -------------------------
            supabase.storage.from_(BUCKET_NAME).upload(
                filename,
                file.read(),
                {"content-type": file.content_type}
            )

            file_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)

            # -------------------------
            # 2️⃣ Wait 2 seconds
            # -------------------------
            time.sleep(2)

            # -------------------------
            # 3️⃣ Send To n8n Webhook
            # -------------------------
            response = requests.post(
                WEBHOOK_URL,
                json={
                    "name": name,
                    "email": email,
                    "description": description,
                    "video_url": file_url,
                    "video_filename": filename,
                    "time": datetime.datetime.now().isoformat()
                },
                auth=HTTPBasicAuth(username, password),
                timeout=15
            )

            if response.status_code == 200:
                message = "Upload complete & Workflow triggered successfully!"
            elif response.status_code in [401, 403]:
                message = "Invalid credentials. Access denied."
            else:
                message = f"n8n Error: {response.status_code}"

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)