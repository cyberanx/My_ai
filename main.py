import json
import os
import requests

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

KV = '''
<ChatRoot>:
    orientation: "vertical"
    spacing: dp(8)
    padding: dp(8)

    Label:
        text: "NOVA AI"
        font_size: "24sp"
        size_hint_y: None
        height: dp(50)

    ScrollView:
        id: scroll
        Label:
            id: chat
            text: root.chat_text
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1]
            halign: "left"
            valign: "top"
            padding: dp(10), dp(10)

    BoxLayout:
        size_hint_y: None
        height: dp(55)
        spacing: dp(5)

        TextInput:
            id: message
            hint_text: "Type message..."
            multiline: False
            on_text_validate: root.send_message()

        Button:
            text: "Send"
            size_hint_x: None
            width: dp(80)
            on_release: root.send_message()
'''

class ChatRoot(BoxLayout):
    chat_text = StringProperty("Nova: Hi Anand! 👋\\n\\n")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memory_file = "memory.json"
        self.memory = self.load_memory()

        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = "openai/gpt-4o-mini"

    def load_memory(self):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_memory(self):
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.memory,
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception:
            pass

    def send_message(self):
        text = self.ids.message.text.strip()

        if not text:
            return

        self.ids.message.text = ""

        self.chat_text += f"Anand: {text}\\n"

        if text.lower() in ["exit", "quit"]:
            App.get_running_app().stop()
            return

        answer = self.ask_ai(text)

        self.chat_text += f"Nova: {answer}\\n\\n"

        self.save_memory()

    def ask_ai(self, user_text):

        if not self.api_key:
            return "API key set nahi hai."

        system_prompt = f"""
You are Nova, Anand's personal AI assistant.

Known memory:
{json.dumps(self.memory, ensure_ascii=False)}

Speak naturally in Hindi, Hinglish, or English.
Keep normal replies concise and friendly.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_text
            }
        ]

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages
                },
                timeout=60
            )

            data = response.json()

            if response.status_code != 200:
                return "API error: " + str(data)

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            return "Connection error: " + str(e)


class NovaApp(App):

    def build(self):
        Builder.load_string(KV)
        return ChatRoot()


if __name__ == "__main__":
    NovaApp().run()
