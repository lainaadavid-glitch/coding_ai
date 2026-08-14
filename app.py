import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from dotenv import load_dotenv
import requests
import threading
import json
import subprocess
import keyword
import re
import os


# =========================================================
# ENVIRONMENT SETTINGS
# =========================================================

load_dotenv()

MODEL = os.getenv("MODEL")
URL = os.getenv("URL")

conversation = []

current_file = None
project_folder = None

ai_running = False
stop_requested = False


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()
window.title("🤖 My Coding AI")
window.geometry("1350x850")
window.configure(bg="#202123")


# =========================================================
# COLORS
# =========================================================

BG = "#202123"
SIDEBAR = "#18191c"
CHAT_BG = "#343541"
EDITOR_BG = "#1e1e1e"
INPUT_BG = "#40414F"


# =========================================================
# UTILITY
# =========================================================

def set_status(text):
    window.after(
        0,
        lambda: status.config(text=text)
    )


def add_text(text, tag="ai"):
    chat.insert(
        tk.END,
        text,
        tag
    )
    chat.see(tk.END)


def clear_main_area():
    for widget in content_frame.winfo_children():
        widget.destroy()


def show_page(page):
    clear_main_area()

    if page == "chat":
        create_chat_page()

    elif page == "debug":
        create_debug_page()

    elif page == "generate":
        create_generator_page()

    elif page == "run":
        create_runner_page()

    elif page == "projects":
        create_projects_page()

    elif page == "settings":
        create_settings_page()


# =========================================================
# AI BUTTON CONTROL
# =========================================================

def disable_ai_buttons():
    global ai_running

    ai_running = True

    send_button.config(state=tk.DISABLED)

    if debug_button:
        debug_button.config(state=tk.DISABLED)

    if generate_button:
        generate_button.config(state=tk.DISABLED)

    stop_button.config(state=tk.NORMAL)


def finished():
    global ai_running
    global stop_requested

    ai_running = False
    stop_requested = False

    if send_button:
        send_button.config(state=tk.NORMAL)

    if debug_button:
        debug_button.config(state=tk.NORMAL)

    if generate_button:
        generate_button.config(state=tk.NORMAL)

    stop_button.config(state=tk.DISABLED)

    set_status("🟢 Ready")

    entry.focus()


# =========================================================
# NORMAL CHAT
# =========================================================

def ask_ai():

    question = entry.get().strip()

    if not question:
        return

    entry.delete(0, tk.END)

    chat.insert(
        tk.END,
        f"\nYou: {question}\n\n",
        "user"
    )

    chat.insert(
        tk.END,
        "AI: ",
        "ai"
    )

    chat.see(tk.END)

    disable_ai_buttons()

    set_status("🤔 AI is thinking...")

    threading.Thread(
        target=get_ai_response,
        args=(question,),
        daemon=True
    ).start()


def get_ai_response(question):

    conversation.append(
        f"User: {question}"
    )

    system_prompt = """
You are Coding AI, a friendly programming tutor.

Rules:
- Explain programming in simple language.
- Assume the user is a beginner.
- Give examples when useful.
- Explain code you provide.
- Help find and fix errors.
- Teach the user instead of only giving answers.
"""

    history = "\n".join(conversation)

    prompt = (
        system_prompt
        + "\n\nConversation:\n"
        + history
        + "\nAI:"
    )

    send_to_ollama(prompt)


# =========================================================
# DEBUGGER
# =========================================================

def debug_code():

    code = debug_box.get(
        "1.0",
        tk.END
    ).strip()

    if not code:
        set_status("⚠️ Paste Python code first")
        return

    chat.insert(
        tk.END,
        "\n🐛 Code to analyze:\n",
        "user"
    )

    chat.insert(
        tk.END,
        code + "\n\n",
        "code"
    )

    chat.insert(
        tk.END,
        "AI: ",
        "ai"
    )

    chat.see(tk.END)

    disable_ai_buttons()

    set_status("🔍 Analyzing code...")

    threading.Thread(
        target=analyze_code,
        args=(code,),
        daemon=True
    ).start()


