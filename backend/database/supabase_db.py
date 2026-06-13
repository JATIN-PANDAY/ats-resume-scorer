import logging
import httpx
import json
import socket
from datetime import datetime, timezone
from typing import List, Optional, Dict

logger = logging.getLogger('ats_resume_scorer')

from backend.core.config import SUPABASE_URL, SUPABASE_KEY

# --- SAFETY GATE: Check for internet connection ---
def is_online(host="8.8.8.8", port=53, timeout=1):
    """Checks if internet is available before attempting connection."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def _get_headers():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

async def save_analysis(user_id: str, filename: str, analysis_result: Dict) -> Optional[str]:
    # Check if we are online before trying to save
    if not is_online():
        logger.warning("Offline mode: Skipping database save.")
        return None

    headers = _get_headers()
    if not headers:
        return None

    def _json_default(o):
        if hasattr(o, 'model_dump'):
            return o.model_dump()
        return str(o)
        
    serializable_result = json.loads(json.dumps(analysis_result, default=_json_default))

    # Using fixed email for local developer mode
    user_email = "developer@local.com"

    doc = {
        "user_email": user_email,
        "resume_name": filename,
        "overall_score": int(serializable_result.get("ats_score", 0)),
        "formatting_score": int(serializable_result.get("component_scores", {}).get("formatting_score", 0)),
        "analysis_result": serializable_result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analysis_history"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=doc)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                inserted_id = str(data[0].get("id"))
                logger.info(f"Saved analysis to analysis_history: {inserted_id}")
                return inserted_id
            return None
    except Exception as exc:
        logger.error(f"Failed to save analysis to Supabase: {exc}")
        return None

async def get_user_history(user_id: str) -> List[Dict]:
    # Check if we are online before trying to fetch
    if not is_online():
        logger.warning("Offline mode: Skipping database fetch.")
        return []

    headers = _get_headers()
    if not headers:
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analysis_history"
    user_email = "developer@local.com"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=headers, 
                params={
                    "user_email": f"eq.{user_email}",
                    "order": "created_at.desc"
                }
            )
            response.raise_for_status()
            docs = response.json()
            
            results = []
            for doc in docs:
                results.append({
                    "id": str(doc.get("id")),
                    "filename": doc.get("resume_name", "resume"),
                    "resume_name": doc.get("resume_name", "resume"),
                    "job_title": "Software Engineer",
                    "ats_score": doc.get("overall_score", 0),
                    "keyword_match": doc.get("formatting_score", 0),
                    "missing_keywords": doc.get("analysis_result", {}).get("missing_keywords", []),
                    "date": doc.get("created_at", ""),
                    "created_at": doc.get("created_at", ""),
                    "analysis_result": doc.get("analysis_result", {}),
                })
            return results
    except Exception as exc:
        logger.error(f"Failed to fetch history from Supabase: {exc}")
        return []

async def delete_analysis(analysis_id: str, user_id: str) -> bool:
    # Check if we are online before trying to delete
    if not is_online():
        logger.warning("Offline mode: Skipping database delete.")
        return False

    headers = _get_headers()
    if not headers:
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/analysis_history"
    user_email = "developer@local.com"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url, 
                headers=headers, 
                params={
                    "id": f"eq.{analysis_id}",
                    "user_email": f"eq.{user_email}"
                }
            )
            response.raise_for_status()
            return True
    except Exception as exc:
        logger.error(f"Failed to delete analysis {analysis_id}: {exc}")
        return False