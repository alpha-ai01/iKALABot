from ai.router import route_request
from services.tool_router import ToolRouter

router = ToolRouter()

def execute_task(task="chat", text="", **kwargs):
    # Check if it's a tool task handled by ToolRouter
    tool_result = router.route(task, text=text, **kwargs)
    if tool_result:
        return tool_result
        
    if task not in ["chat", "search"]:
        raise ValueError(f"Unknown task: {task}")

    return route_request(
        prompt=text,
        provider=kwargs.get("provider", "auto"),
        is_vision=kwargs.get("is_vision", False),
        is_x_search=(task == "search"),
    )
