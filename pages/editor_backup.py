import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os


class EditorPage:

    def __init__(self, parent, set_status):

        self.parent = parent
        self.set_status = set_status

        self.current_file = None
        self.process = None

        self.create_page()


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
            1,
            weight=1
        )

        # ===============================================
        # TITLE
        # ===============================================

        title = ctk.CTkLabel(
            self.page,
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

        # ===============================================
        # EDITOR
        # ===============================================

        self.editor = ctk.CTkTextbox(
            self.page,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            ),
            undo=True
        )

        self.editor.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=10
        )

        # ===============================================
        # BUTTON BAR
        # ===============================================

        buttons = ctk.CTkFrame(
            self.page
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

        self.stop_button = ctk.CTkButton(
            buttons,
            text="🛑 Stop",
            fg_color="#c0392b",
            hover_color="#e74c3c",
            command=self.stop_code,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            buttons,
            text="🧹 Clear",
            command=self.clear_editor
        ).pack(
            side="left",
            padx=5
        )


    # ===============================================
    # OPEN FILE
    # ===============================================

    def open_file(self):

        path = filedialog.askopenfilename(
            title="Open Python File",
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

            self.current_file = path

            self.set_status(
                f"📂 Opened {os.path.basename(path)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Open Error",
                str(error)
            )


    # ===============================================
    # SAVE FILE
    # ===============================================

    def save_file(self):

        if self.current_file is None:

            self.current_file = filedialog.asksaveasfilename(
                title="Save Python File",
                defaultextension=".py",
                filetypes=[
                    ("Python files", "*.py")
                ]
            )

        if not self.current_file:
            return

        code = self.editor.get(
            "1.0",
            "end"
        )

        try:

            with open(
                self.current_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            self.set_status(
                f"💾 Saved {os.path.basename(self.current_file)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                str(error)
            )


    # ===============================================
    # RUN CODE
    # ===============================================

    def run_code(self):

        code = self.editor.get(
            "1.0",
            "end"
        ).strip()

        if not code:
            self.set_status(
                "⚠️ Editor is empty"
            )
            return

        self.set_status(
            "▶️ Running Python..."
        )

        self.stop_button.configure(
            state="normal"
        )

        threading.Thread(
            target=self.execute_code,
            args=(code,),
            daemon=True
        ).start()


    def execute_code(self, code):

        try:

            self.process = subprocess.Popen(
                ["python", "-c", code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = self.process.communicate()

            output = stdout

            if stderr:

                output += (
                    "\n❌ Error:\n"
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

            self.parent.after(
                0,
                lambda: self.stop_button.configure(
                    state="disabled"
                )
            )


    # ===============================================
    # STOP CODE
    # ===============================================

    def stop_code(self):

        if self.process:

            try:
                self.process.kill()

                self.set_status(
                    "🛑 Code stopped"
                )

            except Exception:
                pass

            self.process = None

            self.stop_button.configure(
                state="disabled"
            )


    # ===============================================
    # SHOW OUTPUT
    # ===============================================

    def show_output(self, output):

        output_window = ctk.CTkToplevel(
            self.page
        )

        output_window.title(
            "▶️ Program Output"
        )

        output_window.geometry(
            "700x450"
        )

        output_box = ctk.CTkTextbox(
            output_window,
            font=ctk.CTkFont(
                family="Consolas",
                size=13
            )
        )

        output_box.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        output_box.insert(
            "1.0",
            output
        )

        self.set_status(
            "🟢 Code finished"
        )


    # ===============================================
    # CLEAR
    # ===============================================

    def clear_editor(self):

        self.editor.delete(
            "1.0",
            "end"
        )

        self.current_file = None

        self.set_status(
            "🧹 Editor cleared"
        )