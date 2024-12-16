import requests
import signal
import sys
from bs4 import BeautifulSoup
import re
import csv


# Colors
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def def_handler(sig, frame):
    print(f"{bcolors.FAIL}\n\n[!] Quitting...\n{bcolors.ENDC}")
    sys.exit(1)


signal.signal(signal.SIGINT, def_handler)


def scraping(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(
            f"{bcolors.FAIL}\n\n[!] Error accessing the page. Status code: {response.status_code}\n{bcolors.ENDC}"
        )
        sys.exit(1)
    soup = BeautifulSoup(response.content, "html.parser")

    # Searching for all <p> elements with the class “card”
    cards = soup.find_all("p", class_="card")

    # Extracting emails using a regular expression
    email_pattern = re.compile(r"[\w.-]+@[\w.-]+\.[a-zA-Z]{2,6}")
    phone_pattern = re.compile(r"Tel[eé]fono: (\d{9})")

    emails = set()
    records = []

    for card in cards:
        card_text = card.get_text(separator=" ").strip()
        found_emails = email_pattern.findall(card_text)
        found_phones = phone_pattern.findall(card_text)
        phone = found_phones[0] if found_phones else "N/A"

        for email in found_emails:
            cleaned_email = email.lower().strip()
            if cleaned_email not in emails:
                emails.add(cleaned_email)
                # We extract name and role if available
                name = (
                    card.find("strong").get_text(strip=True)
                    if card.find("strong")
                    else "N/A"
                )
                role = (
                    card_text.replace(name, "")
                    .replace(email, "")
                    .replace(f"Phone: {phone}", "")
                    .strip()
                )
                records.append((name, cleaned_email, phone, role))

    return records


if __name__ == "__main__":
    url = "https://www.fi.upm.es/?id=estructura/departamentos"
    records = scraping(url)

    # Showing results
    if records:
        print(f"{bcolors.OKGREEN}Emails found:{bcolors.ENDC}")
        for _, email, _, _ in records:
            print(f"[*] {email}")

        # Asking if user wants to save in a CSV file
        save_csv = (
            input(
                f"{bcolors.WARNING}Do you want to save the information in a CSV file (y/n)?{bcolors.ENDC} {bcolors.UNDERLINE}(Extra information such as name, role and phone number will be stored in the CSV){bcolors.ENDC}: "
            )
            .strip()
            .lower()
        )
        if save_csv == "y":
            with open("data.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Email", "Phone", "Role"])
                writer.writerows(records)
            print(f"{bcolors.OKGREEN}Information stored in 'data.csv'{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}No data were found{bcolors.ENDC}")
