
import customtkinter as ctk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv
import requests
import threading
import subprocess
import os
import json
import keyword
import re

# =========================================================
# LOAD PRIVATE SETTINGS
# =========================================================

load_dotenv()

MODEL = os.getenv("MODEL")
URL = os.getenv("URL")

conversation = []

current_file = None
project_folder = None

# =========================================================
# APP SETTINGS
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# MAIN APP
# =========================================================

class CodingAI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("🤖 Coding AI")
        self.geometry("1350x850")
        self.minsize(1000, 650)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        self.sidebar.grid_propagate(False)

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0
        )
        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )
        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.create_sidebar()

        self.pages = {}

        self.create_chat_page()
        self.create_editor_page()
        self.create_debugger_page()
        self.create_projects_page()
        self.create_settings_page()

        self.show_page("chat")


    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(self):

        title = ctk.CTkLabel(
            self.sidebar,
            text="🤖 CODING AI",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )
        title.pack(
            pady=(30, 35)
        )

        self.add_nav_button(
            "💬  Chat",
            "chat"
        )

        self.add_nav_button(
            "📝  Code Editor",
            "editor"
        )

        self.add_nav_button(
            "🐛  Debugger",
            "debugger"
        )

        self.add_nav_button(
            "📁  Projects",
            "projects"
        )

        self.add_nav_button(
            "⚙️  Settings",
            "settings"
        )

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="🟢 Ready",
            text_color="lightgreen"
        )

        self.status_label.pack(
            side="bottom",
            pady=20
        )


    def add_nav_button(self, text, page):

        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=45,
            anchor="w",
            command=lambda: self.show_page(page)
        )

        button.pack(
            fill="x",
            padx=15,
            pady=5
        )


    # =====================================================
    # PAGE SYSTEM
    # =====================================================

    def create_page(self, name):

        frame = ctk.CTkFrame(
            self.content,
            corner_radius=0
        )

        frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        frame.grid_rowconfigure(
            1,
            weight=1
        )

        self.pages[name] = frame

        return frame


    def show_page(self, page):

        self.pages[page].tkraise()


    # =====================================================
    # CHAT PAGE
    # =====================================================

    def create_chat_page(self):

        page = self.create_page("chat")

        title = ctk.CTkLabel(
            page,
            text="💬 Chat with Coding AI",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=20
        )

        self.chat_box = ctk.CTkTextbox(
            page,
            font=ctk.CTkFont(
                size=14
            )
        )

        self.chat_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=10
        )

        self.chat_box.insert(
            "end",
            "🤖 Coding AI\n\n"
            "Ask me anything about programming.\n"
        )

        bottom = ctk.CTkFrame(
            page
        )

        bottom.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=15
        )

        bottom.grid_columnconfigure(
            0,
            weight=1
        )

        self.chat_entry = ctk.CTkEntry(
            bottom,
            placeholder_text="Ask Coding AI..."
        )

        self.chat_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10)
        )

        send = ctk.CTkButton(
            bottom,
            text="💬 Send",
            width=100,
            command=self.ask_ai
        )

        send.grid(
            row=0,
            column=1
        )

        clear = ctk.CTkButton(
            bottom,
            text="🧹 Clear",
            width=100,
            command=self.clear_chat
        )

        clear.grid(
            row=0,
            column=2,
            padx=(10, 0)
        )

        self.chat_entry.bind(
            "<Return>",
            lambda event: self.ask_ai()
        )


    def ask_ai(self):

        question = self.chat_entry.get().strip()

        if not question:
            return

        self.chat_entry.delete(
            0,
            "end"
        )

        self.chat_box.insert(
            "end",
            f"\n\nYou: {question}\n\nAI: "
        )

        self.chat_box.see("end")

        self.set_status(
            "🤔 AI is thinking..."
        )

        conversation.append(
            f"User: {question}"
        )

        prompt = f"""
You are Coding AI, a friendly programming tutor.

Rules:
- Explain programming simply.
- Assume the user is a beginner.
- Give examples when useful.
- Explain code you provide.
- Help find and fix errors.
- Teach instead of only giving answers.

Conversation:

{"".join(conversation)}

AI:
"""

        threading.Thread(
            target=self.send_to_ollama,
            args=(prompt,),
            daemon=True
        ).start()


    def clear_chat(self):

        conversation.clear()

        self.chat_box.delete(
            "1.0",
            "end"
        )

        self.chat_box.insert(
            "end",
            "🤖 Coding AI\n\n"
        )


    # =====================================================
    # EDITOR PAGE
    # =====================================================

    def create_editor_page(self):

        page = self.create_page("editor")

        title = ctk.CTkLabel(
            page,
            text="📝 Python Code Editor",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=20
        )

        self.editor = ctk.CTkTextbox(
            page,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            )
        )

        self.editor.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=10
        )

        buttons = ctk.CTkFrame(
            page
        )

        buttons.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=15
        )

        ctk.CTkButton(
            buttons,
            text="📂 Open",
            command=self.open_file
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="💾 Save",
            command=self.save_file
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="▶️ Run",
            command=self.run_code
        ).pack(
            side="left",
            padx=5
        )


    # =====================================================
    # DEBUGGER PAGE
    # =====================================================

    def create_debugger_page(self):

        page = self.create_page("debugger")

        title = ctk.CTkLabel(
            page,
            text="🐛 Python Debugger",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=20
        )

        self.debug_box = ctk.CTkTextbox(
            page,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            )
        )

        self.debug_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=10
        )

        ctk.CTkButton(
            page,
            text="🐛 Debug Code",
            command=self.debug_code
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=25,
            pady=15
        )


    def debug_code(self):

        code = self.debug_box.get(
            "1.0",
            "end"
        ).strip()

        if not code:
            return

        self.set_status(
            "🔍 Analyzing code..."
        )

        prompt = f"""
You are an expert Python debugging assistant.

Analyze this code.

Find:
1. Syntax errors.
2. Logical errors.
3. Explain every problem simply.
4. Provide corrected code.
5. Explain your changes.

Code:

{code}
"""

        threading.Thread(
            target=self.send_to_ollama,
            args=(prompt,),
            daemon=True
        ).start()


    # =====================================================
    # PROJECTS PAGE
    # =====================================================

    def create_projects_page(self):

        page = self.create_page("projects")

        title = ctk.CTkLabel(
            page,
            text="📁 Projects",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=25,
            pady=20
        )

        self.project_label = ctk.CTkLabel(
            page,
            text="No project selected"
        )

        self.project_label.pack(
            anchor="w",
            padx=25,
            pady=10
        )

        ctk.CTkButton(
            page,
            text="📂 Open Project",
            command=self.open_project
        ).pack(
            anchor="w",
            padx=25,
            pady=10
        )


    def open_project(self):

        global project_folder

        folder = filedialog.askdirectory(
            title="Open Python Project"
        )

        if not folder:
            return

        project_folder = folder

        self.project_label.configure(
            text=folder
        )

        self.set_status(
            "📁 Project opened"
        )


    # =====================================================
    # SETTINGS PAGE
    # =====================================================

    def create_settings_page(self):

        page = self.create_page("settings")

        title = ctk.CTkLabel(
            page,
            text="⚙️ Settings",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        title.pack(
            anchor="w",
            padx=25,
            pady=20
        )

        appearance = ctk.CTkOptionMenu(
            page,
            values=[
                "Dark",
                "Light",
                "System"
            ],
            command=self.change_appearance
        )

        appearance.set(
            "Dark"
        )

        appearance.pack(
            anchor="w",
            padx=25,
            pady=15
        )

        model_label = ctk.CTkLabel(
            page,
            text="AI Model: Loaded from .env"
        )

        model_label.pack(
            anchor="w",
            padx=25,
            pady=10
        )


    def change_appearance(self, choice):

        ctk.set_appearance_mode(
            choice.lower()
        )


    # =====================================================
    # OLLAMA
    # =====================================================

    def send_to_ollama(self, prompt):

        try:

            response = requests.post(
                URL,
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True,
                timeout=300
            )

            response.raise_for_status()

            full_answer = ""

            for line in response.iter_lines():

                if not line:
                    continue

                result = json.loads(
                    line.decode()
                )

                text = result.get(
                    "response",
                    ""
                )

                full_answer += text

                self.after(
                    0,
                    lambda t=text: self.add_ai_text(t)
                )

            conversation.append(
                f"AI: {full_answer}"
            )

            self.after(
                0,
                lambda: self.set_status("🟢 Ready")
            )

        except requests.exceptions.ConnectionError:

            self.after(
                0,
                lambda: self.add_ai_text(
                    "\n❌ Cannot connect to AI server.\n"
                )
            )

            self.after(
                0,
                lambda: self.set_status("🔴 Connection error")
            )

        except Exception as error:

            self.after(
                0,
                lambda: self.add_ai_text(
                    f"\n❌ Error: {error}\n"
                )
            )

            self.after(
                0,
                lambda: self.set_status("🔴 Error")
            )


    def add_ai_text(self, text):

        self.chat_box.insert(
            "end",
            text
        )

        self.chat_box.see(
            "end"
        )


    # =====================================================
    # FILE FUNCTIONS
    # =====================================================

    def open_file(self):

        global current_file

        path = filedialog.askopenfilename(
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                code = file.read()

            self.editor.delete(
                "1.0",
                "end"
            )

            self.editor.insert(
                "1.0",
                code
            )

            current_file = path

            self.set_status(
                f"📂 Opened {os.path.basename(path)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Open Error",
                str(error)
            )


    def save_file(self):

        global current_file

        if current_file is None:

            current_file = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[
                    ("Python files", "*.py")
                ]
            )

        if not current_file:
            return

        code = self.editor.get(
            "1.0",
            "end"
        )

        try:

            with open(
                current_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            self.set_status(
                f"💾 Saved {os.path.basename(current_file)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )


    # =====================================================
    # RUN CODE
    # =====================================================

    def run_code(self):

        code = self.editor.get(
            "1.0",
            "end"
        ).strip()

        if not code:
            return

        self.set_status(
            "▶️ Running..."
        )

        threading.Thread(
            target=self.execute_code,
            args=(code,),
            daemon=True
        ).start()


    def execute_code(self, code):

        try:

            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout

            if result.stderr:
                output += "\n❌ Error:\n"
                output += result.stderr

            if not output:
                output = "✅ Code finished successfully."

            self.after(
                0,
                lambda: self.chat_box.insert(
                    "end",
                    f"\n\n▶️ RESULT\n{output}\n"
                )
            )

            self.after(
                0,
                lambda: self.set_status(
                    "🟢 Code finished"
                )
            )

        except subprocess.TimeoutExpired:

            self.after(
                0,
                lambda: self.set_status(
                    "⏳ Code timed out"
                )
            )


    # =====================================================
    # STATUS
    # =====================================================

    def set_status(self, text):

        self.status_label.configure(
            text=text
        )


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    app = CodingAI()

    app.mainloop()

