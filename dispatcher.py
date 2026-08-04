from ai.router import route_request

def execute_task(task='chat', text='', **kwargs):
    if task == 'chat':
        return route_request(
            prompt=text,
            provider=kwargs.get('provider', 'auto'),
            is_vision=kwargs.get('is_vision', False),
            is_x_search=kwargs.get('is_x_search', False),
        )

    raise ValueError(f'Unknown task: {task}')
