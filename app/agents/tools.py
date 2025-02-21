import requests
from langchain_core.tools import tool
from app.config import agent_cfg


def invoke_n8n_webhook(url: str, function_name: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Error invoking {function_name}: {e}"


@tool
def get_inventory_data():
    """Get the inventory data. Used to answer all questions related to inventory and stock levels"""
    return invoke_n8n_webhook(
        agent_cfg.INVENTORY_DATA_N8N_WEBHOOK, "get_inventory_data"
    )


@tool
def get_sales_data():
    """Get the sales data. Used to answer all questions related to sales"""
    return invoke_n8n_webhook(agent_cfg.SALES_DATA_N8N_WEBHOOK, "get_sales_data")


tools = [get_inventory_data, get_sales_data]

# agent = Agent(settings.OPENAI_MODEL_MINI)


# def invoke_n8n_webhook(url: str, function_name: str):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         return f"Error invoking {function_name}: {e}"


# @agent.tool_plain
# def get_inventory_data():
#     """Get the inventory data. Used to answer all questions related to inventory and stock levels"""
#     return invoke_n8n_webhook(settings.INVENTORY_DATA_N8N_WEBHOOK, "get_inventory_data")


# @agent.tool_plain
# def get_sales_data():
#     """Get the sales data. Used to answer all questions related to sales"""
#     return invoke_n8n_webhook(settings.SALES_DATA_N8N_WEBHOOK, "get_sales_data")
