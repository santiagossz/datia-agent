from langchain_openai import ChatOpenAI
from app.config import agent_cfg, logger
from .tools import tools
from typing import TypedDict, Annotated, Sequence, Literal, List
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import add_messages
from langgraph.graph import END
from langgraph.types import Command, interrupt
import pandas as pd


class InputState(TypedDict):
    user_input: Annotated[Sequence[HumanMessage], add_messages]


class WorkflowState(InputState):
    ai_response: Annotated[Sequence[AIMessage], add_messages]
    tool_call: dict
    data: dict
    plot: Annotated[List[str], lambda x, y: x + y]
    new_plot: Annotated[List[str], lambda x, y: x + y]
    link: str


class Workflow:
    def __init__(self):
        self.llm = ChatOpenAI(model=agent_cfg.OPENAI_MODEL)
        self.llm_mini = ChatOpenAI(model=agent_cfg.OPENAI_MODEL_MINI)
        self.tools = tools
        self.tool_dict = {tool.name: tool for tool in self.tools}

    def router_agent(self, state):
        logger.info("Empezando el análisis de datos con DatIA AI")
        llm = self.llm.bind_tools(self.tools)
        res = llm.invoke([state["user_input"][-1]])
        if res.tool_calls:
            return {"tool_call": res.tool_calls}
        return {"ai_response": res}

    def router(self, state) -> Literal["extract_data_agent", END]:
        if state.get("tool_call", None):
            return "extract_data_agent"
        return END

    def extract_data_agent(self, state):
        tool_call = state["tool_call"][0]
        logger.info(
            f"La herramienta que se va a utilizar es: {tool_call['name'].upper()}"
        )
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = self.tool_dict[tool_name]
        tool_res = tool.invoke(tool_args)
        res = ToolMessage(content=tool_res, tool_call_id=tool_call["id"])
        logger.debug("El humano validará si la data es correcta")
        return {"data": res.content, "link": tool.link}

    def validate_data(self, state) -> Command[Literal["create_df"]]:
        _ = interrupt(
            {"validate_data": {"data_head": state["data"][:5], "link": state["link"]}}
        )
        return Command(
            goto="create_df",
        )

    def create_df(self, state):
        logger.info("Generando el dataframe que responderá a la pregunta")
        prompt = """
        You are an expert data analyst uisng pandas dataFrames
        ## Instructions:
        You will be given a pandas dataframe and a query.
        Your job is to generate a pandas dataframe that answers the query.
        1. Generate a pandas dataframe from the following data:
        <data>
        {data}
        </data>
        2. This is the query:
        <query>
        {query}
        </query>
        ## Response:
        Only return the pandas dataframe in json. nothing else.

        Important:
        - Don't make up data, only use the data provided.
        - Make sure the dataframe is in the correct format.
        """
        message = prompt.format(data=state["data"], query=state["user_input"][-1])
        df_json = self.llm.invoke(message)
        logger.debug(f"El dataframe generado es: {df_json.content}")
        return {"data": df_json}

    def plot_data_agent(self, state):
        logger.info("Generando la visualización que responderá a la pregunta")

        prompt = """
        You are an expert data analyst uisng pandas plotly dashboards
        ## Instructions:
        You will be given a pandas dataframe in json format.
        Your job is to generate a plotly dashboard from the dataframe.
        1. Generate a plotly dashboard from the following data:
        <data>
        {data}
        </data>
        2. Format the plotly dashboard in json format so it can be ready to plot 
        from plotly.io from_json method.
        ## Response:
        Only return the plotly dashboard ready to plot. nothing else.

        Notes:
        - Don't make up data, only use the data provided.
        - Make the plots beatiful with palette colors and good design.
        """
        message = prompt.format(data=state["data"])
        plot = self.llm.invoke(message)
        plot = plot.content.strip("```json").strip("```").strip()
        logger.debug(
            "El usuario validará si la visualización es de su preferencia o desea un cambio"
        )
        return {"plot": [plot]}

    def validate_plot(self, state) -> Command[Literal["analyze_data_agent"]]:
        human_validation = interrupt({"validate_plot": {"plot": state["plot"][-1]}})
        human_input = human_validation
        if human_input:
            prompt = """
            You are an expert data analyst uisng plotly dashboards
            ## Instructions:
            You will be given a plotly dashboard and a query.
            Your job is to update the plotly dashboard format based on the query.
            for example if the query says, "now in line chart and red color"
            generate a new plotly dashboard with the new format. Don't change any data,
            only the format.
            1. This is the data dataframe:
            <data>
            {data}
            </data>
            2. This is the plotly dashboard:
            <plot>
            {plot}
            </plot>
            3. This is the query:
            <query>
            {query}
            </query>
            ## Response:
            Only return the plotly dashboard ready to plot. nothing else.
            """
            message = prompt.format(
                plot=state["plot"],
                data=state["data"],
                query="now in line chart",
            )
            plot = self.llm.invoke(message)
            plot = plot.content.strip("```json").strip("```").strip()
        else:
            plot = state["plot"][-1]

        return Command(
            goto="analyze_data_agent",
            update={"new_plot": [plot]},
        )

    def analyze_data_agent(self, state):
        logger.info("Analizando la data para responder a la pregunta")
        prompt = """
        You are an expert data analyst. Use the following data to answer the query.
        ## Instructions:
        You will be given a pandas dataframe in json format.
        Your job is to generate an analysis of the dataframe based on the query.
        Reponse only in spanish
        1. This is the data dataframe:
        <data>
        {data}
        </data>
        2. This is the query:
        <query>
        {query}
        """
        message = prompt.format(data=state["data"], query=state["user_input"][-1])
        res = self.llm.invoke(message)
        return {"ai_response": res}