def analyze_code(code):

    prompt = f"""
You are an expert Python debugging assistant.

Analyze this Python code.

Do these things:

1. Find syntax errors.
2. Find logical errors.
3. Explain each problem simply.
4. Provide corrected code.
5. Explain what you changed.

Code:

{code}

Give your answer clearly and make it easy
for a beginner to understand.
"""

    send_to_ollama(prompt)


# =========================================================
# CODE GENERATOR
# =========================================================

def generate_code():

    request = generator_entry.get().strip()

    if not request:
        return

    generator_entry.delete(0, tk.END)

    chat.insert(
        tk.END,
        f"\n💻 Generate: {request}\n\n",
        "user"
    )

    chat.insert(
        tk.END,
        "AI: ",
        "ai"
    )

    chat.see(tk.END)

    disable_ai_buttons()

    set_status("💻 Generating code...")

    prompt = f"""
You are an expert Python programmer.

The user wants you to create code.

User request:

{request}

Rules:

- Write clean Python code.
- Keep it beginner-friendly.
- Make the code complete.
- Explain what the code does.
- Explain important parts of the code.
"""

    threading.Thread(
        target=send_to_ollama,
        args=(prompt,),
        daemon=True
    ).start()


# =========================================================
# OLLAMA
# =========================================================

def send_to_ollama(prompt):

    global stop_requested

    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True
    }

    try:

        response = requests.post(
            URL,
            json=data,
            stream=True,
            timeout=300
        )

        response.raise_for_status()

        full_answer = ""

        for line in response.iter_lines():

            if stop_requested:
                break

            if line:

                result = json.loads(
                    line.decode("utf-8")
                )

                text = result.get(
                    "response",
                    ""
                )

                full_answer += text

                window.after(
                    0,
                    lambda text=text: add_text(text)
                )

        if stop_requested:

            window.after(
                0,
                lambda: add_text(
                    "\n\n⛔ Response stopped.\n"
                )
            )

        else:

            conversation.append(
                f"AI: {full_answer}"
            )

        window.after(
            0,
            finished
        )

    except requests.exceptions.ConnectionError:

        window.after(
            0,
            lambda: add_text(
                "\n❌ Can't connect to the AI service.\n"
            )
        )

        window.after(
            0,
            finished
        )

    except requests.exceptions.Timeout:

        window.after(
            0,
            lambda: add_text(
                "\n⏳ AI took too long to respond.\n"
            )
        )

        window.after(
            0,
            finished
        )

    except Exception as error:

        window.after(
            0,
            lambda: add_text(
                f"\n❌ Error: {error}\n"
            )
        )

        window.after(
            0,
            finished
        )


# =========================================================
# STOP RESPONSE
# =========================================================

def stop_response():

    global stop_requested

    if not ai_running:
        return

    stop_requested = True

    set_status("⛔ Stopping response...")


# =========================================================
# RUN CODE
# =========================================================

def run_code():

    code = runner_box.get(
        "1.0",
        tk.END
    ).strip()

    if not code:
        set_status("⚠️ Paste Python code first")
        return

    output_box.delete(
        "1.0",
        tk.END
    )

    set_status("▶️ Running Python...")

    threading.Thread(
        target=execute_code,
        args=(code,),
        daemon=True
    ).start()


def execute_code(code):

    try:

        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = ""

        if result.stdout:

            output += (
                "📤 Output:\n"
                + result.stdout
            )

        if result.stderr:

            output += (
                "\n❌ Error:\n"
                + result.stderr
            )

        if not output:

            output = (
                "✅ Code finished successfully."
            )

        window.after(
            0,
            lambda: show_runner_output(output)
        )

    except subprocess.TimeoutExpired:

        window.after(
            0,
            lambda: show_runner_output(
                "⏳ Code took too long and was stopped."
            )
        )

    except Exception as error:

        window.after(
            0,
            lambda: show_runner_output(
                f"❌ Error: {error}"
            )
        )


