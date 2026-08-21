from utils.text_utils import clean_ai_response

def test_cleaner():
    test_cases = [
        ("**Hello**", "Hello"),
        ("*World*", "World"),
        ("### Title\n\nContent", "Title\n\nContent"),
        ("```text\nCode\n```", "Code"),
        ("[Link](url)", "Link"),
        ("Line 1\n\n\nLine 2", "Line 1\n\nLine 2"),
        ("2 * 5 = 10", "2 * 5 = 10") # Should not break this
    ]
    
    for input_text, expected in test_cases:
        result = clean_ai_response(input_text)
        assert result == expected, f"Failed for {input_text}: Expected {expected}, got {result}"
        print(f"Passed: {input_text} -> {result}")

if __name__ == "__main__":
    test_cleaner()
    print("All tests passed!")
