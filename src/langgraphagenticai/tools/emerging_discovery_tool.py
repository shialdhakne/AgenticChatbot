# File: src/langgraphagenticai/tools/emerging_discovery_tool.py

import requests
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from langchain.tools.base import BaseTool
from huggingface_hub import HfApi

class EmergingDiscoveryTool(BaseTool):
    # Pydantic v2 needs type hints on class fields
    name: str = "emerging_discovery"
    description: str = (
        "Fetch the latest raw emerging-tech items (title, link, date, source) "
        "from arXiv and HuggingFace for a given field."
    )

    def _run(self, field: str = "Generative AI"):
        """
        Return a list of dicts with keys:
          - title: str
          - date: datetime (timezone-aware, UTC)
          - link: str
          - source: str
        """
        results = []
        field = (field or "Generative AI").strip()

        # -------- arXiv --------
        params = {
            "search_query": f"all:{field}",
            "start": 0,
            "max_results": 3,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        resp = requests.get("http://export.arxiv.org/api/query", params=params, timeout=20)
        feed = feedparser.parse(resp.text)

        for entry in getattr(feed, "entries", []):
            raw = getattr(entry, "published", None) or getattr(entry, "updated", None)

            # Normalize to tz-aware UTC
            dt = None
            if raw:
                # Try RFC 2822 first (common in arXiv feeds)
                try:
                    dt = parsedate_to_datetime(raw)
                except Exception:
                    dt = None
                # Fallback: ISO 8601 (handle trailing Z)
                if dt is None:
                    try:
                        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                    except Exception:
                        dt = None
            if dt is None:
                dt = datetime.now(timezone.utc)

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)

            results.append({
                "title": getattr(entry, "title", "Untitled"),
                "date": dt,  # tz-aware UTC
                "link": getattr(entry, "id", None) or getattr(entry, "link", ""),
                "source": "arXiv",
            })

        # -------- Hugging Face --------
        api = HfApi()
        try:
            trending = api.list_models(
                filter=field.replace(" ", "-"),
                sort="downloads",
                limit=3,
            )
        except Exception:
            trending = []

        now_utc = datetime.now(timezone.utc)  # tz-aware UTC to match arXiv
        for m in trending or []:
            results.append({
                "title": getattr(m, "modelId", "unknown-model"),
                "date": now_utc,
                "link": f"https://huggingface.co/{getattr(m, 'modelId', '')}",
                "source": "HuggingFace",
            })

        # Safe sort: everything is tz-aware UTC
        results.sort(key=lambda x: x["date"], reverse=True)
        return results

    async def _arun(self, field: str):
        raise NotImplementedError("EmergingDiscoveryTool does not support async")

def get_emerging_discovery_tool() -> EmergingDiscoveryTool:
    return EmergingDiscoveryTool()