def show_runner_output(output):

    output_box.delete(
        "1.0",
        tk.END
    )

    output_box.insert(
        tk.END,
        output
    )

    set_status("🟢 Code finished")


# =========================================================
# CLEAR CHAT
# =========================================================

def clear_chat():

    conversation.clear()

    if chat:

        chat.delete(
            "1.0",
            tk.END
        )

        chat.insert(
            tk.END,
            "🤖 Coding AI\n\n",
            "title"
        )

    set_status("🧹 Chat cleared")


# =========================================================
# PROJECT FUNCTIONS
# =========================================================

def open_project():

    global project_folder

    folder = filedialog.askdirectory(
        title="Open Python Project"
    )

    if not folder:
        return

    project_folder = folder

    refresh_project()

    set_status(
        f"📁 Project opened: {os.path.basename(folder)}"
    )


def refresh_project():

    if not project_folder:
        return

    file_tree.delete(
        0,
        tk.END
    )

    try:

        items = os.listdir(
            project_folder
        )

        folders = []
        files = []

        for item in items:

            path = os.path.join(
                project_folder,
                item
            )

            if os.path.isdir(path):

                folders.append(item)

            elif item.endswith(".py"):

                files.append(item)

        for folder in sorted(folders):

            file_tree.insert(
                tk.END,
                f"📁 {folder}"
            )

        for file in sorted(files):

            file_tree.insert(
                tk.END,
                f"🐍 {file}"
            )

    except Exception as error:

        messagebox.showerror(
            "Project Error",
            str(error)
        )


def open_project_file(event=None):

    global current_file

    selection = file_tree.curselection()

    if not selection:
        return

    item = file_tree.get(
        selection[0]
    )

    if not item.startswith("🐍"):
        return

    filename = item[2:].strip()

    path = os.path.join(
        project_folder,
        filename
    )

    open_python_file(path)


def open_python_file(path):

    global current_file

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            code = file.read()

        current_file = path

        set_status(
            f"📂 Opened {os.path.basename(path)}"
        )

        if current_page == "projects":

            project_editor.delete(
                "1.0",
                tk.END
            )

            project_editor.insert(
                "1.0",
                code
            )

    except Exception as error:

        messagebox.showerror(
            "File Error",
            str(error)
        )


def new_python_file():

    global current_file

    if not project_folder:

        messagebox.showwarning(
            "No Project",
            "Open a project folder first."
        )

        return

    filename = filedialog.asksaveasfilename(
        title="Create Python File",
        initialdir=project_folder,
        defaultextension=".py",
        filetypes=[
            ("Python Files", "*.py")
        ]
    )

    if not filename:
        return

    try:

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "# New Python file\n"
            )

        current_file = filename

        refresh_project()

        set_status(
            "📄 New Python file created"
        )

    except Exception as error:

        messagebox.showerror(
            "Create Error",
            str(error)
        )


