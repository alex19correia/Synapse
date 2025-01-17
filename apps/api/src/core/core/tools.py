class ToolManager:
    def __init__(self):
        self.available_tools = {}
        
    def register_tool(self, name: str, tool_fn):
        """Registra uma nova ferramenta"""
        self.available_tools[name] = tool_fn 