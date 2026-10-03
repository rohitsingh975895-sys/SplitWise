import csv
from pathlib import Path


def export_expenses_csv(
    file_path,
    expenses
):
    path = Path(file_path)

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Date",
            "Description",
            "Category",
            "Paid By",
            "Amount",
            "Split Method"
        ])

        for expense in expenses:
            writer.writerow([
                expense[1],
                expense[2],
                expense[3],
                expense[4],
                expense[5],
                expense[7]
            ])


def create_text_report(
    trip,
    members,
    expenses,
    balances,
    settlements
):
    lines = []

    lines.append("=" * 60)
    lines.append("                  TRIPSPLIT REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append(f"Trip Name: {trip[1]}")
    lines.append(f"Start Date: {trip[2]}")
    lines.append(f"End Date: {trip[3]}")
    lines.append(f"Currency: {trip[4]}")
    lines.append("")

    lines.append("MEMBERS")
    lines.append("-" * 60)

    for member in members:
        lines.append(f"- {member[1]}")

    lines.append("")

    lines.append("EXPENSES")
    lines.append("-" * 60)

    total = 0

    for expense in expenses:

        amount = expense[5]
        total += amount

        lines.append(
            f"{expense[1]} | "
            f"{expense[2]} | "
            f"{expense[3]} | "
            f"{expense[4]} | "
            f"{trip[4]} {amount:.2f}"
        )

    lines.append("")
    lines.append(
        f"TOTAL EXPENSES: {trip[4]} {total:.2f}"
    )

    lines.append("")

    lines.append("BALANCES")
    lines.append("-" * 60)

    for member_id, data in balances.items():

        lines.append(
            f"{data['name']}: "
            f"Paid={trip[4]} {data['paid']:.2f}, "
            f"Owed={trip[4]} {data['owed']:.2f}, "
            f"Balance={trip[4]} {data['balance']:.2f}"
        )

    lines.append("")

    lines.append("SETTLEMENT")
    lines.append("-" * 60)

    if settlements:

        for settlement in settlements:
            lines.append(
                f"{settlement['payer']} -> "
                f"{settlement['receiver']} : "
                f"{trip[4]} {settlement['amount']:.2f}"
            )

    else:
        lines.append("No settlement required.")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)
