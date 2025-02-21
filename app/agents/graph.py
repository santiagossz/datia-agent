from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langgraph.graph import END
from .workflow import Workflow


class AgentsGraph:
    def __init__(self):
        self.workflow = Workflow()
        self.graph = self.create_graph()

    def create_graph(self):
        graph = StateGraph(MessagesState)
        graph.add_node("extract_data_agent", self.workflow.extract_data_agent)
        graph.set_entry_point("extract_data_agent")
        graph.add_edge("extract_data_agent", END)
        return graph.compile()

    async def run_workflow(self, state):
        return await self.graph.ainvoke(state)
