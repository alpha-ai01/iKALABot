from utils.text_utils import clean_ai_response

def test_sanitizer_plain_text():
    # Test markdown removal
    assert clean_ai_response("## Hello **World**!") == "Hello World"
    # Test symbols removal
    assert clean_ai_response("Hello @World %25") == "Hello World 25"
    # Test deduplication
    assert clean_ai_response("Line 1\n\nLine 1\n\nLine 2") == "Line 1\n\nLine 2"
