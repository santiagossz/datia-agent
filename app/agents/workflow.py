from langchain_openai import ChatOpenAI
from app.config import agent_cfg, logger
from .tools import tools


class Workflow:
    def __init__(self):
        self.llm = ChatOpenAI(model=agent_cfg.OPENAI_MODEL)
        self.llm_mini = ChatOpenAI(model=agent_cfg.OPENAI_MODEL_MINI)

    async def extract_data_agent(self, state):
        # res = agent.run(state["messages"][-1])
        # return {"messages": res}

        llm = self.llm.bind_tools(tools)
        res = await llm.ainvoke(state["messages"])
        logger.debug(res.tool_calls)
        return {"messages": res}
