class Trip:
    def __init__(
        self,
        trip_id=None,
        trip_name="",
        start_date="",
        end_date="",
        currency="INR"
    ):
        self.trip_id = trip_id
        self.trip_name = trip_name
        self.start_date = start_date
        self.end_date = end_date
        self.currency = currency


class Member:
    def __init__(
        self,
        member_id=None,
        trip_id=None,
        name="",
        email=""
    ):
        self.member_id = member_id
        self.trip_id = trip_id
        self.name = name
        self.email = email


class Expense:
    def __init__(
        self,
        expense_id=None,
        trip_id=None,
        description="",
        amount=0,
        paid_by=None,
        category="Other",
        expense_date="",
        split_method="Equal"
    ):
        self.expense_id = expense_id
        self.trip_id = trip_id
        self.description = description
        self.amount = amount
        self.paid_by = paid_by
        self.category = category
        self.expense_date = expense_date
        self.split_method = split_method
