def calculate_settlements(balances):
    """
    balances format:

    {
        member_id: {
            "name": "Rohit",
            "balance": 6000
        }
    }
    """

    creditors = []
    debtors = []

    for member_id, data in balances.items():

        balance = round(data["balance"], 2)

        if balance > 0.01:
            creditors.append({
                "member_id": member_id,
                "name": data["name"],
                "amount": balance
            })

        elif balance < -0.01:
            debtors.append({
                "member_id": member_id,
                "name": data["name"],
                "amount": abs(balance)
            })

    creditors.sort(
        key=lambda x: x["amount"],
        reverse=True
    )

    debtors.sort(
        key=lambda x: x["amount"],
        reverse=True
    )

    settlements = []

    creditor_index = 0
    debtor_index = 0

    while (
        creditor_index < len(creditors)
        and debtor_index < len(debtors)
    ):
        creditor = creditors[creditor_index]
        debtor = debtors[debtor_index]

        amount = min(
            creditor["amount"],
            debtor["amount"]
        )

        amount = round(amount, 2)

        if amount > 0.01:
            settlements.append({
                "payer_id": debtor["member_id"],
                "payer": debtor["name"],
                "receiver_id": creditor["member_id"],
                "receiver": creditor["name"],
                "amount": amount
            })

        creditor["amount"] = round(
            creditor["amount"] - amount,
            2
        )

        debtor["amount"] = round(
            debtor["amount"] - amount,
            2
        )

        if creditor["amount"] <= 0.01:
            creditor_index += 1

        if debtor["amount"] <= 0.01:
            debtor_index += 1

    return settlements
