from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()


# Moodle Credentials
try:
    USERNAME = os.getenv('MOODLE_USERNAME')
    PASSWORD = os.getenv('MOODLE_PASSWORD')
except KeyError as e:
    raise KeyError(f"Environment variable {e} not set. Please check your .env file.")

LOGIN_URL = 'https://ascend.iecbclearning.ca/login/index.php'
DOWNLOAD_URL = 'https://ascend.iecbclearning.ca/reportbuilder/download.php'
INTAKE_URL = 'https://ascend.iecbclearning.ca/local/edwiserform/export.php'


def download_moodle_data():
    # Start a session
    session = requests.Session()

    # Log in to Moodle
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    logintoken = soup.find('input', {'name': 'logintoken'})['value']

    login_payload = {
        'username': USERNAME,
        'password': PASSWORD,
        'logintoken': logintoken
    }
    response = session.post(LOGIN_URL, data=login_payload)

    # Download reports
    if 'Invalid login' in response.text:
        print('Login failed')
    else:
        reports_dict = {
            19: 'Cohorts'
        }
        
        for report_id, report_name in reports_dict.items():
            file_response = session.get(DOWNLOAD_URL, params={'id': report_id, 'download': 'csv'})
            with open(f'data/{report_name}.csv', 'wb') as f:
                f.write(file_response.content)
        intakes_dict = {
            14: 'Intake Responses - English',
            21: 'Intake Responses - French',
        }

        for intake_id, intake_name in intakes_dict.items():
            intake_response = session.get(INTAKE_URL, params={'id': intake_id, 'action': 'data', 'type': 'csv'})
            with open(f'data/{intake_name}.csv', 'wb') as f:
                f.write(intake_response.content)
        print('Reports downloaded successfully')
