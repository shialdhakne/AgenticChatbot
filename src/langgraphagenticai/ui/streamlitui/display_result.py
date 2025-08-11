# File: src/langgraphagenticai/ui/streamlitui/display_result.py
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json
import os
import glob  # ← added

class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
        print(user_message)
        if usecase =="Basic Chatbot":
                for event in graph.stream({'messages':("user",user_message)}):
                    print(event.values())
                    for value in event.values():
                        print(value['messages'])
                        with st.chat_message("user"):
                            st.write(user_message)
                        with st.chat_message("assistant"):
                            st.write(value["messages"].content)
                            
        elif usecase=="Chatbot With Web":
             # Prepare state and invoke the graph
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            for message in res['messages']:
                if type(message) == HumanMessage:
                    with st.chat_message("user"):
                        st.write(message.content)
                elif type(message)==ToolMessage:
                    with st.chat_message("ai"):
                        st.write("Tool Call Start")
                        st.write(message.content)
                        st.write("Tool Call End")
                elif type(message)==AIMessage and message.content:
                    with st.chat_message("assistant"):
                        st.write(message.content)
                        
        elif usecase == "AI News":
            frequency = self.user_message
            with st.spinner("Fetching and summarizing news... ⏳"):
                result = graph.invoke({"messages": frequency})
                try:
                    # Read the markdown file
                    AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                    with open(AI_NEWS_PATH, "r") as file:
                        markdown_content = file.read()

                    # Display the markdown content in Streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    
        # inside DisplayResultStreamlit.display_result_on_ui (or similar)
        # Inside your DisplayResultStreamlit.display_result_on_ui (or equivalent):

        elif usecase == "Emerging Tech Discovery":           

            # Only run on click (keep your existing flag logic)
            if st.session_state.get("IsFetchEmergingClicked", False):
                field = st.session_state.get("emerging_field", "Generative AI")

                with st.spinner("Discovering emerging AI topics… ⏳"):
                    state = graph.invoke({"messages": [HumanMessage(content=field)]})

                # Reset the flag so it doesn't keep re-running
                st.session_state.IsFetchEmergingClicked = False

                # 🔎 DEBUG: see what we actually got back
                # st.caption(f"🧪 ET debug — state keys: {list(state.keys()) if hasattr(state, 'keys') else type(state)}")

                # Prefer summary
                summary = state.get("summary") if isinstance(state, dict) else None
                if summary:
                    st.markdown(summary, unsafe_allow_html=True)
                    return

                # If summary missing, try raw items
                items = state.get("emerging_data", []) if isinstance(state, dict) else []
                if isinstance(items, list) and items:
                    for it in items:
                        title = it.get("title", "")
                        source = it.get("source", "")
                        link = it.get("link", "")
                        st.markdown(f"- **{title}** ({source}) — {link}")
                    return

                # Final fallback: read the saved file
                candidates = []

                # 1) exact filename returned by the graph (if any)
                if isinstance(state, dict):
                    fn = state.get("filename")
                    if fn:
                        candidates.append(fn)

                # 2) computed candidates (space and underscore versions)
                raw_field = (field or "emerging").strip()
                lower_field = raw_field.lower()
                candidates.append(os.path.join(".", "EmergingTech", f"{raw_field}_summary.md"))               # keeps spaces
                candidates.append(os.path.join(".", "EmergingTech", f"{lower_field}_summary.md"))            # lower w/ spaces
                candidates.append(os.path.join(".", "EmergingTech", f"{lower_field.replace(' ', '_')}_summary.md"))  # underscores

                # 3) last resort: any *_summary.md in the folder (pick most recent)
                all_md = sorted(
                    glob.glob(os.path.join(".", "EmergingTech", "*_summary.md")),
                    key=lambda p: os.path.getmtime(p),
                    reverse=True,
                )
                candidates.extend(all_md)

                # Try them in order
                picked = None
                for path in candidates:
                    if path and os.path.exists(path):
                        picked = path
                        break

                if picked:
                    with open(picked, "r", encoding="utf-8") as f:
                        st.markdown(f.read(), unsafe_allow_html=True)
                    # st.caption(f"📄 Showing: {picked}")
                else:
                    st.info("No emerging-tech data to display yet (no summary/emerging_data/MD file).")
            else:
                st.info("Enter a topic and click **Discover Emerging Tech**.")
