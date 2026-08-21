from voice.text_to_speech import text_to_speech
import os

def test_tts_smoke():
    print("Testing TTS with gTTS...")
    text = "สวัสดีครับ ระบบทดสอบเสียง"
    path = text_to_speech(text)
    
    if path and os.path.exists(path):
        size = os.path.getsize(path)
        print(f"TTS Success: File created at {path}, size: {size} bytes")
        if size > 0:
            print("Smoke test passed: File is not empty.")
            os.remove(path)
            return True
        else:
            print("Smoke test failed: File is empty.")
            return False
    else:
        print("Smoke test failed: File not created.")
        return False

if __name__ == "__main__":
    if test_tts_smoke():
        exit(0)
    else:
        exit(1)
