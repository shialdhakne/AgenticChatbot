from langgraph.graph import StateGraph, START, END
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.tools.search_tool import get_tool, create_tool_node
from langgraph.prebuilt import tools_condition,ToolNode 
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode
from src.langgraphagenticai.nodes.ai_news_node import AINewsNode
from src.langgraphagenticai.tools.emerging_discovery_tool import get_emerging_discovery_tool
from langgraph.prebuilt import ToolNode
from src.langgraphagenticai.nodes.emerging_tech_node import EmergingTechNode

class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder =  StateGraph(State)
        
    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.
        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        
        self.basic_chatbot_node=BasicChatbotNode(self.llm)
        
        
        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START, "chatbot")        
        self.graph_builder.add_edge("chatbot", END)
        
    
    def chatbot_with_tools_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        # Define tool and tool node
        tools=get_tool()
        tool_node=create_tool_node(tools)

        ## Define the LLM
        llm=self.llm

        ## Define the chatbot node

        obj_chatbot_with_node=ChatbotWithToolNode(llm)
        chatbot_node=obj_chatbot_with_node.create_chatbot(tools)
        ## Add nodes
        self.graph_builder.add_node("chatbot",chatbot_node)
        self.graph_builder.add_node("tools",tool_node)
        # Define conditional and direct edges
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")
       
    
    def ai_news_builder_graph(self):

        ai_news_node=AINewsNode(self.llm)

        ## added the nodes

        self.graph_builder.add_node("fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news",ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result",ai_news_node.save_result)

        #added the edges

        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news","summarize_news")
        self.graph_builder.add_edge("summarize_news","save_result")
        self.graph_builder.add_edge("save_result", END)   
        
    def emerging_tech_builder_graph(self):
        node = EmergingTechNode(self.llm)
        self.graph_builder.add_node("fetch_emerging", node.fetch_emerging)
        self.graph_builder.add_node("summarize_emerging", node.summarize_emerging)
        self.graph_builder.add_node("save_emerging", node.save_result)
        self.graph_builder.set_entry_point("fetch_emerging")
        self.graph_builder.add_edge("fetch_emerging", "summarize_emerging")
        self.graph_builder.add_edge("summarize_emerging", "save_emerging")
        self.graph_builder.add_edge("save_emerging", END) 
    
       
    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        if usecase == "Chatbot With Web":
            self.chatbot_with_tools_build_graph()
        if usecase == "AI News":
            self.ai_news_builder_graph()        
        if usecase == "Emerging Tech Discovery":
            self.emerging_tech_builder_graph()


        return self.graph_builder.compile()

        