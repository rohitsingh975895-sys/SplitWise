def equal_split(amount, member_ids):
    if not member_ids:
        raise ValueError("No members selected.")

    amount = float(amount)
    count = len(member_ids)

    base = round(amount / count, 2)

    splits = {}

    for member_id in member_ids:
        splits[member_id] = base

    # Correct rounding difference
    difference = round(
        amount - sum(splits.values()),
        2
    )

    if difference != 0:
        first_member = member_ids[0]
        splits[first_member] = round(
            splits[first_member] + difference,
            2
        )

    return splits


def exact_split(amounts, total_amount):
    total_amount = float(total_amount)

    if not amounts:
        raise ValueError("No split amounts entered.")

    cleaned = {}

    for member_id, value in amounts.items():
        value = float(value)

        if value < 0:
            raise ValueError(
                "Exact split amounts cannot be negative."
            )

        cleaned[member_id] = round(value, 2)

    total = round(sum(cleaned.values()), 2)

    if abs(total - total_amount) > 0.01:
        raise ValueError(
            f"Split total ₹{total:.2f} does not match "
            f"expense amount ₹{total_amount:.2f}."
        )

    return cleaned


def percentage_split(percentages, total_amount):
    total_amount = float(total_amount)

    if not percentages:
        raise ValueError("No percentages entered.")

    cleaned_percentages = {}

    for member_id, value in percentages.items():
        value = float(value)

        if value < 0 or value > 100:
            raise ValueError(
                "Percentage must be between 0 and 100."
            )

        cleaned_percentages[member_id] = value

    percentage_total = round(
        sum(cleaned_percentages.values()),
        2
    )

    if abs(percentage_total - 100) > 0.01:
        raise ValueError(
            f"Percentage total is {percentage_total}%. "
            "It must equal 100%."
        )

    splits = {}

    for member_id, percentage in cleaned_percentages.items():
        splits[member_id] = round(
            total_amount * percentage / 100,
            2
        )

    difference = round(
        total_amount - sum(splits.values()),
        2
    )

    if difference != 0:
        first_member = next(iter(splits))
        splits[first_member] = round(
            splits[first_member] + difference,
            2
        )

    return splits


def share_split(shares, total_amount):
    total_amount = float(total_amount)

    if not shares:
        raise ValueError("No shares entered.")

    cleaned = {}

    for member_id, value in shares.items():
        value = float(value)

        if value <= 0:
            raise ValueError(
                "Shares must be greater than zero."
            )

        cleaned[member_id] = value

    total_shares = sum(cleaned.values())

    if total_shares <= 0:
        raise ValueError("Total shares must be greater than zero.")

    splits = {}

    for member_id, share in cleaned.items():
        splits[member_id] = round(
            total_amount * share / total_shares,
            2
        )

    difference = round(
        total_amount - sum(splits.values()),
        2
    )

    if difference != 0:
        first_member = next(iter(splits))
        splits[first_member] = round(
            splits[first_member] + difference,
            2
        )

    return splits


def calculate_split(
    method,
    amount,
    member_ids,
    values=None
):
    method = method.lower()

    if method == "equal":
        return equal_split(amount, member_ids)

    if method == "exact":
        return exact_split(values, amount)

    if method == "percentage":
        return percentage_split(values, amount)

    if method == "shares":
        return share_split(values, amount)

    raise ValueError("Unknown split method.")
