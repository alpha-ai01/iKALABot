import importlib

# รายชื่อฟังก์ชันที่มีในโปรเจกต์และ mapping กับคำสั่ง/โหมด
TASK_MAP = {
    "search": "add_search_tool",
    "image_gen": "add_image_generation",
    "deep_research": "run_deep_research",
    "pdf": "run_pdf_research_task",
    "local_image": "run_local_image_analysis",
    "url_summary": "run_url_summary",
    "openrouter_stream": "add_openrouter_stream",
    "fibonacci": "run_fibonacci_task",
}

def execute_task(task_name, *args, **kwargs):
    """
    ฟังก์ชันกลางสำหรับดึงสคริปต์ย่อยมาทำงานโดยไม่ต้องแก้ไฟล์หลักบ่อยๆ
    """
    module_name = TASK_MAP.get(task_name)
    if not module_name:
        return f"Task '{task_name}' not found."
    
    try:
        mod = importlib.import_module(module_name)
        # เรียกใช้ฟังก์ชัน main หรือ run ภายในโมดูลนั้นๆ
        if hasattr(mod, "run"):
            return mod.run(*args, **kwargs)
        elif hasattr(mod, "main"):
            return mod.main(*args, **kwargs)
        return f"Module '{module_name}' imported successfully."
    except Exception as e:
        return f"Error executing {task_name}: {str(e)}"