def save_project_file():

    global current_file

    if not current_file:
        save_file()
        return

    try:

        code = project_editor.get(
            "1.0",
            tk.END
        ).rstrip()

        with open(
            current_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(code)

        refresh_project()

        set_status(
            f"💾 Saved {os.path.basename(current_file)}"
        )

    except Exception as error:

        messagebox.showerror(
            "Save Error",
            str(error)
        )


def save_file():

    global current_file

    code = project_editor.get(
        "1.0",
        tk.END
    ).rstrip()

    if not code:
        return

    file_path = filedialog.asksaveasfilename(
        title="Save Python File",
        defaultextension=".py",
        filetypes=[
            ("Python Files", "*.py"),
            ("All Files", "*.*")
        ]
    )

    if not file_path:
        return

    try:

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(code)

        current_file = file_path

        if project_folder:
            refresh_project()

        set_status(
            f"💾 Saved {os.path.basename(file_path)}"
        )

    except Exception as error:

        messagebox.showerror(
            "Save Error",
            str(error)
        )


def delete_project_file():

    global current_file

    selection = file_tree.curselection()

    if not selection:
        return

    item = file_tree.get(
        selection[0]
    )

    if not item.startswith("🐍"):
        return

    filename = item[2:].strip()

    path = os.path.join(
        project_folder,
        filename
    )

    answer = messagebox.askyesno(
        "Delete File",
        f"Delete {filename}?"
    )

    if not answer:
        return

    try:

        os.remove(path)

        if current_file == path:
            current_file = None

        refresh_project()

        set_status(
            f"🗑️ Deleted {filename}"
        )

    except Exception as error:

        messagebox.showerror(
            "Delete Error",
            str(error)
        )


# =========================================================
# SETTINGS
# =========================================================

def create_settings_page():

    title_label = tk.Label(
        content_frame,
        text="⚙️ Settings",
        font=("Arial", 20, "bold"),
        bg=BG,
        fg="white"
    )

    title_label.pack(
        pady=25
    )

    info = tk.Label(
        content_frame,
        text=(
            "Private AI configuration is loaded automatically.\n"
            "Sensitive configuration is not displayed here."
        ),
        font=("Arial", 12),
        bg=BG,
        fg="#aaaaaa"
    )

    info.pack(
        pady=10
    )

    clear_button = tk.Button(
        content_frame,
        text="🧹 Clear Conversation",
        command=clear_chat,
        width=25
    )

    clear_button.pack(
        pady=10
    )

    theme_label = tk.Label(
        content_frame,
        text="🎨 Interface",
        font=("Arial", 13, "bold"),
        bg=BG,
        fg="white"
    )

    theme_label.pack(
        pady=(30, 5)
    )

    dark_button = tk.Button(
        content_frame,
        text="🌙 Dark Theme",
        command=lambda: set_theme("dark"),
        width=25
    )

    dark_button.pack(
        pady=5
    )


def set_theme(theme):

    if theme == "dark":

        window.configure(
            bg="#202123"
        )

        set_status(
            "🌙 Dark theme enabled"
        )


# =========================================================
# CHAT PAGE
# =========================================================

def create_chat_page():

    global chat
    global entry
    global send_button
    global debug_button
    global generate_button
    global stop_button

    title = tk.Label(
        content_frame,
        text="💬 AI CHAT",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg="white"
    )

    title.pack(
        pady=8
    )

    chat = scrolledtext.ScrolledText(
        content_frame,
        wrap=tk.WORD,
        font=("Arial", 12),
        bg=CHAT_BG,
        fg="white",
        insertbackground="white"
    )

    chat.pack(
        padx=10,
        pady=5,
        fill=tk.BOTH,
        expand=True
    )

    chat.tag_config(
        "user",
        foreground="#00ff88",
        font=("Arial", 12, "bold")
    )

    chat.tag_config(
        "ai",
        foreground="white"
    )

    chat.tag_config(
        "code",
        foreground="#00ffff",
        font=("Consolas", 11)
    )

    chat.tag_config(
        "title",
        foreground="#00ff88",
        font=("Arial", 15, "bold")
    )

    chat.insert(
        tk.END,
        "🤖 Coding AI\n\n",
        "title"
    )

    bottom = tk.Frame(
        content_frame,
        bg=BG
    )

    bottom.pack(
        fill=tk.X,
        padx=10,
        pady=8
    )

    entry = tk.Entry(
        bottom,
        font=("Arial", 13),
        bg=INPUT_BG,
        fg="white",
        insertbackground="white"
    )

    entry.pack(
        side=tk.LEFT,
        fill=tk.X,
        expand=True,
        ipady=8
    )

    send_button = tk.Button(
        bottom,
        text="💬 Send",
        command=ask_ai
    )

    send_button.pack(
        side=tk.LEFT,
        padx=3
    )

    debug_button = tk.Button(
        bottom,
        text="🐛 Debug Code",
        command=lambda: show_page("debug")
    )

    debug_button.pack(
        side=tk.LEFT,
        padx=3
    )

    generate_button = tk.Button(
        bottom,
        text="💻 Generate",
        command=lambda: show_page("generate")
    )

    generate_button.pack(
        side=tk.LEFT,
        padx=3
    )

    stop_button = tk.Button(
        bottom,
        text="⛔ Stop",
        command=stop_response,
        state=tk.DISABLED
    )

    stop_button.pack(
        side=tk.LEFT,
        padx=3
    )

    entry.bind(
        "<Return>",
        lambda event: ask_ai()
    )

    entry.focus()


# =========================================================
# DEBUG PAGE
# =========================================================

def create_debug_page():

    global debug_box

    title = tk.Label(
        content_frame,
        text="🐛 CODE DEBUGGER",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg="white"
    )

    title.pack(
        pady=10
    )

    debug_box = scrolledtext.ScrolledText(
        content_frame,
        font=("Consolas", 11),
        bg=EDITOR_BG,
        fg="white",
        insertbackground="white"
    )

    debug_box.pack(
        padx=20,
        pady=10,
        fill=tk.BOTH,
        expand=True
    )

    button = tk.Button(
        content_frame,
        text="🐛 Debug Code",
        command=debug_code
    )

    button.pack(
        pady=10
    )


# =========================================================
# GENERATOR PAGE
# =========================================================

def create_generator_page():

    global generator_entry

    title = tk.Label(
        content_frame,
        text="💻 CODE GENERATOR",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg="white"
    )

    title.pack(
        pady=15
    )

    label = tk.Label(
        content_frame,
        text="Describe the Python program you want:",
        font=("Arial", 12),
        bg=BG,
        fg="white"
    )

    label.pack(
        pady=5
    )

    generator_entry = tk.Entry(
        content_frame,
        font=("Arial", 13),
        bg=INPUT_BG,
        fg="white",
        insertbackground="white"
    )

    generator_entry.pack(
        padx=30,
        fill=tk.X,
        ipady=10
    )

    button = tk.Button(
        content_frame,
        text="💻 Generate Code",
        command=generate_code
    )

    button.pack(
        pady=15
    )

    generator_entry.focus()


# =========================================================
# RUNNER PAGE
# =========================================================

def create_runner_page():

    global runner_box
    global output_box

    title = tk.Label(
        content_frame,
        text="▶️ PYTHON RUNNER",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg="white"
    )

    title.pack(
        pady=10
    )

    runner_box = scrolledtext.ScrolledText(
        content_frame,
        height=15,
        font=("Consolas", 11),
        bg=EDITOR_BG,
        fg="white",
        insertbackground="white"
    )

    runner_box.pack(
        padx=20,
        pady=10,
        fill=tk.BOTH,
        expand=True
    )

    run_button = tk.Button(
        content_frame,
        text="▶️ Run Code",
        command=run_code
    )

    run_button.pack(
        pady=5
    )

    output_label = tk.Label(
        content_frame,
        text="📤 Output",
        font=("Arial", 12, "bold"),
        bg=BG,
        fg="white"
    )

    output_label.pack(
        pady=5
    )

    output_box = scrolledtext.ScrolledText(
        content_frame,
        height=8,
        font=("Consolas", 11),
        bg="#111111",
        fg="#00ff88"
    )

    output_box.pack(
        padx=20,
        pady=5,
        fill=tk.X
    )


# =========================================================
# PROJECT PAGE
# =========================================================

def create_projects_page():

    global file_tree
    global project_editor

    title = tk.Label(
        content_frame,
        text="📁 PROJECTS",
        font=("Arial", 18, "bold"),
        bg=BG,
        fg="white"
    )

    title.pack(
        pady=8
    )

    toolbar = tk.Frame(
        content_frame,
        bg=BG
    )

    toolbar.pack(
        fill=tk.X,
        padx=10
    )

    tk.Button(
        toolbar,
        text="📂 Open Project",
        command=open_project
    ).pack(
        side=tk.LEFT,
        padx=3
    )

    tk.Button(
        toolbar,
        text="➕ New Python File",
        command=new_python_file
    ).pack(
        side=tk.LEFT,
        padx=3
    )

    tk.Button(
        toolbar,
        text="🔄 Refresh",
        command=refresh_project
    ).pack(
        side=tk.LEFT,
        padx=3
    )

    tk.Button(
        toolbar,
        text="💾 Save",
        command=save_project_file
    ).pack(
        side=tk.LEFT,
        padx=3
    )

    body = tk.Frame(
        content_frame,
        bg=BG
    )

    body.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=10
    )

    file_tree = tk.Listbox(
        body,
        width=25,
        bg="#252526",
        fg="white",
        selectbackground="#44475a",
        font=("Consolas", 10),
        borderwidth=0
    )

    file_tree.pack(
        side=tk.LEFT,
        fill=tk.Y
    )

    file_tree.bind(
        "<Double-Button-1>",
        open_project_file
    )

    project_editor = scrolledtext.ScrolledText(
        body,
        font=("Consolas", 11),
        bg=EDITOR_BG,
        fg="white",
        insertbackground="white",
        undo=True,
        wrap=tk.NONE
    )

    project_editor.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True,
        padx=(10, 0)
    )

    refresh_project()


