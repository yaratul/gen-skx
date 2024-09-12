import requests
import logging
from colorama import Fore, Style, init
from datetime import datetime
import random

# Initialize colorama for colored output
init(autoreset=True)

# Set up logging for the Stripe Secret Key Validator
logging.basicConfig(filename='stripe_key_check.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Stripe Secret Key Validator Functions
def detect_key_type(sk_key):
    if sk_key.startswith("sk_live"):
        return "Live Key"
    elif sk_key.startswith("sk_test"):
        return "Test Key"
    else:
        return "Unknown Key Type"

def check_stripe_key(sk_key):
    key_type = detect_key_type(sk_key)
    logging.info(f"Checking {key_type}: {sk_key}")
    print(f"\nKey Type Detected: {Fore.YELLOW}{key_type}{Style.RESET_ALL}\n")

    tests = {
        "Charges Access": "https://api.stripe.com/v1/charges",
        "Customers Access": "https://api.stripe.com/v1/customers",
        "Refunds Access": "https://api.stripe.com/v1/refunds",
        "Balance Access": "https://api.stripe.com/v1/balance",
        "Payment Intents Access": "https://api.stripe.com/v1/payment_intents",
        "Cards Access": "https://api.stripe.com/v1/payment_methods?type=card",
        "Disputes Access": "https://api.stripe.com/v1/disputes",
    }

    headers = {
        "Authorization": f"Bearer {sk_key}"
    }

    passed = 0
    failed = 0

    print("Verifying Stripe Secret Key Abilities:\n")

    for test_name, url in tests.items():
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(Fore.GREEN + "✓ " + Style.RESET_ALL + f"{test_name} - Valid and Accessible")
            logging.info(f"{test_name}: Passed")
            passed += 1
        elif response.status_code == 401:
            print(Fore.RED + "✗ " + Style.RESET_ALL + f"{test_name} - Unauthorized (Invalid or expired key)")
            logging.warning(f"{test_name}: Unauthorized (Invalid or expired key)")
            failed += 1
        elif response.status_code == 403:
            print(Fore.RED + "✗ " + Style.RESET_ALL + f"{test_name} - Forbidden (Insufficient permissions)")
            logging.warning(f"{test_name}: Forbidden (Insufficient permissions)")
            failed += 1
        else:
            print(Fore.RED + "✗ " + Style.RESET_ALL + f"{test_name} - Inaccessible (Error code: {response.status_code})")
            logging.error(f"{test_name}: Inaccessible (Error code: {response.status_code})")
            failed += 1

    print("\nSummary Report:")
    print(f"Total Checks: {passed + failed}")
    print(Fore.GREEN + f"✓ Passed: {passed}")
    print(Fore.RED + f"✗ Failed: {failed}")
    logging.info(f"Summary: Total Checks - {passed + failed}, Passed - {passed}, Failed - {failed}")

# Credit Card Generator Functions
def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    checksum = 0
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def is_valid_luhn(card_number):
    return luhn_checksum(card_number) == 0

def generate_card_number(prefix, length):
    number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(length - len(prefix) - 1)])
    checksum_digit = 10 - luhn_checksum(int(number) * 10)
    if checksum_digit == 10:
        checksum_digit = 0
    return number + str(checksum_digit)

def generate_expiration_date():
    month = f'{random.randint(1, 12):02}'
    year = f'{random.randint(2024, 2030)}'
    return month, year

def generate_credit_card(prefix="4", length=16):
    card_number = generate_card_number(prefix, length)
    exp_month, exp_year = generate_expiration_date()
    return f"{card_number}|{exp_month}|{exp_year}"

def generate_multiple_cards(count=1, prefix="4", length=16):
    cards = []
    for _ in range(min(count, 50)):  # Limit to 50 cards per generation
        cards.append(generate_credit_card(prefix, length))
    return cards

# Main Menu
def main_menu():
    while True:
        print("\nWelcome to the Multi-Tool Application")
        print("Please choose an option:")
        print("1. Stripe Secret Key Validator")
        print("2. Credit Card Generator")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            sk_key = input("Please enter the Stripe Secret Key (sk_live_...): ")
            check_stripe_key(sk_key)
        elif choice == "2":
            count = int(input("Enter the number of cards to generate (max 50): "))
            prefix = input("Enter the card prefix (default is '4' for Visa): ") or "4"
            length = int(input("Enter the card length (default is 16): ") or 16)
            
            cards = generate_multiple_cards(count, prefix, length)
            print("\nGenerated Credit Cards:\n")
            for card in cards:
                print(card)
        elif choice == "3":
            print("Exiting the application. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
