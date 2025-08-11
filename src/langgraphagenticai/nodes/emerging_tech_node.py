# File: src/langgraphagenticai/nodes/emerging_tech_node.py

from src.langgraphagenticai.tools.emerging_discovery_tool import get_emerging_discovery_tool
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import os

class EmergingTechNode:
    """
    Node for discovering and summarizing emerging Generative AI topics.
    """
    def __init__(self, llm):
        """
        Initialize the EmergingTechNode with an LLM and the EmergingDiscoveryTool.
        """
        self.tool = get_emerging_discovery_tool()
        self.llm = llm
        # this is used to capture various steps in this file so that later can be use for steps shown
        self.state = {}
        # Toggle debug on/off by ENV var if you want: os.environ.get("ET_DEBUG") == "1"
        self._debug = True

    def _dbg(self, label, value):
        """Simple debug printer (safe for Streamlit console)."""
        if not self._debug:
            return
        try:
            preview = repr(value)
        except Exception:
            preview = f"<unrepr-able of type {type(value)}>"
        print(f"[EmergingTechNode DEBUG] {label}: type={type(value)} value={preview[:800]}")

    def fetch_emerging(self, state: dict) -> dict:
        """
        Fetch raw emerging AI topics based on the specified field.

        Args:
            state (dict): The state dictionary containing 'messages'.

        Returns:
            dict: Updated state with 'emerging_data' list of raw items.
        """
        # ---- DEBUG: Inspect incoming state/messages ----
        self._dbg("state.keys()", list(state.keys()))
        self._dbg("state['messages']", state.get("messages"))

        # EXACT pattern as AINewsNode: get topic/field from first message, lowercase
        # But add a tiny guard if messages is a plain string
        messages = state.get("messages")
        if isinstance(messages, list) and messages:
            msg0 = messages[0]
            self._dbg("messages[0]", msg0)
            # ChatMessage (has .content)
            if hasattr(msg0, "content"):
                field = msg0.content.lower()
            # dict message with 'content'
            elif isinstance(msg0, dict) and "content" in msg0:
                field = str(msg0["content"]).lower()
            else:
                # fallback: treat first element as string
                field = str(msg0).lower()
        elif isinstance(messages, str):
            # someone passed the raw string directly
            field = messages.lower()
        else:
            field = "generative ai"

        self._dbg("resolved field", field)
        self.state["field"] = field

        # Fetch raw items via the tool
        items = self.tool._run(field)
        self._dbg("tool._run(field) -> items", items)

        # --- HARDENING to prevent "string indices must be integers" ---
        # Normalize items into a list[dict]
        if isinstance(items, dict) and "results" in items:
            # If a provider returns {"results": [...]}, unwrap it
            items = items.get("results", [])
            self._dbg("unwrapped items", items)

        if isinstance(items, str):
            # Wrap stray strings to keep the rest of the pipeline safe
            items = [{"title": items, "source": "unknown", "date": "", "link": ""}]
            self._dbg("wrapped string items", items)

        if not isinstance(items, list):
            self._dbg("items not a list; forcing []", items)
            items = []

        # Keep only dict entries and show first one for inspection
        items = [i for i in items if isinstance(i, dict)]
        if items:
            self._dbg("items[0] keys", list(items[0].keys()))

        # Update state (same pattern as AINewsNode)
        state["emerging_data"] = items
        self.state["emerging_data"] = state["emerging_data"]
        return state

    def summarize_emerging(self, state: dict) -> dict:
        """
        Summarize the fetched emerging topics into markdown format.

        Args:
            state (dict): State containing 'emerging_data'.

        Returns:
            dict: Updated state with 'summary' key containing markdown text.
        """
        topics = self.state.get("emerging_data", [])
        self._dbg("summarize_emerging topics", topics)

        # Build articles string (defensive)
        lines = []
        for idx, t in enumerate(topics):
            if not isinstance(t, dict):
                self._dbg(f"topics[{idx}] not dict", t)
                continue

            title = t.get("title", "")
            source = t.get("source", "")
            link = t.get("link", "")
            date_val = t.get("date")

            if isinstance(date_val, datetime):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val) if date_val is not None else ""

            lines.append(f"Title: {title}\nSource: {source}\nURL: {link}\nDate: {date_str}")

        articles_str = "\n\n".join(lines)
        self._dbg("articles_str", articles_str)

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize emerging Generative AI items into markdown. For each item include:
            - Date in **YYYY-MM-DD** format (use given date)
            - A concise, newcomer-friendly summary
            - Source URL as link
            Use format:
            ### [Date]
            - [Summary](URL)"""),
            ("user", "Articles:\n{articles}")
        ])

        formatted = prompt_template.format(articles=articles_str)
        self._dbg("LLM prompt (formatted)", formatted)

        response = self.llm.invoke(formatted)
        self._dbg("LLM response", response)

        state["summary"] = getattr(response, "content", "")
        self.state["summary"] = state["summary"]
        return self.state

    def save_result(self, state: dict) -> dict:
        """
        Save the markdown summary to a file for later retrieval.

        Args:
            state (dict): State containing 'summary' and 'field'.

        Returns:
            dict: Updated state with 'filename' of the saved file.
        """
        field = self.state.get("field", "emerging")
        summary = self.state.get("summary", "")

        directory = "./EmergingTech"
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, f"{field}_summary.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {field.capitalize()} Emerging Tech Summary\n\n")
            f.write(summary)

        self._dbg("saved filename", filename)
        self.state["filename"] = filename
        return self.state
