import pandas as pd
import yagmail
import time
import os
import random
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'sentagain_contacts.csv')
SENT_FILE = os.path.join(BASE_DIR, 'sent_contacts.csv')
LOG_FILE = os.path.join(BASE_DIR, 'email_log.txt')

YOUR_EMAIL = os.environ.get('SENDER_EMAIL', 'Khushimalik511263@gmail.com')
YOUR_APP_PASSWORD = os.environ.get('APP_PASSWORD')

# Daily safe limit
MAX_EMAILS = random.randint(40, 55)

# --- SUBJECTS ---
SUBJECTS = [
    "Quick question about your team",
    "Regarding opportunities at {company}",
    "Loved your recent work at {company}",
    "Interested in your AI/ML work",
    "Exploring roles at {company}"
]

# --- TEMPLATES ---
TEMPLATES = [
   
]

# --- FUNCTIONS ---
def smart_delay():
    time.sleep(random.randint(60, 180))

def take_break():
    print("⏸ Taking a human-like break...")
    time.sleep(random.randint(300, 900))

def should_skip():
    return random.random() < 0.15

def get_subject(company):
    return random.choice(SUBJECTS).format(company=company)

def get_template():
    return random.choice(TEMPLATES)

def load_contacts():
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: {CSV_FILE} not found!")
        return pd.DataFrame()

    df = pd.read_csv(CSV_FILE)
    df = df.dropna(subset=['Name', 'Email', 'Company'])

    if not os.path.exists(SENT_FILE):
        pd.DataFrame(columns=['Name', 'Email', 'Company', 'Date']).to_csv(SENT_FILE, index=False)

    sent = pd.read_csv(SENT_FILE)
    df = df[~df['Email'].isin(sent['Email'])]
    return df

def save_sent(sent_emails_list):
    if not sent_emails_list:
        return
    sent = pd.read_csv(SENT_FILE)
    new_sent = pd.DataFrame(sent_emails_list)
    sent = pd.concat([sent, new_sent], ignore_index=True)
    sent.drop_duplicates(subset=['Email'], inplace=True)
    sent.to_csv(SENT_FILE, index=False)
    print("📁 Sent contacts CSV updated successfully.")

# --- MAIN FUNCTION ---
def send_emails():
    if not YOUR_APP_PASSWORD:
        print("❌ App password missing")
        return

    contacts = load_contacts()
    if contacts.empty:
        print("No new contacts to email.")
        return

    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
    
    # Shuffle and limit
    contacts = contacts.sample(frac=1).reset_index(drop=True)
    NUM_TO_SEND = int(os.environ.get('NUM_EMAILS', 15))
    contacts = contacts.head(NUM_TO_SEND)

    
    sent_emails = [] 
    
    print(f"🚀 Sending up to {len(contacts)} emails in this session...")

    for i, row in contacts.iterrows():
        if should_skip():
            print(f"⏭ Skipping {row['Name']} (Random human behavior)")
            continue

        name = row['Name']
        email = row['Email']
        company = row['Company'] if pd.notna(row['Company']) else "your company"

        if "@" not in str(email):
            continue

        subject = get_subject(company)
        template = get_template()
        body = template.format(name=name, company=company)

        try:
            yag.send(to=email, subject=subject, contents=body)
            print(f"[{i+1}] ✅ Sent to {name} <{email}>")

            
            sent_emails.append({
                'Name': name,
                'Email': email,
                'Company': company,
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.now()} | {name} | {email} | sent\n")

        except Exception as e:
            print(f"[{i+1}] ❌ Failed for {name}: {e}")

        # Delays
        if i < len(contacts) - 1:
            smart_delay()
            if i % random.randint(6, 10) == 0 and i != 0:
                take_break()

   
    if sent_emails:
        save_sent(sent_emails)
    else:
        print("No emails were actually sent this session.")

if __name__ == "__main__":
    print(f"--- Start: {datetime.now()} ---")
    send_emails()
    print(f"--- End: {datetime.now()} ---")
