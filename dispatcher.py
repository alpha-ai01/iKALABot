from ai.router import route_request

def execute_task(task="chat", text="", **kwargs):
    if task not in ["chat", "search"]:
        raise ValueError(f"Unknown task: {task}")

    return route_request(
        prompt=text,
        provider=kwargs.get("provider", "auto"),
        is_vision=kwargs.get("is_vision", False),
        is_x_search=(task == "search"),
    )
