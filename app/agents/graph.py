from langgraph.graph import StateGraph
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from .workflow import Workflow, InputState, WorkflowState
from app.config import logger


class AgentsGraph:
    def __init__(self):
        self.memory = MemorySaver()
        self.workflow = Workflow()
        self.graph = self.create_graph()

    def create_graph(self):
        graph = StateGraph(WorkflowState, input=InputState)

        graph.add_node("router_agent", self.workflow.router_agent)
        graph.add_node("extract_data_agent", self.workflow.extract_data_agent)
        graph.add_node("validate_data", self.workflow.validate_data)
        graph.add_node("create_df", self.workflow.create_df)
        graph.add_node("plot_data_agent", self.workflow.plot_data_agent)
        graph.add_node("validate_plot", self.workflow.validate_plot)
        graph.add_node("analyze_data_agent", self.workflow.analyze_data_agent)

        graph.set_entry_point("router_agent")
        graph.add_conditional_edges(
            "router_agent",
            self.workflow.router,
        )
        graph.add_edge("extract_data_agent", "validate_data")
        graph.add_edge("create_df", "plot_data_agent")
        graph.add_edge("plot_data_agent", "validate_plot")
        graph.add_edge("analyze_data_agent", END)

        # graph.add_edge("validate_plot_agent", "analyze_data_agent")
        # graph.add_edge("analyze_data_agent", END)
        return graph.compile(checkpointer=self.memory)

    def run_workflow(self, state, config):
        return self.graph.invoke(state, config)

    def run_stream_workflow(self, state, config):
        for chunk in self.graph.stream(state, config, stream_mode="updates"):
            print(chunk)

    def get_memory(self, config):
        return self.graph.get_state(config).values
