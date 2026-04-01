import pandas as pd
import yagmail
import time
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, '23800+ Ultimate HR Outreach List - DataNiti.xlsx - 3300+ Verified HR Leads.csv')
TEMPLATE_FILE = os.path.join(BASE_DIR, 'email_template.txt')
SENT_FILE = os.path.join(BASE_DIR, 'sent_contacts.csv')
PDF_ATTACHMENT = os.path.join(BASE_DIR, 'Khushi(4).pdf')
LOG_FILE = os.path.join(BASE_DIR, 'email_log.txt')

# Pull credentials securely
YOUR_EMAIL = os.environ.get('SENDER_EMAIL', 'khushimalik15566@gmail.com')
YOUR_APP_PASSWORD = os.environ.get('APP_PASSWORD')
NUM_TO_SEND = int(os.environ.get('NUM_EMAILS', 10))
DELAY_SECONDS = int(os.environ.get('DELAY_SECONDS', 30))

def load_contacts():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Could not find the file: {CSV_FILE}")

    try:
        if CSV_FILE.endswith('.xlsx'):
            try:
                df = pd.read_excel(CSV_FILE, engine='openpyxl')
            except Exception:
                df = pd.read_csv(CSV_FILE)
        else:
            df = pd.read_csv(CSV_FILE)
    except Exception as e:
        raise ValueError(f"Failed to read the file. Error: {e}")
    
    df = df.dropna(how='all')
    required_columns = ['Name', 'Email', 'Company']
    df = df.dropna(subset=required_columns)
    
    # Create empty sent file if it doesn't exist to prevent errors
    if not os.path.exists(SENT_FILE):
        pd.DataFrame(columns=['Name', 'Email', 'Company', 'Date']).to_csv(SENT_FILE, index=False)
        
    sent = pd.read_csv(SENT_FILE)
    df = df[~df['Email'].isin(sent['Email'])]
    
    return df

def save_sent_contacts(sent_emails):
    sent = pd.read_csv(SENT_FILE)
    sent = pd.concat([sent, pd.DataFrame(sent_emails)], ignore_index=True)
    sent.drop_duplicates(subset=['Email'], inplace=True)
    sent.to_csv(SENT_FILE, index=False)

def load_template():
    if not os.path.exists(TEMPLATE_FILE):
        return "Hi {name},\n\nI am applying for a role at {company}.\n\nBest,\nKhushi"
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def send_emails():
    if not YOUR_APP_PASSWORD:
        print("ERROR: App Password not found!")
        return

    contacts = load_contacts()
    if contacts.empty:
        print('No new contacts to email.')
        return

    template = load_template()
    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
    
    if not os.path.exists(PDF_ATTACHMENT):
        print(f"Error: CV file not found at {PDF_ATTACHMENT}")
        return

    sent_emails = []
    print(f"Found {len(contacts)} new contacts. Sending {min(NUM_TO_SEND, len(contacts))} emails...")

    for i, (index, row) in enumerate(contacts.head(NUM_TO_SEND).iterrows()):
        name, email, company = row['Name'], row['Email'], row['Company']
        if pd.isna(company): company = "your company"

        body = template.format(name=name, company=company)
        subject = f'Application for AI/ML/Data Full time and Intern Roles at {company}'

        try:
            yag.send(to=email, subject=subject, contents=body, attachments=PDF_ATTACHMENT)
            print(f"[{i+1}/{NUM_TO_SEND}] Sent to {name} <{email}>")
            sent_emails.append({'Name': name, 'Email': email, 'Company': company, 'Date': datetime.now()})
        except Exception as e:
            print(f"[{i+1}/{NUM_TO_SEND}] Failed to send to {name} <{email}>: {e}")

        if i < min(NUM_TO_SEND, len(contacts)) - 1:
            time.sleep(DELAY_SECONDS)

    if sent_emails:
        save_sent_contacts(sent_emails)
        print("Updated sent_contacts.csv locally.")

if __name__ == '__main__':
    print(f"--- Starting Email Run at {datetime.now()} ---")
    send_emails()
    print("--- Email Run Completed ---")
