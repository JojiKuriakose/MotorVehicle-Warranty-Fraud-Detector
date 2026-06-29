import io
import os
import sys
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from src.tools.processClaim import process_claims

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

app = FastAPI(
    title="Warranty Fraud Detector API",
    version="1.0.0",
    description="FastAPI backend for warranty fraud claim processing.",
    docs_url="/swagger",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "app": "warranty-fraud-detector",
        "version": app.version,
    }


@app.post("/process_csv", tags=["csv"])
async def process_csv(file: UploadFile = File(...)) -> StreamingResponse:
    if file.content_type not in ["text/csv", "application/vnd.ms-excel", "application/octet-stream"]:
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV.")

    try:
        raw_bytes = await file.read()
        claims_df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Cannot parse CSV file: {exc}") from exc

    processed_df = process_claims(claims_df)
    csv_bytes = processed_df.to_csv(index=False).encode("utf-8")

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=processed_claims.csv"},
 )


@app.post("/process_claim", tags=["claims"])
def process_claim(claims: list[dict[str, Any]]) -> JSONResponse:
    if not isinstance(claims, list) or len(claims) == 0:
        raise HTTPException(status_code=400, detail="Request body must be a non-empty list of claim objects.")

    try:
        claims_df = pd.DataFrame(claims)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not convert request body to DataFrame: {exc}") from exc

    processed_df = process_claims(claims_df)
    payload = processed_df.where(pd.notnull(processed_df), None).to_dict(orient="records")
    return JSONResponse(content=payload)


if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)