# =========================================================
# SIDEBAR
# =========================================================

sidebar = tk.Frame(
    window,
    width=200,
    bg=SIDEBAR
)

sidebar.pack(
    side=tk.LEFT,
    fill=tk.Y
)

sidebar.pack_propagate(
    False
)


title = tk.Label(
    sidebar,
    text="🤖 CODING AI",
    font=("Arial", 16, "bold"),
    bg=SIDEBAR,
    fg="white"
)

title.pack(
    pady=20
)


def sidebar_button(text, page):

    button = tk.Button(
        sidebar,
        text=text,
        command=lambda: show_page(page),
        anchor="w",
        padx=15,
        bg="#252526",
        fg="white",
        activebackground="#44475a",
        activeforeground="white",
        relief=tk.FLAT
    )

    button.pack(
        fill=tk.X,
        padx=10,
        pady=3
    )


sidebar_button("💬 Chat", "chat")
sidebar_button("🐛 Debugger", "debug")
sidebar_button("💻 Generator", "generate")
sidebar_button("▶️ Runner", "run")
sidebar_button("📁 Projects", "projects")
sidebar_button("⚙️ Settings", "settings")


# =========================================================
# CONTENT AREA
# =========================================================

content_frame = tk.Frame(
    window,
    bg=BG
)

content_frame.pack(
    side=tk.LEFT,
    fill=tk.BOTH,
    expand=True
)


# =========================================================
# STATUS BAR
# =========================================================

status = tk.Label(
    window,
    text="🟢 Ready",
    bg="#18191c",
    fg="white",
    anchor="w"
)

status.pack(
    side=tk.BOTTOM,
    fill=tk.X
)


# =========================================================
# GLOBAL WIDGET REFERENCES
# =========================================================

chat = None
entry = None

send_button = None
debug_button = None
generate_button = None
stop_button = None

debug_box = None
generator_entry = None
runner_box = None
output_box = None

file_tree = None
project_editor = None

current_page = "chat"


# =========================================================
# PAGE WRAPPER
# =========================================================

_old_show_page = show_page


def show_page(page):

    global current_page

    current_page = page

    clear_main_area()

    if page == "chat":
        create_chat_page()

    elif page == "debug":
        create_debug_page()

    elif page == "generate":
        create_generator_page()

    elif page == "run":
        create_runner_page()

    elif page == "projects":
        create_projects_page()

    elif page == "settings":
        create_settings_page()


# =========================================================
# START
# =========================================================

show_page("chat")

window.mainloop()

