
import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import keyword
import re


class EditorPage:

    def __init__(self, parent, set_status):

        self.parent = parent
        self.set_status = set_status

        # File tabs
        self.tabs = {}
        self.active_tab = None
        self.current_file = None

        # Running process
        self.process = None

        self.create_page()

    # =====================================================
    # CREATE PAGE
    # =====================================================

    def create_page(self):

        self.page = ctk.CTkFrame(
            self.parent,
            corner_radius=0
        )

        self.page.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.page.grid_columnconfigure(
            0,
            weight=1
        )

        self.page.grid_rowconfigure(
            2,
            weight=1
        )

        # =================================================
        # TITLE
        # =================================================

        self.title_label = ctk.CTkLabel(
            self.page,
            text="📝 Python Code Editor",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=(15, 5)
        )

        # =================================================
        # TAB BAR
        # =================================================

        self.tab_bar = ctk.CTkScrollableFrame(
            self.page,
            height=45,
            orientation="horizontal"
        )

        self.tab_bar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=5
        )

        # =================================================
        # EDITOR FRAME
        # =================================================

        editor_frame = ctk.CTkFrame(
            self.page
        )

        editor_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=25,
            pady=5
        )

        editor_frame.grid_columnconfigure(
            1,
            weight=1
        )

        editor_frame.grid_rowconfigure(
            0,
            weight=1
        )

        # =================================================
        # LINE NUMBERS
        # =================================================

        self.line_numbers = ctk.CTkTextbox(
            editor_frame,
            width=55,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            ),
            fg_color="#202020",
            text_color="#777777",
            border_width=0
        )

        self.line_numbers.grid(
            row=0,
            column=0,
            sticky="ns"
        )

        self.line_numbers.configure(
            state="disabled"
        )

        # =================================================
        # CODE EDITOR
        # =================================================

        self.editor = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            ),
            wrap="none"
        )

        self.editor.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # =================================================
        # KEYBOARD SHORTCUTS
        # =================================================

        self.editor.bind(
            "<KeyRelease>",
            self.on_text_change
        )

        self.editor.bind(
            "<Control-s>",
            self.shortcut_save
        )

        self.editor.bind(
            "<Control-f>",
            self.open_find
        )

        self.editor.bind(
            "<Control-w>",
            self.shortcut_close_tab
        )

        self.editor.bind(
            "<Tab>",
            self.insert_spaces
        )

        # =================================================
        # BUTTON BAR
        # =================================================

        buttons = ctk.CTkFrame(
            self.page
        )

        buttons.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=25,
            pady=8
        )

        ctk.CTkButton(
            buttons,
            text="📂 Open",
            width=90,
            command=self.open_file
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="💾 Save",
            width=90,
            command=self.save_file
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="💾 Save As",
            width=100,
            command=self.save_as
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="▶️ Run",
            width=90,
            command=self.run_code
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="🛑 Stop",
            width=90,
            fg_color="#c0392b",
            hover_color="#e74c3c",
            command=self.stop_code
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="🔍 Find",
            width=90,
            command=self.open_find
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            buttons,
            text="🧹 Clear",
            width=90,
            command=self.clear_editor
        ).pack(
            side="left",
            padx=4
        )

        # =================================================
        # OUTPUT
        # =================================================

        output_title = ctk.CTkLabel(
            self.page,
            text="▶️ Output",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        )

        output_title.grid(
            row=4,
            column=0,
            sticky="w",
            padx=25,
            pady=(5, 2)
        )

        self.output = ctk.CTkTextbox(
            self.page,
            height=150,
            font=ctk.CTkFont(
                family="Consolas",
                size=13
            )
        )

        self.output.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 15)
        )

        self.update_line_numbers()

    # =====================================================
    # CREATE TAB
    # =====================================================

    def create_tab(self, path, code=""):

        if path in self.tabs:

            self.switch_tab(path)

            return

        self.tabs[path] = {
            "code": code,
            "button": None,
            "close_button": None,
            "frame": None
        }

        tab = ctk.CTkFrame(
            self.tab_bar,
            corner_radius=6
        )

        tab.pack(
            side="left",
            padx=2
        )

        name = os.path.basename(path)

        file_button = ctk.CTkButton(
            tab,
            text=f"📄 {name}",
            width=120,
            height=30,
            fg_color="transparent",
            hover_color="#343638",
            command=lambda p=path: self.switch_tab(p)
        )

        file_button.pack(
            side="left"
        )

        close_button = ctk.CTkButton(
            tab,
            text="×",
            width=28,
            height=30,
            fg_color="transparent",
            hover_color="#c0392b",
            command=lambda p=path: self.close_tab(p)
        )

        close_button.pack(
            side="left"
        )

        self.tabs[path]["button"] = file_button
        self.tabs[path]["close_button"] = close_button
        self.tabs[path]["frame"] = tab

        self.switch_tab(path)

    # =====================================================
    # SWITCH TAB
    # =====================================================

    def switch_tab(self, path):

        if path not in self.tabs:
            return

        if self.active_tab in self.tabs:

            self.tabs[
                self.active_tab
            ]["code"] = self.editor.get(
                "1.0",
                "end-1c"
            )

        self.active_tab = path
        self.current_file = path

        code = self.tabs[path]["code"]

        self.editor.delete(
            "1.0",
            "end"
        )

        self.editor.insert(
            "1.0",
            code
        )

        self.title_label.configure(
            text=f"📝 {os.path.basename(path)}"
        )

        self.update_line_numbers()
        self.highlight_syntax()

        for tab_path, data in self.tabs.items():

            if tab_path == path:

                data["button"].configure(
                    fg_color="#1f6aa5"
                )

            else:

                data["button"].configure(
                    fg_color="transparent"
                )

    # =====================================================
    # CLOSE TAB
    # =====================================================

    def close_tab(self, path):

        if path not in self.tabs:
            return

        if path == self.active_tab:

            self.tabs[path]["code"] = self.editor.get(
                "1.0",
                "end-1c"
            )

        self.tabs[path]["frame"].destroy()

        del self.tabs[path]

        if not self.tabs:

            self.active_tab = None
            self.current_file = None

            self.editor.delete(
                "1.0",
                "end"
            )

            self.title_label.configure(
                text="📝 Python Code Editor"
            )

            self.update_line_numbers()

            return

        remaining = list(
            self.tabs.keys()
        )

        self.switch_tab(
            remaining[-1]
        )

    # =====================================================
    # CTRL + W
    # =====================================================

    def shortcut_close_tab(self, event=None):

        if self.active_tab:

            self.close_tab(
                self.active_tab
            )

        return "break"

    # =====================================================
    # CTRL + S
    # =====================================================

    def shortcut_save(self, event=None):

        self.save_file()

        return "break"

    # =====================================================
    # LOAD FILE
    # =====================================================

    def load_file(self, path):

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                code = file.read()

            self.create_tab(
                path,
                code
            )

            self.set_status(
                f"📂 Opened {os.path.basename(path)}"
            )

        except UnicodeDecodeError:

            messagebox.showerror(
                "Open Error",
                "This file is not a text file."
            )

        except Exception as error:

            messagebox.showerror(
                "Open Error",
                str(error)
            )

    # =====================================================
    # OPEN FILE
    # =====================================================

    def open_file(self):

        path = filedialog.askopenfilename(
            filetypes=[
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if path:

            self.load_file(path)

    # =====================================================
    # SAVE FILE
    # =====================================================

    def save_file(self):

        if not self.current_file:

            return self.save_as()

        try:

            code = self.editor.get(
                "1.0",
                "end-1c"
            )

            with open(
                self.current_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            if self.current_file in self.tabs:

                self.tabs[
                    self.current_file
                ]["code"] = code

            self.set_status(
                f"💾 Saved {os.path.basename(self.current_file)}"
            )

            return True

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )

            return False

    # =====================================================
    # SAVE AS
    # =====================================================

    def save_as(self):

        path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return False

        code = self.editor.get(
            "1.0",
            "end-1c"
        )

        self.create_tab(
            path,
            code
        )

        return self.save_file()

    # =====================================================
    # TEXT CHANGE
    # =====================================================

    def on_text_change(self, event=None):

        if self.active_tab:

            self.tabs[
                self.active_tab
            ]["code"] = self.editor.get(
                "1.0",
                "end-1c"
            )

        self.update_line_numbers()
        self.highlight_syntax()

    # =====================================================
    # LINE NUMBERS
    # =====================================================

    def update_line_numbers(self):

        try:

            code = self.editor.get(
                "1.0",
                "end-1c"
            )

            count = code.count("\n") + 1

            numbers = "\n".join(
                str(i)
                for i in range(
                    1,
                    count + 1
                )
            )

            self.line_numbers.configure(
                state="normal"
            )

            self.line_numbers.delete(
                "1.0",
                "end"
            )

            self.line_numbers.insert(
                "1.0",
                numbers
            )

            self.line_numbers.configure(
                state="disabled"
            )

        except Exception:
            pass

    # =====================================================
    # SYNTAX HIGHLIGHTING
    # =====================================================

    def highlight_syntax(self):

        try:

            self.editor.tag_config(
                "keyword",
                foreground="#ff79c6"
            )

            self.editor.tag_config(
                "string",
                foreground="#f1fa8c"
            )

            self.editor.tag_config(
                "comment",
                foreground="#6272a4"
            )

            self.editor.tag_config(
                "number",
                foreground="#bd93f9"
            )

            self.editor.tag_config(
                "function",
                foreground="#50fa7b"
            )

            for tag in [
                "keyword",
                "string",
                "comment",
                "number",
                "function"
            ]:

                self.editor.tag_remove(
                    tag,
                    "1.0",
                    "end"
                )

            for word in keyword.kwlist:

                self.apply_pattern(
                    r"\b" + re.escape(word) + r"\b",
                    "keyword"
                )

            self.apply_pattern(
                r'(\".*?\"|\'.*?\')',
                "string"
            )

            self.apply_pattern(
                r"#.*",
                "comment"
            )

            self.apply_pattern(
                r"\b\d+(\.\d+)?\b",
                "number"
            )

            self.apply_pattern(
                r"\b[a-zA-Z_][a-zA-Z0-9_]*(?=\()",
                "function"
            )

        except Exception:
            pass

    # =====================================================
    # APPLY PATTERN
    # =====================================================

    def apply_pattern(self, pattern, tag):

        code = self.editor.get(
            "1.0",
            "end-1c"
        )

        for match in re.finditer(
            pattern,
            code
        ):

            start = (
                "1.0 + "
                + str(match.start())
                + " chars"
            )

            end = (
                "1.0 + "
                + str(match.end())
                + " chars"
            )

            self.editor.tag_add(
                tag,
                start,
                end
            )

    # =====================================================
    # RUN CODE
    # =====================================================

    def run_code(self):

        code = self.editor.get(
            "1.0",
            "end-1c"
        ).strip()

        if not code:

            self.set_status(
                "⚠️ No code to run"
            )

            return

        self.output.delete(
            "1.0",
            "end"
        )

        self.output.insert(
            "1.0",
            "▶️ Running...\n\n"
        )

        self.set_status(
            "▶️ Running code..."
        )

        threading.Thread(
            target=self.execute_code,
            args=(code,),
            daemon=True
        ).start()

    # =====================================================
    # EXECUTE CODE
    # =====================================================

    def execute_code(self, code):

        try:

            self.process = subprocess.Popen(
                [
                    "python",
                    "-c",
                    code
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = self.process.communicate()

            output = stdout

            if stderr:

                output += (
                    "\n❌ ERROR\n"
                    + stderr
                )

            if not output:

                output = (
                    "✅ Code finished successfully."
                )

            self.parent.after(
                0,
                lambda: self.show_output(output)
            )

        except Exception as error:

            self.parent.after(
                0,
                lambda: self.show_output(
                    f"❌ Error: {error}"
                )
            )

        finally:

            self.process = None

    # =====================================================
    # SHOW OUTPUT
    # =====================================================

    def show_output(self, text):

        self.output.delete(
            "1.0",
            "end"
        )

        self.output.insert(
            "1.0",
            text
        )

        self.set_status(
            "🟢 Code finished"
        )

    # =====================================================
    # STOP CODE
    # =====================================================

    def stop_code(self):

        if self.process is None:

            self.set_status(
                "ℹ️ Nothing is running"
            )

            return

        try:

            self.process.kill()

            self.process = None

            self.output.insert(
                "end",
                "\n\n🛑 Program stopped."
            )

            self.set_status(
                "🛑 Program stopped"
            )

        except Exception as error:

            self.set_status(
                f"❌ Stop error: {error}"
            )

    # =====================================================
    # FIND
    # =====================================================

    def open_find(self):

        window = ctk.CTkToplevel(
            self.page
        )

        window.title(
            "🔍 Find"
        )

        window.geometry(
            "400x150"
        )

        window.transient(
            self.page
        )

        ctk.CTkLabel(
            window,
            text="Find text:"
        ).pack(
            pady=(20, 5)
        )

        entry = ctk.CTkEntry(
            window,
            width=300
        )

        entry.pack(
            pady=5
        )

        entry.focus()

        def find_text():

            search = entry.get()

            if not search:
                return

            self.editor.tag_remove(
                "search",
                "1.0",
                "end"
            )

            self.editor.tag_config(
                "search",
                background="#555555"
            )

            start = "1.0"

            while True:

                position = self.editor.search(
                    search,
                    start,
                    stopindex="end"
                )

                if not position:
                    break

                end = (
                    position
                    + "+"
                    + str(len(search))
                    + "c"
                )

                self.editor.tag_add(
                    "search",
                    position,
                    end
                )

                start = end

        ctk.CTkButton(
            window,
            text="🔍 Find",
            command=find_text
        ).pack(
            pady=10
        )

    # =====================================================
    # INSERT SPACES
    # =====================================================

    def insert_spaces(self, event=None):

        self.editor.insert(
            "insert",
            "    "
        )

        return "break"

    # =====================================================
    # CLEAR EDITOR
    # =====================================================

    def clear_editor(self):

        answer = messagebox.askyesno(
            "Clear Editor",
            "Clear the current file?"
        )

        if not answer:
            return

        self.editor.delete(
            "1.0",
            "end"
        )

        if self.active_tab:

            self.tabs[
                self.active_tab
            ]["code"] = ""

        self.update_line_numbers()

        self.output.delete(
            "1.0",
            "end"
        )

        self.set_status(
            "🧹 Editor cleared"
        )

