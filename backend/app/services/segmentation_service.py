def get_customer_segment(customer: dict, membership: dict, consent: dict):
    total_spend = float(customer.get("total_spend") or 0)
    purchase_frequency = int(customer.get("purchase_frequency") or 0)
    tier = membership.get("tier") if membership else "Non-member"
    do_not_contact = consent.get("do_not_contact") if consent else False

    if do_not_contact:
        return "Do Not Contact"

    if tier == "Non-member" and total_spend >= 10000 and purchase_frequency >= 3:
        return "Potential Member"

    if tier == "Silver" and total_spend >= 22000:
        return "Silver-to-Gold Eligible"

    if tier == "Gold" and total_spend >= 50000:
        return "Gold-to-Platinum Eligible"

    if purchase_frequency <= 2:
        return "Low Spender"

    if total_spend >= 50000:
        return "High Spender"

    if total_spend >= 20000:
        return "Medium Spender"

    return "General Customer"