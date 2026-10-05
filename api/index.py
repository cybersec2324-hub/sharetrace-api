from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import json
import sys
import os

app = FastAPI(title="ShareTrace API")

@app.get("/")
def home():
    return {"message": "ShareTrace API is running live on Vercel! Use /analyze?url=<your_link>"}

@app.get("/analyze")
def analyze_link(url: str):
    try:
        # Vercel serverless optimization
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # Call the sharetrace package natively
        process = subprocess.run(
            [sys.executable, "-m", "sharetrace", url, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )

        stdout_output = process.stdout.strip()
        stderr_output = process.stderr.strip()

        if stdout_output:
            start_index = stdout_output.find('{')
            if start_index != -1:
                clean_json = stdout_output[start_index:]
                return json.loads(clean_json)

        return JSONResponse(
            status_code=400, 
            content={"status": "error", "message": stderr_output or "No data extracted. Unsupported URL."}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))