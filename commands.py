import subprocess


APPS = {
    "youtube": "com.google.android.youtube",
    "chrome": "com.android.chrome",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "settings": "com.android.settings",
    "calculator": "com.google.android.calculator",
}


def open_app(app_name):
    app_name = app_name.lower().strip()

    package = APPS.get(app_name)

    if not package:
        return f"I don't know how to open {app_name} yet."

    try:
        subprocess.run(
            [
                "monkey",
                "-p",
                package,
                "-c",
                "android.intent.category.LAUNCHER",
                "1",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return f"Opening {app_name}."

    except Exception as e:
        return f"Could not open {app_name}: {e}"


def handle_command(text):
    text = text.lower().strip()

    if text.startswith("open "):
        app_name = text[5:].strip()
        return open_app(app_name)

    return None
