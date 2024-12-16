import requests
import signal
import sys
from bs4 import BeautifulSoup
import re


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

# URL base and main page
base_url = "https://www.etsisi.upm.es"
main_page = "/escuela/dptos/dpto_per?id_dpto=SI"

# Regular expression to extract the JS function
email_pattern = re.compile(r"escribe_dir\('([^']+)','([^']+)'\)")

# Firstly we obtain the maing page
response = requests.get(base_url + main_page)
soup = BeautifulSoup(response.text, "html.parser")

# Filtering links according to criteria
user_links = soup.find_all(
    "a",
    href=lambda href: href and href.startswith("/sites/default/cicphp"),
    title=True,
    class_=False,
)

# Scrolling user links
for link in user_links:
    user_page = base_url + link["href"]
    user_response = requests.get(user_page)
    user_soup = BeautifulSoup(user_response.text, "html.parser")

    # Searching for the JS function that generates the mail
    script_tag = user_soup.find("script", text=email_pattern)
    if script_tag:
        match = email_pattern.search(script_tag.text)
        if match:
            username, domain = match.groups()
            email = f"{username}@{domain}"
            print(f"User: {link.text}, Email: {email}")
