from google import genai

try:
    client = genai.Client()

    # 1. สร้าง Chat Session
    chat = client.chats.create(model="gemini-3.6-flash")

    # 2. ส่งข้อความแรก
    print("=== Sending Turn 1 ===")
    response = chat.send_message("I have 2 dogs in my house.")
    print(f"Response: {response.text}\n")

    # 3. ส่งข้อความที่สอง (โมเดลจะจำบริบทจากข้อความแรกได้)
    print("=== Sending Turn 2 ===")
    response = chat.send_message("How many paws are in my house?")
    print(f"Response: {response.text}\n")

    # 4. ดึงและแสดงประวัติการสนทนาทั้งหมด
    print("=== Chat History ===")
    for message in chat.get_history():
        print(f"role - {message.role}: ", end="")
        print(message.parts[0].text)

except Exception as e:
    print(f"[Error]: {e}")
