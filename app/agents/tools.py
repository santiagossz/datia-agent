import requests
from app.config import agent_cfg
from langchain.tools import BaseTool
import pandas as pd


class RetrieveDBTools(BaseTool):
    name: str
    description: str
    function_name: str
    webhook_url: str
    link: str

    def __init__(self):
        super().__init__()

    def invoke_n8n_webhook(self, url: str, function_name: str):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error invoking {function_name}: {e}"

    def _run(self):
        return self.invoke_n8n_webhook(self.webhook_url, self.function_name)


class InventoryDataTool(RetrieveDBTools):
    name: str = "inventory_data"
    description: str = "Get the inventory data. Used to answer all questions related to inventory and stock levels"
    function_name: str = "get_inventory_data"
    webhook_url: str = agent_cfg.INVENTORY_DATA_N8N_WEBHOOK
    link: str = "https://docs.google.com/spreadsheets/d/1Hlic_rMwEZAMWQ4YSZgvoOcBQi9dKhF2HzBif7vcr7E/edit?gid=256326229#gid=256326229"


class SalesDataTool(RetrieveDBTools):
    name: str = "sales_data"
    description: str = (
        "Get the sales data. Used to answer all questions related to sales"
    )
    function_name: str = "get_sales_data"
    webhook_url: str = agent_cfg.SALES_DATA_N8N_WEBHOOK
    link: str = "https://supabase.com/dashboard/project/bnuqyhrjybzqmbtlfghh/editor/30397?schema=public"


tools = [InventoryDataTool(), SalesDataTool()]
