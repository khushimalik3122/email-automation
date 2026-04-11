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

# --- TEMPLATES (CLEAN + UNIQUE) ---
TEMPLATES = [

"""Hi {name},

I came across your work at {company} and genuinely liked what your team is building in the AI/ML space.

I’m currently working on Generative AI and RAG-based systems, focusing on improving model performance and real-world deployment efficiency.

I’d really appreciate the opportunity to connect, learn from your experience, and explore if I could contribute in any way.

Best regards,  
Khushi Malik  
📞 +91-9536110472  
LinkedIn: https://www.linkedin.com/in/khushi-6b972b280/
""",

"""Hi {name},

Your work at {company} caught my attention while I was exploring teams working on impactful AI/ML solutions.

I’m building systems around Generative AI and scalable ML pipelines, with a strong focus on practical implementation and optimization.

I would love to connect with you and explore potential opportunities or even get your valuable feedback on my work.

Best regards,  
Khushi Malik  
📞 +91-9536110472  
LinkedIn: https://www.linkedin.com/in/khushi-6b972b280/
""",

"""Hi {name},

I was recently exploring {company} and found your work particularly interesting.

I’m currently working on AI/ML systems, especially in Generative AI and RAG pipelines, and I’m keen to understand how teams like yours approach building and scaling such solutions.

I’d really value the chance to connect and learn from your experience.

Best regards,  
Khushi Malik  
📞 +91-9536110472  
LinkedIn: https://www.linkedin.com/in/khushi-6b972b280/
""",

"""Hi {name},

I had a quick question regarding how your team at {company} is currently approaching AI/ML development and deployment.

I’ve been working on similar systems involving Generative AI and efficient model pipelines, and I’m always looking to learn from professionals building impactful solutions.

If you’re open to it, I’d really appreciate a brief conversation or your perspective.

Best regards,  
Khushi Malik  
📞 +91-9536110472  
LinkedIn: https://www.linkedin.com/in/khushi-6b972b280/
"""
]

# --- FUNCTIONS ---

def smart_delay():
    time.sleep(random.randint(60, 180))  # 1–3 min delay

def take_break():
    print("⏸ Taking a human-like break...")
    time.sleep(random.randint(300, 900))  # 5–15 min

def should_skip():
    return random.random() < 0.15  # 15% skip

def get_subject(company):
    return random.choice(SUBJECTS).format(company=company)

def get_template():
    return random.choice(TEMPLATES)

# --- LOAD CONTACTS ---
def load_contacts():
    df = pd.read_csv(CSV_FILE)
    df = df.dropna(subset=['Name', 'Email', 'Company'])

    if not os.path.exists(SENT_FILE):
        pd.DataFrame(columns=['Name', 'Email', 'Company', 'Date']).to_csv(SENT_FILE, index=False)

    sent = pd.read_csv(SENT_FILE)
    df = df[~df['Email'].isin(sent['Email'])]

    return df

# --- SAVE SENT ---
def save_sent(sent_emails):
    sent = pd.read_csv(SENT_FILE)
    sent = pd.concat([sent, pd.DataFrame(sent_emails)], ignore_index=True)
    sent.drop_duplicates(subset=['Email'], inplace=True)
    sent.to_csv(SENT_FILE, index=False)

# --- MAIN FUNCTION ---
def send_emails():
    if not YOUR_APP_PASSWORD:
        print("❌ App password missing")
        return

    contacts = load_contacts()
    if contacts.empty:
        print("No new contacts.")
        return

    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)

    # Shuffle contacts
    contacts = contacts.sample(frac=1).reset_index(drop=True)

    # Session-based sending (human-like)
    session_limit = random.randint(12, 18)
    contacts = contacts.head(session_limit)

    sent_emails = []
    total_to_send = min(MAX_EMAILS, len(contacts))

    print(f"🚀 Sending up to {total_to_send} emails in this session...")

    for i, row in contacts.head(total_to_send).iterrows():

        if should_skip():
            continue

        name = row['Name']
        email = row['Email']
        company = row['Company'] if pd.notna(row['Company']) else "your company"

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
                'Date': datetime.now()
            })

            with open(LOG_FILE, "a") as f:
                f.write(f"{datetime.now()} | {name} | {email} | sent\n")

        except Exception as e:
            print(f"[{i+1}] ❌ Failed: {e}")

        smart_delay()

        # Random batch break
        if i % random.randint(6, 10) == 0 and i != 0:
            take_break()

        # Random extra pause (human noise)
        if random.random() < 0.05:
            time.sleep(random.randint(120, 300))

    if sent_emails:
        save_sent(sent_emails)
        print("📁 Sent contacts updated.")

# --- RUN ---
if __name__ == "__main__":
    print(f"--- Start: {datetime.now()} ---")
    send_emails()
    print(f"--- End: {datetime.now()} ---")
