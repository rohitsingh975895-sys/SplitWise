import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

from database import DatabaseManager
from calculations import calculate_split
from settlement import calculate_settlements
from reports import export_expenses_csv, create_text_report


class TripSplitApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title(
            "Splitwise - Smart Group Trip Expense & Settlement System"
        )

        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.db = DatabaseManager()

        self.current_trip_id = None
        self.current_trip = None

        self.configure(bg="#f4f6f8")

        self.setup_style()
        self.show_trip_selection()

    # ==========================================================
    # STYLE
    # ==========================================================

    def setup_style(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Title.TLabel",
            font=("Arial", 22, "bold"),
            background="#ffffff"
        )

        style.configure(
            "Heading.TLabel",
            font=("Arial", 16, "bold"),
            background="#ffffff"
        )

        style.configure(
            "Normal.TLabel",
            font=("Arial", 10),
            background="#ffffff"
        )

        style.configure(
            "Primary.TButton",
            font=("Arial", 10, "bold"),
            padding=8
        )

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 10)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold")
        )

    def clear_window(self):

        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================================
    # TRIP SELECTION
    # ==========================================================

    def show_trip_selection(self):

        self.clear_window()

        frame = tk.Frame(
            self,
            bg="#ffffff",
            padx=40,
            pady=40
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=50
        )

        tk.Label(
            frame,
            text="Splitwise",
            font=("Arial", 30, "bold"),
            bg="#ffffff",
            fg="#222222"
        ).pack(pady=(40, 5))

        tk.Label(
            frame,
            text="Smart Group Trip Expense & Settlement System",
            font=("Arial", 13),
            bg="#ffffff",
            fg="#666666"
        ).pack(pady=(0, 35))

        button_frame = tk.Frame(
            frame,
            bg="#ffffff"
        )

        button_frame.pack()

        ttk.Button(
            button_frame,
            text="Create New Trip",
            style="Primary.TButton",
            command=self.create_trip_window
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )

        ttk.Button(
            button_frame,
            text="Open Existing Trip",
            style="Primary.TButton",
            command=self.open_trip_window
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )

        ttk.Button(
            button_frame,
            text="Exit",
            command=self.destroy
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=10
        )

    # ==========================================================
    # CREATE TRIP
    # ==========================================================

    def create_trip_window(self):

        window = tk.Toplevel(self)

        window.title("Create New Trip")
        window.geometry("500x450")
        window.transient(self)
        window.grab_set()

        frame = ttk.Frame(window, padding=30)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Create New Trip",
            style="Heading.TLabel"
        ).pack(pady=(10, 25))

        ttk.Label(
            frame,
            text="Trip Name:"
        ).pack(anchor="w")

        name_entry = ttk.Entry(frame, width=45)
        name_entry.pack(pady=(5, 15))

        ttk.Label(
            frame,
            text="Start Date (DD/MM/YYYY):"
        ).pack(anchor="w")

        start_entry = ttk.Entry(frame, width=45)
        start_entry.pack(pady=(5, 15))

        ttk.Label(
            frame,
            text="End Date (DD/MM/YYYY):"
        ).pack(anchor="w")

        end_entry = ttk.Entry(frame, width=45)
        end_entry.pack(pady=(5, 15))

        ttk.Label(
            frame,
            text="Currency:"
        ).pack(anchor="w")

        currency_var = tk.StringVar(value="INR")

        currency_combo = ttk.Combobox(
            frame,
            textvariable=currency_var,
            values=["INR", "USD", "EUR", "GBP"],
            state="readonly",
            width=42
        )

        currency_combo.pack(pady=(5, 20))

        def save_trip():

            name = name_entry.get().strip()
            start = start_entry.get().strip()
            end = end_entry.get().strip()
            currency = currency_var.get()

            if not name:
                messagebox.showerror(
                    "Error",
                    "Trip name cannot be empty.",
                    parent=window
                )
                return

            if start:
                try:
                    datetime.strptime(
                        start,
                        "%d/%m/%Y"
                    )
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        "Invalid start date.",
                        parent=window
                    )
                    return

            if end:
                try:
                    datetime.strptime(
                        end,
                        "%d/%m/%Y"
                    )
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        "Invalid end date.",
                        parent=window
                    )
                    return

            if start and end:
                start_date = datetime.strptime(
                    start,
                    "%d/%m/%Y"
                )

                end_date = datetime.strptime(
                    end,
                    "%d/%m/%Y"
                )

                if end_date < start_date:
                    messagebox.showerror(
                        "Error",
                        "End date cannot be before start date.",
                        parent=window
                    )
                    return

            trip_id = self.db.add_trip(
                name,
                start,
                end,
                currency
            )

            window.destroy()

            self.open_trip(
                trip_id
            )

        ttk.Button(
            frame,
            text="Create Trip",
            style="Primary.TButton",
            command=save_trip
        ).pack(pady=10)

    # ==========================================================
    # OPEN TRIP
    # ==========================================================

    def open_trip_window(self):

        trips = self.db.get_trips()

        if not trips:
            messagebox.showinfo(
                "No Trips",
                "No trips have been created yet."
            )
            return

        window = tk.Toplevel(self)

        window.title("Open Trip")
        window.geometry("650x450")
        window.transient(self)
        window.grab_set()

        frame = ttk.Frame(
            window,
            padding=20
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Select Trip",
            style="Heading.TLabel"
        ).pack(pady=(5, 20))

        tree = ttk.Treeview(
            frame,
            columns=(
                "id",
                "name",
                "start",
                "end",
                "currency"
            ),
            show="headings"
        )

        tree.heading("id", text="ID")
        tree.heading("name", text="Trip Name")
        tree.heading("start", text="Start")
        tree.heading("end", text="End")
        tree.heading("currency", text="Currency")

        tree.column("id", width=50)
        tree.column("name", width=200)
        tree.column("start", width=100)
        tree.column("end", width=100)
        tree.column("currency", width=80)

        tree.pack(
            fill="both",
            expand=True
        )

        for trip in trips:
            tree.insert(
                "",
                "end",
                values=trip
            )

        def select_trip():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Trip",
                    "Please select a trip.",
                    parent=window
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            trip_id = int(values[0])

            window.destroy()

            self.open_trip(
                trip_id
            )

        ttk.Button(
            frame,
            text="Open Selected Trip",
            command=select_trip
        ).pack(pady=15)

    def open_trip(self, trip_id):

        trip = self.db.get_trip(trip_id)

        if not trip:
            messagebox.showerror(
                "Error",
                "Trip could not be found."
            )
            return

        self.current_trip_id = trip_id
        self.current_trip = trip

        self.show_dashboard()

    # ==========================================================
    # MAIN LAYOUT
    # ==========================================================

    def create_main_layout(self, page_title):

        self.clear_window()

        sidebar = tk.Frame(
            self,
            bg="#222831",
            width=220
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="TRIPSPLIT",
            font=("Arial", 22, "bold"),
            bg="#222831",
            fg="white"
        ).pack(pady=(30, 5))

        tk.Label(
            sidebar,
            text=self.current_trip[1],
            font=("Arial", 10),
            bg="#222831",
            fg="#cccccc",
            wraplength=180
        ).pack(pady=(0, 25))

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Members", self.show_members),
            ("Expenses", self.show_expenses),
            ("Balances", self.show_balances),
            ("Settlements", self.show_settlements),
            ("Analytics", self.show_analytics),
            ("Reports", self.show_reports)
        ]

        for text, command in buttons:

            tk.Button(
                sidebar,
                text=text,
                command=command,
                font=("Arial", 10),
                bg="#222831",
                fg="white",
                activebackground="#393e46",
                activeforeground="white",
                relief="flat",
                anchor="w",
                padx=25,
                pady=10,
                cursor="hand2"
            ).pack(
                fill="x"
            )

        tk.Button(
            sidebar,
            text="Switch Trip",
            command=self.show_trip_selection,
            font=("Arial", 10),
            bg="#222831",
            fg="#dddddd",
            activebackground="#393e46",
            relief="flat",
            anchor="w",
            padx=25,
            pady=10
        ).pack(
            side="bottom",
            fill="x",
            pady=(0, 15)
        )

        content = tk.Frame(
            self,
            bg="#f4f6f8"
        )

        content.pack(
            side="left",
            fill="both",
            expand=True
        )

        header = tk.Frame(
            content,
            bg="#ffffff",
            height=70
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        tk.Label(
            header,
            text=page_title,
            font=("Arial", 20, "bold"),
            bg="#ffffff",
            fg="#222222"
        ).pack(
            side="left",
            padx=25
        )

        body = tk.Frame(
            content,
            bg="#f4f6f8"
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        return body

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def show_dashboard(self):

        body = self.create_main_layout(
            "Dashboard"
        )

        total = self.db.get_total_expenses(
            self.current_trip_id
        )

        members = self.db.get_members(
            self.current_trip_id
        )

        expenses = self.db.get_expenses(
            self.current_trip_id
        )

        balances = self.db.get_member_balances(
            self.current_trip_id
        )

        cards = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        cards.pack(
            fill="x"
        )

        self.create_card(
            cards,
            "Total Expenses",
            f"{self.current_trip[4]} {total:,.2f}",
            0
        )

        self.create_card(
            cards,
            "Members",
            str(len(members)),
            1
        )

        self.create_card(
            cards,
            "Expenses",
            str(len(expenses)),
            2
        )

        current_member_balance = 0

        if balances:
            current_member_balance = list(
                balances.values()
            )[0]["balance"]

        self.create_card(
            cards,
            "Sample Balance",
            f"{self.current_trip[4]} {current_member_balance:,.2f}",
            3
        )

        recent_frame = tk.LabelFrame(
            body,
            text="Recent Expenses",
            font=("Arial", 11, "bold"),
            bg="#ffffff",
            padx=10,
            pady=10
        )

        recent_frame.pack(
            fill="both",
            expand=True,
            pady=20
        )

        tree = ttk.Treeview(
            recent_frame,
            columns=(
                "date",
                "description",
                "category",
                "paid",
                "amount"
            ),
            show="headings"
        )

        headings = {
            "date": "Date",
            "description": "Description",
            "category": "Category",
            "paid": "Paid By",
            "amount": "Amount"
        }

        for column, heading in headings.items():

            tree.heading(
                column,
                text=heading
            )

        tree.column(
            "date",
            width=100
        )

        tree.column(
            "description",
            width=200
        )

        tree.column(
            "category",
            width=150
        )

        tree.column(
            "paid",
            width=150
        )

        tree.column(
            "amount",
            width=120
        )

        tree.pack(
            fill="both",
            expand=True
        )

        for expense in expenses[:10]:

            tree.insert(
                "",
                "end",
                values=(
                    expense[1],
                    expense[2],
                    expense[3],
                    expense[4],
                    f"{self.current_trip[4]} {expense[5]:.2f}"
                )
            )

    def create_card(
        self,
        parent,
        title,
        value,
        column
    ):

        card = tk.Frame(
            parent,
            bg="#ffffff",
            padx=20,
            pady=15
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=7
        )

        parent.grid_columnconfigure(
            column,
            weight=1
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 10),
            bg="#ffffff",
            fg="#777777"
        ).pack(
            anchor="w"
        )

        tk.Label(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            bg="#ffffff",
            fg="#222222"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

    # ==========================================================
    # MEMBERS
    # ==========================================================

    def show_members(self):

        body = self.create_main_layout(
            "Members"
        )

        top = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Button(
            top,
            text="+ Add Member",
            command=self.add_member_window
        ).pack(
            side="left"
        )

        tree = ttk.Treeview(
            body,
            columns=(
                "id",
                "name",
                "email"
            ),
            show="headings"
        )

        tree.heading(
            "id",
            text="ID"
        )

        tree.heading(
            "name",
            text="Name"
        )

        tree.heading(
            "email",
            text="Email"
        )

        tree.column(
            "id",
            width=60
        )

        tree.column(
            "name",
            width=250
        )

        tree.column(
            "email",
            width=300
        )

        tree.pack(
            fill="both",
            expand=True
        )

        def refresh():

            for item in tree.get_children():
                tree.delete(item)

            for index, member in enumerate(self.db.get_members(self.current_trip_id),start=1):
                tree.insert(
                  "",
                  "end",
                  values=(
                    index,
                    member[1],
                    member[2]
                  )
                 )
        refresh()

        def edit_member():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Member",
                    "Please select a member."
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            self.member_edit_window(
                int(values[0]),
                values[1],
                values[2],
                refresh
            )

        def delete_member():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Member",
                    "Please select a member."
                )
                return

            member_id = int(
                tree.item(
                    selected[0],
                    "values"
                )[0]
            )

            if not messagebox.askyesno(
                "Confirm",
                "Delete this member?"
            ):
                return

            try:
                self.db.delete_member(
                    member_id
                )

                refresh()

            except ValueError as error:

                messagebox.showerror(
                    "Cannot Delete",
                    str(error)
                )

        buttons = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            buttons,
            text="Edit Selected",
            command=edit_member
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ttk.Button(
            buttons,
            text="Delete Selected",
            command=delete_member
        ).pack(
            side="left"
        )

    def add_member_window(self):

        window = tk.Toplevel(self)

        window.title("Add Member")
        window.geometry("450x300")

        frame = ttk.Frame(
            window,
            padding=25
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Member Name:"
        ).pack(
            anchor="w"
        )

        name_entry = ttk.Entry(
            frame,
            width=45
        )

        name_entry.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Email (optional):"
        ).pack(
            anchor="w"
        )

        email_entry = ttk.Entry(
            frame,
            width=45
        )

        email_entry.pack(
            pady=(5, 20)
        )

        def save():

            name = name_entry.get().strip()
            email = email_entry.get().strip()

            if not name:
                messagebox.showerror(
                    "Error",
                    "Member name cannot be empty.",
                    parent=window
                )
                return

            existing = self.db.get_members(
                self.current_trip_id
            )

            if any(
                member[1].lower() == name.lower()
                for member in existing
            ):
                messagebox.showerror(
                    "Error",
                    "A member with this name already exists.",
                    parent=window
                )
                return

            self.db.add_member(
                self.current_trip_id,
                name,
                email
            )

            window.destroy()
            self.show_members()

        ttk.Button(
            frame,
            text="Add Member",
            command=save
        ).pack()

    def member_edit_window(
        self,
        member_id,
        name,
        email,
        refresh
    ):

        window = tk.Toplevel(self)

        window.title("Edit Member")
        window.geometry("450x300")

        frame = ttk.Frame(
            window,
            padding=25
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text="Member Name:"
        ).pack(
            anchor="w"
        )

        name_entry = ttk.Entry(
            frame,
            width=45
        )

        name_entry.insert(
            0,
            name
        )

        name_entry.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Email:"
        ).pack(
            anchor="w"
        )

        email_entry = ttk.Entry(
            frame,
            width=45
        )

        email_entry.insert(
            0,
            email
        )

        email_entry.pack(
            pady=(5, 20)
        )

        def save():

            new_name = name_entry.get().strip()
            new_email = email_entry.get().strip()

            if not new_name:
                messagebox.showerror(
                    "Error",
                    "Name cannot be empty.",
                    parent=window
                )
                return

            self.db.update_member(
                member_id,
                new_name,
                new_email
            )

            window.destroy()
            refresh()

        ttk.Button(
            frame,
            text="Save Changes",
            command=save
        ).pack()

    # ==========================================================
    # EXPENSES
    # ==========================================================

    def show_expenses(self):

        body = self.create_main_layout(
            "Expenses"
        )

        top = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        top.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Button(
            top,
            text="+ Add Expense",
            command=self.add_expense_window
        ).pack(
            side="left"
        )

        search_var = tk.StringVar()

        ttk.Label(
            top,
            text="Search:"
        ).pack(
            side="left",
            padx=(30, 5)
        )

        search_entry = ttk.Entry(
            top,
            textvariable=search_var,
            width=30
        )

        search_entry.pack(
            side="left"
        )

        tree = ttk.Treeview(
            body,
            columns=(
                "id",
                "date",
                "description",
                "category",
                "paid",
                "amount",
                "method"
            ),
            show="headings"
        )

        headings = [
            ("id", "ID", 50),
            ("date", "Date", 100),
            ("description", "Description", 200),
            ("category", "Category", 130),
            ("paid", "Paid By", 130),
            ("amount", "Amount", 100),
            ("method", "Split Method", 120)
        ]

        for column, heading, width in headings:

            tree.heading(
                column,
                text=heading
            )

            tree.column(
                column,
                width=width
            )

        tree.pack(
            fill="both",
            expand=True
        )

        def refresh(*args):

            for item in tree.get_children():
                tree.delete(item)

            search = search_var.get().lower()

            expenses = self.db.get_expenses(
                self.current_trip_id
            )

            for expense in expenses:

                if search and search not in expense[2].lower():
                    continue

                tree.insert(
                    "",
                    "end",
                    values=(
                        expense[0],
                        expense[1],
                        expense[2],
                        expense[3],
                        expense[4],
                        f"{self.current_trip[4]} {expense[5]:.2f}",
                        expense[7]
                    )
                )

        search_var.trace_add(
            "write",
            refresh
        )

        refresh()

        buttons = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        def edit():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Expense",
                    "Please select an expense."
                )
                return

            expense_id = int(
                tree.item(
                    selected[0],
                    "values"
                )[0]
            )

            self.add_expense_window(
                expense_id
            )

        def delete():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Expense",
                    "Please select an expense."
                )
                return

            expense_id = int(
                tree.item(
                    selected[0],
                    "values"
                )[0]
            )

            if not messagebox.askyesno(
                "Confirm",
                "Delete this expense?"
            ):
                return

            self.db.delete_expense(
                expense_id
            )

            refresh()

        ttk.Button(
            buttons,
            text="Edit Selected",
            command=edit
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ttk.Button(
            buttons,
            text="Delete Selected",
            command=delete
        ).pack(
            side="left"
        )

    # ==========================================================
    # ADD / EDIT EXPENSE
    # ==========================================================

    def add_expense_window(
        self,
        expense_id=None
    ):

        members = self.db.get_members(
            self.current_trip_id
        )

        if not members:
            messagebox.showwarning(
                "No Members",
                "Add at least one member first."
            )
            return

        window = tk.Toplevel(self)

        window.title(
            "Edit Expense"
            if expense_id
            else "Add Expense"
        )

        window.geometry("650x700")

        window.transient(self)
        window.grab_set()

        frame = ttk.Frame(
            window,
            padding=25
        )

        frame.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            frame,
            text=(
                "Edit Expense"
                if expense_id
                else "Add Expense"
            ),
            style="Heading.TLabel"
        ).pack(
            pady=(0, 20)
        )

        ttk.Label(
            frame,
            text="Description:"
        ).pack(
            anchor="w"
        )

        description_entry = ttk.Entry(
            frame,
            width=55
        )

        description_entry.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Amount:"
        ).pack(
            anchor="w"
        )

        amount_entry = ttk.Entry(
            frame,
            width=55
        )

        amount_entry.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Paid By:"
        ).pack(
            anchor="w"
        )

        member_names = [
            member[1]
            for member in members
        ]

        member_lookup = {
            member[1]: member[0]
            for member in members
        }

        paid_by_var = tk.StringVar()

        paid_by_combo = ttk.Combobox(
            frame,
            textvariable=paid_by_var,
            values=member_names,
            state="readonly",
            width=52
        )

        paid_by_combo.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Category:"
        ).pack(
            anchor="w"
        )

        category_var = tk.StringVar(
            value="Food"
        )

        category_combo = ttk.Combobox(
            frame,
            textvariable=category_var,
            values=[
                "Food",
                "Accommodation",
                "Transport",
                "Entertainment",
                "Shopping",
                "Other"
            ],
            state="readonly",
            width=52
        )

        category_combo.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Date (DD/MM/YYYY):"
        ).pack(
            anchor="w"
        )

        date_entry = ttk.Entry(
            frame,
            width=55
        )

        date_entry.insert(
            0,
            datetime.now().strftime("%d/%m/%Y")
        )

        date_entry.pack(
            pady=(5, 15)
        )

        ttk.Label(
            frame,
            text="Split Method:"
        ).pack(
            anchor="w"
        )

        split_var = tk.StringVar(
            value="Equal"
        )

        split_combo = ttk.Combobox(
            frame,
            textvariable=split_var,
            values=[
                "Equal",
                "Exact",
                "Percentage",
                "Shares"
            ],
            state="readonly",
            width=52
        )

        split_combo.pack(
            pady=(5, 15)
        )

        split_frame = tk.LabelFrame(
            frame,
            text="Split Values",
            bg="#ffffff",
            padx=10,
            pady=10
        )

        split_frame.pack(
            fill="both",
            expand=True,
            pady=5
        )

        value_entries = {}

        def build_split_inputs(*args):

            for widget in split_frame.winfo_children():
                widget.destroy()

            value_entries.clear()

            method = split_var.get()

            if method == "Equal":

                tk.Label(
                    split_frame,
                    text="The expense will be divided equally.",
                    bg="#ffffff",
                    fg="#555555"
                ).pack(
                    pady=15
                )

                return

            label_text = {
                "Exact": "Amount",
                "Percentage": "Percentage",
                "Shares": "Shares"
            }[method]

            for member_id, name, email in members:

                row = tk.Frame(
                    split_frame,
                    bg="#ffffff"
                )

                row.pack(
                    fill="x",
                    pady=3
                )

                tk.Label(
                    row,
                    text=name,
                    width=20,
                    anchor="w",
                    bg="#ffffff"
                ).pack(
                    side="left"
                )

                entry = ttk.Entry(
                    row,
                    width=20
                )

                entry.pack(
                    side="left"
                )

                tk.Label(
                    row,
                    text=label_text,
                    bg="#ffffff"
                ).pack(
                    side="left",
                    padx=5
                )

                value_entries[member_id] = entry

        split_var.trace_add(
            "write",
            build_split_inputs
        )

        build_split_inputs()

        if expense_id:

            expense, splits = self.db.get_expense(
                expense_id
            )

            if expense:

                description_entry.insert(
                    0,
                    expense[2]
                )

                amount_entry.insert(
                    0,
                    str(expense[3])
                )

                paid_member = self.db.get_member(
                    expense[4]
                )

                if paid_member:
                    paid_by_var.set(
                        paid_member[2]
                    )

                category_var.set(
                    expense[5]
                )

                date_entry.delete(
                    0,
                    "end"
                )

                date_entry.insert(
                    0,
                    expense[6]
                )

                split_var.set(
                    expense[7]
                )

                window.after(
                    100,
                    lambda: self.fill_split_values(
                        value_entries,
                        splits
                    )
                )

        def save_expense():

            description = description_entry.get().strip()
            amount_text = amount_entry.get().strip()
            paid_name = paid_by_var.get().strip()
            category = category_var.get()
            expense_date = date_entry.get().strip()
            method = split_var.get()

            if not description:
                messagebox.showerror(
                    "Error",
                    "Description cannot be empty.",
                    parent=window
                )
                return

            try:
                amount = float(amount_text)

                if amount <= 0:
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter a valid positive amount.",
                    parent=window
                )
                return

            if not paid_name:

                messagebox.showerror(
                    "Error",
                    "Select who paid.",
                    parent=window
                )

                return

            try:
                datetime.strptime(
                    expense_date,
                    "%d/%m/%Y"
                )

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Enter date as DD/MM/YYYY.",
                    parent=window
                )

                return

            paid_by = member_lookup[
                paid_name
            ]

            try:

                if method == "Equal":

                    member_ids = [
                        member[0]
                        for member in members
                    ]

                    splits = calculate_split(
                        "equal",
                        amount,
                        member_ids
                    )

                else:

                    values = {}

                    for member_id, entry in value_entries.items():

                        text = entry.get().strip()

                        if not text:
                            text = "0"

                        try:
                            values[member_id] = float(text)

                        except ValueError:
                            raise ValueError(
                                "All split values must be numbers."
                            )

                    splits = calculate_split(
                        method,
                        amount,
                        [member[0] for member in members],
                        values
                    )

                if expense_id:

                    self.db.update_expense(
                        expense_id,
                        description,
                        amount,
                        paid_by,
                        category,
                        expense_date,
                        method,
                        splits
                    )

                else:

                    self.db.add_expense(
                        self.current_trip_id,
                        description,
                        amount,
                        paid_by,
                        category,
                        expense_date,
                        method,
                        splits
                    )

                window.destroy()

                self.refresh_settlements()

                self.show_expenses()

            except ValueError as error:

                messagebox.showerror(
                    "Split Error",
                    str(error),
                    parent=window
                )

        ttk.Button(
            frame,
            text=(
                "Save Changes"
                if expense_id
                else "Add Expense"
            ),
            command=save_expense
        ).pack(
            pady=15
        )

    def fill_split_values(
        self,
        value_entries,
        splits
    ):

        for member_id, amount in splits:

            if member_id in value_entries:

                entry = value_entries[
                    member_id
                ]

                entry.delete(
                    0,
                    "end"
                )

                entry.insert(
                    0,
                    str(amount)
                )

    # ==========================================================
    # BALANCES
    # ==========================================================

    def show_balances(self):

        body = self.create_main_layout(
            "Balances"
        )

        balances = self.db.get_member_balances(
            self.current_trip_id
        )

        tree = ttk.Treeview(
            body,
            columns=(
                "member",
                "paid",
                "owed",
                "balance",
                "status"
            ),
            show="headings"
        )

        headings = [
            ("member", "Member"),
            ("paid", "Total Paid"),
            ("owed", "Total Owed"),
            ("balance", "Net Balance"),
            ("status", "Status")
        ]

        for column, heading in headings:

            tree.heading(
                column,
                text=heading
            )

        tree.column(
            "member",
            width=220
        )

        tree.column(
            "paid",
            width=150
        )

        tree.column(
            "owed",
            width=150
        )

        tree.column(
            "balance",
            width=150
        )

        tree.column(
            "status",
            width=180
        )

        tree.pack(
            fill="both",
            expand=True
        )

        for member_id, data in balances.items():

            balance = data["balance"]

            if balance > 0.01:
                status = "Should Receive"

            elif balance < -0.01:
                status = "Should Pay"

            else:
                status = "Settled"

            tree.insert(
                "",
                "end",
                values=(
                    data["name"],
                    f"{self.current_trip[4]} {data['paid']:.2f}",
                    f"{self.current_trip[4]} {data['owed']:.2f}",
                    f"{self.current_trip[4]} {balance:.2f}",
                    status
                )
            )

    # ==========================================================
    # SETTLEMENTS
    # ==========================================================

    def refresh_settlements(self):

        balances = self.db.get_member_balances(
            self.current_trip_id
        )

        settlements = calculate_settlements(
            balances
        )

        self.db.clear_settlements(
            self.current_trip_id
        )

        for settlement in settlements:

            self.db.add_settlement(
                self.current_trip_id,
                settlement["payer_id"],
                settlement["receiver_id"],
                settlement["amount"]
            )

    def show_settlements(self):

        self.refresh_settlements()

        body = self.create_main_layout(
            "Settlements"
        )

        settlements = self.db.get_settlements(
            self.current_trip_id
        )

        tree = ttk.Treeview(
            body,
            columns=(
                "id",
                "payer",
                "receiver",
                "amount",
                "status"
            ),
            show="headings"
        )

        headings = [
            ("id", "ID"),
            ("payer", "Payer"),
            ("receiver", "Receiver"),
            ("amount", "Amount"),
            ("status", "Status")
        ]

        for column, heading in headings:

            tree.heading(
                column,
                text=heading
            )

        tree.pack(
            fill="both",
            expand=True
        )

        for settlement in settlements:

            tree.insert(
                "",
                "end",
                values=(
                    settlement[0],
                    settlement[1],
                    settlement[2],
                    f"{self.current_trip[4]} {settlement[3]:.2f}",
                    settlement[4]
                )
            )

        def mark_paid():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    "Select Settlement",
                    "Please select a settlement."
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            settlement_id = int(
                values[0]
            )

            if values[4] == "Paid":

                messagebox.showinfo(
                    "Already Paid",
                    "This settlement is already marked as paid."
                )

                return

            self.db.update_settlement_status(
                settlement_id,
                "Paid"
            )

            self.show_settlements()

        ttk.Button(
            body,
            text="Mark Selected as Paid",
            command=mark_paid
        ).pack(
            pady=10
        )

    # ==========================================================
    # ANALYTICS
    # ==========================================================

    def show_analytics(self):

        body = self.create_main_layout(
            "Analytics"
        )

        tk.Label(
            body,
            text="Expense Analytics",
            font=("Arial", 16, "bold"),
            bg="#f4f6f8"
        ).pack(
            pady=20
        )

        ttk.Button(
            body,
            text="Show Category Chart",
            command=self.show_category_chart
        ).pack(
            pady=10
        )

        ttk.Button(
            body,
            text="Show Member Spending Chart",
            command=self.show_member_chart
        ).pack(
            pady=10
        )

        ttk.Button(
            body,
            text="Show Daily Spending Chart",
            command=self.show_daily_chart
        ).pack(
            pady=10
        )

    def show_category_chart(self):

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Install matplotlib using:\npip install matplotlib"
            )
            return

        data = self.db.get_category_totals(
            self.current_trip_id
        )

        if not data:
            messagebox.showinfo(
                "No Data",
                "No expenses available."
            )
            return

        labels = [
            row[0]
            for row in data
        ]

        values = [
            row[1]
            for row in data
        ]

        plt.figure(
            figsize=(8, 5)
        )

        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%"
        )

        plt.title(
            "Expenses by Category"
        )

        plt.tight_layout()
        plt.show()

    def show_member_chart(self):

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Install matplotlib using:\npip install matplotlib"
            )
            return

        data = self.db.get_member_spending(
            self.current_trip_id
        )

        labels = [
            row[0]
            for row in data
        ]

        values = [
            row[1]
            for row in data
        ]

        plt.figure(
            figsize=(8, 5)
        )

        plt.bar(
            labels,
            values
        )

        plt.title(
            "Spending by Member"
        )

        plt.xlabel(
            "Member"
        )

        plt.ylabel(
            f"Amount ({self.current_trip[4]})"
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()
        plt.show()

    def show_daily_chart(self):

        try:
            import matplotlib.pyplot as plt
        except ImportError:
            messagebox.showerror(
                "Missing Package",
                "Install matplotlib using:\npip install matplotlib"
            )
            return

        data = self.db.get_daily_spending(
            self.current_trip_id
        )

        if not data:
            messagebox.showinfo(
                "No Data",
                "No expenses available."
            )
            return

        labels = [
            row[0]
            for row in data
        ]

        values = [
            row[1]
            for row in data
        ]

        plt.figure(
            figsize=(9, 5)
        )

        plt.plot(
            labels,
            values,
            marker="o"
        )

        plt.title(
            "Daily Spending"
        )

        plt.xlabel(
            "Date"
        )

        plt.ylabel(
            f"Amount ({self.current_trip[4]})"
        )

        plt.xticks(
            rotation=30
        )

        plt.tight_layout()
        plt.show()

    # ==========================================================
    # REPORTS
    # ==========================================================

    def show_reports(self):

        body = self.create_main_layout(
            "Reports"
        )

        report_text = tk.Text(
            body,
            wrap="word",
            font=("Consolas", 10),
            bg="#ffffff"
        )

        report_text.pack(
            fill="both",
            expand=True
        )

        self.refresh_settlements()

        trip = self.db.get_trip(
            self.current_trip_id
        )

        members = self.db.get_members(
            self.current_trip_id
        )

        expenses = self.db.get_expenses(
            self.current_trip_id
        )

        balances = self.db.get_member_balances(
            self.current_trip_id
        )

        settlements = calculate_settlements(
            balances
        )

        report = create_text_report(
            trip,
            members,
            expenses,
            balances,
            settlements
        )

        report_text.insert(
            "1.0",
            report
        )

        report_text.config(
            state="disabled"
        )

        buttons = tk.Frame(
            body,
            bg="#f4f6f8"
        )

        buttons.pack(
            fill="x",
            pady=10
        )

        def export_csv():

            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[
                    ("CSV files", "*.csv")
                ]
            )

            if not path:
                return

            export_expenses_csv(
                path,
                expenses
            )

            messagebox.showinfo(
                "Export Complete",
                "CSV report exported successfully."
            )

        def save_text_report():

            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[
                    ("Text files", "*.txt")
                ]
            )

            if not path:
                return

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(report)

            messagebox.showinfo(
                "Export Complete",
                "Report saved successfully."
            )

        ttk.Button(
            buttons,
            text="Export CSV",
            command=export_csv
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ttk.Button(
            buttons,
            text="Save Text Report",
            command=save_text_report
        ).pack(
            side="left"
        )


if __name__ == "__main__":
    app = TripSplitApp()
    app.mainloop()
