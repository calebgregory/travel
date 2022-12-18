import typing as ty
import os
import csv
from collections import defaultdict
from pprint import pprint

from typecats import Cat, unstruc_strip_defaults

this_dir = os.path.abspath(os.path.dirname(__file__))


@Cat
class ExpenseRawInput:
    paid: str  # "TRUE" or "FALSE"
    who: str  # e.g., "Brittany, Caleb, Katrina"
    total: str  # e.g., "$99.88"
    by: str = ''  # e.g., "Brittany"


@Cat
class Expense:
    paid: bool
    who: ty.Set[str]
    total: float
    by: str = ''

@Cat
class Report:
    amount_owed_by_person: ty.Mapping[str, ty.Mapping[str, float]]


def expense_from_raw_input(item: ExpenseRawInput) -> Expense:
    """Converts the expense items from the format they're in in Google Sheets to
    one that easier to work with in Python."""
    return Expense(
        paid=item.paid == "TRUE",
        by=item.by,
        who={name.strip() for name in item.who.split(",")},  # "Caleb, Brittany" -> Set { "Caleb", "Brittany" }
        total=float(item.total.strip("$")),  # Text "$99.88" -> Number 99.88
    )


def calculate_amounts_owed(expenses: ty.Iterable[Expense]) -> Report:
    # { "This person": { "owes this person": this_amount } }
    amount_owed_by_person = defaultdict(lambda: defaultdict(int))  # this_amount starts at 0

    for expense in expenses:
        if not expense.paid:  # if it's not paid yet, no one owes anyone anything; skip
            continue

        num_people = len(expense.who)  # the cost is split between this many people
        for person in expense.who:
            if expense.by != person:
                amount_owed_by_person[person][expense.by] += (expense.total / num_people)

    for oweds in amount_owed_by_person.values():
        for owed, amount in oweds.items():
            oweds[owed] = round(amount, 2)  # round to 2 digits

    return Report(amount_owed_by_person=dict(amount_owed_by_person))

def main():
    # ./private/expenses.csv is copy/pasted from the Google Sheet
    with open(os.path.join(this_dir, "private/expenses.csv"), "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        expense_raw_inputs = [ExpenseRawInput.struc(item) for item in reader]

    expenses = [expense_from_raw_input(item) for item in expense_raw_inputs]
    report = calculate_amounts_owed(expenses)

    pprint(unstruc_strip_defaults(report))

if __name__ == "__main__":
    main()
