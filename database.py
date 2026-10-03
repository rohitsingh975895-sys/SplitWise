import sqlite3
from pathlib import Path
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.database_dir = self.base_dir / "database"
        self.database_dir.mkdir(exist_ok=True)

        self.db_path = self.database_dir / "tripsplit.db"

        self.create_tables()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_name TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                currency TEXT DEFAULT 'INR',
                created_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                FOREIGN KEY (trip_id)
                    REFERENCES trips(trip_id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                paid_by INTEGER NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                split_method TEXT NOT NULL,
                FOREIGN KEY (trip_id)
                    REFERENCES trips(trip_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (paid_by)
                    REFERENCES members(member_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_splits (
                split_id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                amount_owed REAL NOT NULL,
                FOREIGN KEY (expense_id)
                    REFERENCES expenses(expense_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (member_id)
                    REFERENCES members(member_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settlements (
                settlement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                payer_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (trip_id)
                    REFERENCES trips(trip_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (payer_id)
                    REFERENCES members(member_id),
                FOREIGN KEY (receiver_id)
                    REFERENCES members(member_id)
            )
        """)

        connection.commit()
        connection.close()

    # ---------------- TRIPS ----------------

    def add_trip(self, trip_name, start_date, end_date, currency):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO trips
            (trip_name, start_date, end_date, currency, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            trip_name,
            start_date,
            end_date,
            currency,
            datetime.now().isoformat()
        ))

        trip_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return trip_id

    def get_trips(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT trip_id, trip_name, start_date, end_date, currency
            FROM trips
            ORDER BY trip_id DESC
        """)

        rows = cursor.fetchall()
        connection.close()

        return rows

    def get_trip(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT trip_id, trip_name, start_date, end_date, currency
            FROM trips
            WHERE trip_id = ?
        """, (trip_id,))

        row = cursor.fetchone()
        connection.close()

        return row

    def delete_trip(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM trips WHERE trip_id = ?",
            (trip_id,)
        )

        connection.commit()
        connection.close()

    # ---------------- MEMBERS ----------------

    def add_member(self, trip_id, name, email=""):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO members (trip_id, name, email)
            VALUES (?, ?, ?)
        """, (trip_id, name, email))

        member_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return member_id

    def get_members(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT member_id, name, email
            FROM members
            WHERE trip_id = ?
            ORDER BY name
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows

    def get_member(self, member_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT member_id, trip_id, name, email
            FROM members
            WHERE member_id = ?
        """, (member_id,))

        row = cursor.fetchone()
        connection.close()

        return row

    def update_member(self, member_id, name, email):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE members
            SET name = ?, email = ?
            WHERE member_id = ?
        """, (name, email, member_id))

        connection.commit()
        connection.close()

    def delete_member(self, member_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM expenses WHERE paid_by = ?",
            (member_id,)
        )

        paid_expenses = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM expense_splits WHERE member_id = ?",
            (member_id,)
        )

        split_records = cursor.fetchone()[0]

        if paid_expenses > 0 or split_records > 0:
            connection.close()
            raise ValueError(
                "This member is already connected to an expense."
            )

        cursor.execute(
            "DELETE FROM members WHERE member_id = ?",
            (member_id,)
        )

        connection.commit()
        connection.close()

    # ---------------- EXPENSES ----------------

    def add_expense(
        self,
        trip_id,
        description,
        amount,
        paid_by,
        category,
        expense_date,
        split_method,
        splits
    ):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO expenses
            (
                trip_id,
                description,
                amount,
                paid_by,
                category,
                expense_date,
                split_method
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            trip_id,
            description,
            amount,
            paid_by,
            category,
            expense_date,
            split_method
        ))

        expense_id = cursor.lastrowid

        for member_id, amount_owed in splits.items():
            cursor.execute("""
                INSERT INTO expense_splits
                (expense_id, member_id, amount_owed)
                VALUES (?, ?, ?)
            """, (
                expense_id,
                member_id,
                amount_owed
            ))

        connection.commit()
        connection.close()

        return expense_id

    def get_expenses(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                e.expense_id,
                e.expense_date,
                e.description,
                e.category,
                m.name,
                e.amount,
                e.paid_by,
                e.split_method
            FROM expenses e
            JOIN members m
                ON e.paid_by = m.member_id
            WHERE e.trip_id = ?
            ORDER BY e.expense_date DESC, e.expense_id DESC
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows

    def get_expense(self, expense_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                expense_id,
                trip_id,
                description,
                amount,
                paid_by,
                category,
                expense_date,
                split_method
            FROM expenses
            WHERE expense_id = ?
        """, (expense_id,))

        expense = cursor.fetchone()

        cursor.execute("""
            SELECT member_id, amount_owed
            FROM expense_splits
            WHERE expense_id = ?
        """, (expense_id,))

        splits = cursor.fetchall()

        connection.close()

        return expense, splits

    def update_expense(
        self,
        expense_id,
        description,
        amount,
        paid_by,
        category,
        expense_date,
        split_method,
        splits
    ):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE expenses
            SET
                description = ?,
                amount = ?,
                paid_by = ?,
                category = ?,
                expense_date = ?,
                split_method = ?
            WHERE expense_id = ?
        """, (
            description,
            amount,
            paid_by,
            category,
            expense_date,
            split_method,
            expense_id
        ))

        cursor.execute("""
            DELETE FROM expense_splits
            WHERE expense_id = ?
        """, (expense_id,))

        for member_id, amount_owed in splits.items():
            cursor.execute("""
                INSERT INTO expense_splits
                (expense_id, member_id, amount_owed)
                VALUES (?, ?, ?)
            """, (
                expense_id,
                member_id,
                amount_owed
            ))

        connection.commit()
        connection.close()

    def delete_expense(self, expense_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM expenses WHERE expense_id = ?",
            (expense_id,)
        )

        connection.commit()
        connection.close()

    # ---------------- BALANCES ----------------

    def get_member_balances(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        members = self.get_members(trip_id)

        balances = {}

        for member_id, name, email in members:

            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE trip_id = ?
                AND paid_by = ?
            """, (trip_id, member_id))

            total_paid = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COALESCE(SUM(es.amount_owed), 0)
                FROM expense_splits es
                JOIN expenses e
                    ON es.expense_id = e.expense_id
                WHERE e.trip_id = ?
                AND es.member_id = ?
            """, (trip_id, member_id))

            total_owed = cursor.fetchone()[0] or 0

            balances[member_id] = {
                "name": name,
                "paid": round(total_paid, 2),
                "owed": round(total_owed, 2),
                "balance": round(total_paid - total_owed, 2)
            }

        connection.close()

        return balances

    # ---------------- SETTLEMENTS ----------------

    def clear_settlements(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM settlements WHERE trip_id = ?",
            (trip_id,)
        )

        connection.commit()
        connection.close()

    def add_settlement(
        self,
        trip_id,
        payer_id,
        receiver_id,
        amount,
        status="Pending"
    ):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO settlements
            (
                trip_id,
                payer_id,
                receiver_id,
                amount,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            trip_id,
            payer_id,
            receiver_id,
            amount,
            status
        ))

        connection.commit()
        connection.close()

    def get_settlements(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                s.settlement_id,
                p.name,
                r.name,
                s.amount,
                s.status,
                s.payer_id,
                s.receiver_id
            FROM settlements s
            JOIN members p
                ON s.payer_id = p.member_id
            JOIN members r
                ON s.receiver_id = r.member_id
            WHERE s.trip_id = ?
            ORDER BY s.settlement_id
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows

    def update_settlement_status(self, settlement_id, status):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE settlements
            SET status = ?
            WHERE settlement_id = ?
        """, (status, settlement_id))

        connection.commit()
        connection.close()

    # ---------------- DASHBOARD ----------------

    def get_total_expenses(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE trip_id = ?
        """, (trip_id,))

        total = cursor.fetchone()[0] or 0

        connection.close()

        return round(total, 2)

    # ---------------- ANALYTICS ----------------

    def get_category_totals(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE trip_id = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows

    def get_member_spending(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT m.name, COALESCE(SUM(e.amount), 0)
            FROM members m
            LEFT JOIN expenses e
                ON m.member_id = e.paid_by
            WHERE m.trip_id = ?
            GROUP BY m.member_id
            ORDER BY SUM(e.amount) DESC
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows

    def get_daily_spending(self, trip_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT expense_date, SUM(amount)
            FROM expenses
            WHERE trip_id = ?
            GROUP BY expense_date
            ORDER BY expense_date
        """, (trip_id,))

        rows = cursor.fetchall()
        connection.close()

        return rows
