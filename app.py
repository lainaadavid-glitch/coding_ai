import customtkinter as ctk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv
import requests
import threading
import os
import json

from pages.editor import EditorPage
from pages.projects import ProjectsPage


# =========================================================
# LOAD PRIVATE SETTINGS
# =========================================================

load_dotenv()

MODEL = os.getenv("MODEL")
URL = os.getenv("URL")

conversation = []


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

        # =================================================
        # MAIN GRID
        # =================================================

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================================
        # SIDEBAR
        # =================================================

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

        # =================================================
        # CONTENT
        # =================================================

        self.content = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        self.content.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================================
        # SIDEBAR
        # =================================================

        self.create_sidebar()

        # =================================================
        # PAGE STORAGE
        # =================================================

        self.pages = {}

        # =================================================
        # CREATE CHAT
        # =================================================

        self.create_chat_page()

        # =================================================
        # CREATE EDITOR
        # =================================================

        self.editor_page = EditorPage(
            self.content,
            self.set_status
        )

        # =================================================
        # CREATE DEBUGGER
        # =================================================

        self.create_debugger_page()

        # =================================================
        # CREATE PROJECTS
        # =================================================

        self.projects_page = ProjectsPage(
            self.content,
            self.editor_page,
            self.set_status
        )

        # =================================================
        # CREATE SETTINGS
        # =================================================

        self.create_settings_page()

        # =================================================
        # SHOW CHAT
        # =================================================

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


    def add_nav_button(
        self,
        text,
        page
    ):

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

    def create_page(
        self,
        name
    ):

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


    def show_page(
        self,
        page
    ):

        # =================================================
        # EDITOR
        # =================================================

        if page == "editor":

            self.editor_page.page.tkraise()

            return

        # =================================================
        # PROJECTS
        # =================================================

        if page == "projects":

            self.projects_page.page.tkraise()

            return

        # =================================================
        # NORMAL PAGES
        # =================================================

        self.pages[page].tkraise()


    # =====================================================
    # CHAT PAGE
    # =====================================================

    def create_chat_page(self):

        page = self.create_page(
            "chat"
        )

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


    # =====================================================
    # ASK AI
    # =====================================================

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

        self.chat_box.see(
            "end"
        )

        self.set_status(
            "🤔 AI is thinking..."
        )

        conversation.append(
            f"User: {question}"
        )

        history = "\n".join(
            conversation
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

{history}

AI:
"""

        threading.Thread(
            target=self.send_to_ollama,
            args=(prompt,),
            daemon=True
        ).start()


    # =====================================================
    # CLEAR CHAT
    # =====================================================

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
    # DEBUGGER PAGE
    # =====================================================

    def create_debugger_page(self):

        page = self.create_page(
            "debugger"
        )

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

        debug_button = ctk.CTkButton(
            page,
            text="🐛 Debug Code",
            command=self.debug_code
        )

        debug_button.grid(
            row=2,
            column=0,
            sticky="w",
            padx=25,
            pady=15
        )


    # =====================================================
    # DEBUG CODE
    # =====================================================

    def debug_code(self):

        code = self.debug_box.get(
            "1.0",
            "end"
        ).strip()

        if not code:

            self.set_status(
                "⚠️ Paste Python code first"
            )

            return

        self.set_status(
            "🔍 Analyzing code..."
        )

        prompt = f"""
You are an expert Python debugging assistant.

Analyze this Python code.

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
    # SETTINGS PAGE
    # =====================================================

    def create_settings_page(self):

        page = self.create_page(
            "settings"
        )

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
            text="AI Model: Loaded privately from .env"
        )

        model_label.pack(
            anchor="w",
            padx=25,
            pady=10
        )


    def change_appearance(
        self,
        choice
    ):

        ctk.set_appearance_mode(
            choice.lower()
        )


    # =====================================================
    # AI CONNECTION
    # =====================================================

    def send_to_ollama(
        self,
        prompt
    ):

        try:

            if not MODEL:

                raise ValueError(
                    "MODEL is missing from .env"
                )

            if not URL:

                raise ValueError(
                    "URL is missing from .env"
                )

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
                    line.decode(
                        "utf-8"
                    )
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
                lambda: self.set_status(
                    "🟢 Ready"
                )
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
                lambda: self.set_status(
                    "🔴 Connection error"
                )
            )

        except requests.exceptions.Timeout:

            self.after(
                0,
                lambda: self.add_ai_text(
                    "\n⏳ AI request timed out.\n"
                )
            )

            self.after(
                0,
                lambda: self.set_status(
                    "⏳ Timeout"
                )
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
                lambda: self.set_status(
                    "🔴 Error"
                )
            )


    # =====================================================
    # ADD AI TEXT
    # =====================================================

    def add_ai_text(
        self,
        text
    ):

        self.chat_box.insert(
            "end",
            text
        )

        self.chat_box.see(
            "end"
        )


    # =====================================================
    # STATUS
    # =====================================================

    def set_status(
        self,
        text
    ):

        self.status_label.configure(
            text=text
        )


# =========================================================
# START APP
# =========================================================

if __name__ == "__main__":

    app = CodingAI()

    app.mainloop()