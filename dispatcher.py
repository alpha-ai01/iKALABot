from ai.router import route_request
from services.tool_router import ToolRouter

router = ToolRouter()

def execute_task(task="chat", text="", images=None, chat_id=None, **kwargs):
    """Unified execution entry point."""
    # Check if it's a tool task handled by ToolRouter
    tool_result = router.route(task, text=text, **kwargs)
    if tool_result:
        return tool_result
        
    # Route all other tasks (including multimodal) through Unified Router
    return route_request(
        prompt=text,
        images=images,
        is_vision=(images is not None),
        is_complex=kwargs.get("is_complex", False),
        chat_id=chat_id
    )
