import customtkinter as ctk
from tkinter import filedialog, messagebox
import os


class ProjectsPage:

    def __init__(self, parent, editor_page, set_status):

        self.parent = parent
        self.editor_page = editor_page
        self.set_status = set_status

        self.project_folder = None

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

        title = ctk.CTkLabel(
            self.page,
            text="📁 Projects",
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
            pady=(20, 10)
        )

        # =================================================
        # TOP BAR
        # =================================================

        top_bar = ctk.CTkFrame(
            self.page,
            fg_color="transparent"
        )

        top_bar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=5
        )

        top_bar.grid_columnconfigure(
            0,
            weight=1
        )

        self.project_label = ctk.CTkLabel(
            top_bar,
            text="No project selected",
            text_color="gray"
        )

        self.project_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        # =================================================
        # BUTTONS
        # =================================================

        button_frame = ctk.CTkFrame(
            top_bar,
            fg_color="transparent"
        )

        button_frame.grid(
            row=0,
            column=1,
            sticky="e"
        )

        ctk.CTkButton(
            button_frame,
            text="📂 Open",
            width=100,
            command=self.open_project
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            width=90,
            command=self.refresh_project
        ).pack(
            side="left",
            padx=4
        )

        ctk.CTkButton(
            button_frame,
            text="➕ New File",
            width=100,
            command=self.new_file
        ).pack(
            side="left",
            padx=4
        )

        # =================================================
        # FILE EXPLORER
        # =================================================

        explorer = ctk.CTkFrame(
            self.page
        )

        explorer.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=25,
            pady=15
        )

        explorer.grid_columnconfigure(
            0,
            weight=1
        )

        explorer.grid_rowconfigure(
            0,
            weight=1
        )

        self.file_list = ctk.CTkScrollableFrame(
            explorer
        )

        self.file_list.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=5,
            pady=5
        )

        # =================================================
        # HELP
        # =================================================

        help_label = ctk.CTkLabel(
            self.page,
            text="💡 Click folders to expand/collapse • Double-click Python files to open them",
            text_color="gray"
        )

        help_label.grid(
            row=3,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 15)
        )

    # =====================================================
    # OPEN PROJECT
    # =====================================================

    def open_project(self):

        folder = filedialog.askdirectory(
            title="Open Python Project"
        )

        if not folder:
            return

        self.project_folder = folder

        self.project_label.configure(
            text=folder
        )

        self.refresh_project()

        self.set_status(
            "📁 Project opened"
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_project(self):

        if not self.project_folder:

            self.set_status(
                "⚠️ Open a project first"
            )

            return

        # Remove previous tree

        for widget in self.file_list.winfo_children():

            widget.destroy()

        self.build_tree(
            self.project_folder,
            self.file_list,
            0
        )

        self.set_status(
            "🔄 Project refreshed"
        )

    # =====================================================
    # BUILD TREE
    # =====================================================

    def build_tree(
        self,
        folder,
        parent,
        level
    ):

        try:

            items = os.listdir(
                folder
            )

        except PermissionError:

            return

        # =================================================
        # SORT
        # FOLDERS FIRST
        # =================================================

        items.sort(
            key=lambda item: (
                not os.path.isdir(
                    os.path.join(
                        folder,
                        item
                    )
                ),
                item.lower()
            )
        )

        for item in items:

            # Hide unnecessary folders/files

            if item in [
                "__pycache__",
                ".git"
            ]:

                continue

            path = os.path.join(
                folder,
                item
            )

            # =================================================
            # FOLDER
            # =================================================

            if os.path.isdir(path):

                self.create_folder(
                    parent,
                    path,
                    item,
                    level
                )

            # =================================================
            # FILE
            # =================================================

            else:

                self.create_file(
                    parent,
                    path,
                    item,
                    level
                )

    # =====================================================
    # CREATE FOLDER
    # =====================================================

    def create_folder(
        self,
        parent,
        folder_path,
        name,
        level
    ):

        # Container for folder + children

        container = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        container.pack(
            fill="x",
            padx=0,
            pady=1
        )

        # =================================================
        # FOLDER BUTTON
        # =================================================

        folder_button = ctk.CTkButton(
            container,
            text=f"{'    ' * level}📁 {name}",
            anchor="w",
            height=32,
            fg_color="transparent",
            hover_color="#343638"
        )

        folder_button.pack(
            fill="x"
        )

        # =================================================
        # CHILDREN FRAME
        # =================================================

        children = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        # Start collapsed

        expanded = [False]

        def toggle_folder():

            if expanded[0]:

                children.pack_forget()

                folder_button.configure(
                    text=f"{'    ' * level}📁 {name}"
                )

                expanded[0] = False

            else:

                children.pack(
                    fill="x"
                )

                folder_button.configure(
                    text=f"{'    ' * level}📂 {name}"
                )

                # Build children only once

                if not children.winfo_children():

                    self.build_tree(
                        folder_path,
                        children,
                        level + 1
                    )

                expanded[0] = True

        folder_button.configure(
            command=toggle_folder
        )

    # =====================================================
    # CREATE FILE
    # =====================================================

    def create_file(
        self,
        parent,
        path,
        name,
        level
    ):

        # Choose icon

        if name.endswith(".py"):

            icon = "🐍"

        elif name.endswith(".json"):

            icon = "📋"

        elif name.endswith(".md"):

            icon = "📝"

        elif name.endswith(".txt"):

            icon = "📄"

        else:

            icon = "📄"

        button = ctk.CTkButton(
            parent,
            text=f"{'    ' * level}{icon} {name}",
            anchor="w",
            height=30,
            fg_color="transparent",
            hover_color="#343638"
        )

        button.pack(
            fill="x",
            padx=0,
            pady=1
        )

        # Double-click opens file

        button.bind(
            "<Double-Button-1>",
            lambda event, p=path: self.open_file(p)
        )

    # =====================================================
    # OPEN FILE
    # =====================================================

    def open_file(
        self,
        path
    ):

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                code = file.read()

            # Put code in editor

            self.editor_page.editor.delete(
                "1.0",
                "end"
            )

            self.editor_page.editor.insert(
                "1.0",
                code
            )

            # Tell editor current file

            self.editor_page.current_file = path

            # Show editor

            self.editor_page.page.tkraise()

            self.set_status(
                f"📂 Opened {os.path.basename(path)}"
            )

        except UnicodeDecodeError:

            messagebox.showerror(
                "Open File Error",
                "This file is not a text file."
            )

        except Exception as error:

            messagebox.showerror(
                "Open File Error",
                str(error)
            )

    # =====================================================
    # NEW FILE
    # =====================================================

    def new_file(self):

        if not self.project_folder:

            messagebox.showwarning(
                "No Project",
                "Open a project first."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Create Python File",
            initialdir=self.project_folder,
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py")
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

            self.refresh_project()

            self.open_file(
                filename
            )

            self.set_status(
                f"📄 Created {os.path.basename(filename)}"
            )

        except Exception as error:

            messagebox.showerror(
                "Create File Error",
                str(error)
            )