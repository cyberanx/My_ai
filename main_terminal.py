import json
import os
import subprocess
import requests

# =========================
# CONFIG
# =========================

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    API_KEY = input("Enter OpenRouter API Key: ").strip()

MODEL = "openai/gpt-4o-mini"

MEMORY_FILE = "memory.json"


# =========================
# MEMORY
# =========================

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


memory = load_memory()


# =========================
# PERSONAL AI
# =========================

system_prompt = f"""
You are Nova, Anand's personal AI assistant.

Known information about Anand:
{json.dumps(memory, ensure_ascii=False, indent=2)}

Use this information naturally when relevant.
Do not repeatedly mention his personal information unless it helps answer his question.

You can communicate in Hindi, Hinglish, or English.
Keep normal answers concise and natural.

You are a friendly personal assistant, not a fictional character.
"""


messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


# =========================
# APP COMMANDS
# =========================

APPS = {
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "settings": "com.android.settings",
    "calculator": "com.google.android.calculator"
}


def open_app(name):
    name = name.lower().strip()

    package = APPS.get(name)

    if not package:
        return f"I don't know how to open {name}."

    try:
        subprocess.run(
            [
                "monkey",
                "-p",
                package,
                "-c",
                "android.intent.category.LAUNCHER",
                "1"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return f"Opening {name}."

    except Exception as e:
        return f"Could not open {name}: {e}"


# =========================
# AI
# =========================

def ask_ai(user_text):

    messages.append({
        "role": "user",
        "content": user_text
    })

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",

            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },

            json={
                "model": MODEL,
                "messages": messages
            },

            timeout=60
        )

        data = response.json()

        if response.status_code != 200:
            return "API error: " + str(data)

        answer = data["choices"][0]["message"]["content"]

        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        return "Connection error: " + str(e)


# =========================
# VOICE
# =========================

def speak(text):

    try:
        subprocess.run(
            ["termux-tts-speak", "-r", "0.95", text],
            timeout=60
        )

    except Exception:
        pass


def listen():

    try:

        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=60
        )

        return result.stdout.strip()

    except Exception as e:

        print("Microphone error:", e)
        return ""


# =========================
# MAIN
# =========================

print()
print("=" * 40)
print("          NOVA AI ONLINE")
print("=" * 40)
print()
print("1 = Text Chat")
print("2 = Voice Chat")
print("Type 'exit' to quit.")
print()

mode = input("Choose mode: ").strip()


while True:

    # -------------------------
    # VOICE MODE
    # -------------------------

    if mode == "2":

        print("\n🎤 Listening...")

        user = listen()

        if not user:
            continue

        print("You:", user)

    # -------------------------
    # TEXT MODE
    # -------------------------

    else:

        user = input("\nYou: ").strip()

        if not user:
            continue

    # -------------------------
    # EXIT
    # -------------------------

    if user.lower() in ["exit", "quit", "bye"]:

        print("Nova: Goodbye Anand!")

        if mode == "2":
            speak("Goodbye Anand")

        break

    # -------------------------
    # APP OPENING
    # -------------------------

    lower = user.lower()

    if lower.startswith("open "):

        app_name = user[5:].strip()

        answer = open_app(app_name)

    else:

        answer = ask_ai(user)

    # -------------------------
    # RESPONSE
    # -------------------------

    print("\nNova:", answer)

    if mode == "2":
        speak(answer)
