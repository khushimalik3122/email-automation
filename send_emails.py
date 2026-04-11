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

# --- HUMAN LOGIC SETTINGS ---
WORK_START = 9  # 9 AM
WORK_END = 19   # 7 PM

# --- SUBJECTS & TEMPLATES ---
SUBJECTS = [
    "Quick question about your team",
    "Regarding opportunities at {company}",
    "Loved your recent work at {company}",
    "Interested in your AI/ML work",
    "Exploring roles at {company}"
]

TEMPLATES = [
    """Hi {name},\n\nI came across your work at {company} and genuinely liked what your team is building in the AI/ML space.\n\nI’m currently working on Generative AI and RAG-based systems, focusing on improving model performance.\n\nI’d really appreciate the opportunity to connect and explore if I could contribute.\n\nBest regards,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/""",
    """Hi {name},\n\nYour work at {company} caught my attention while I was exploring teams working on impactful AI/ML solutions.\n\nI’m building systems around Generative AI and scalable ML pipelines. I would love to connect and get your valuable feedback on my work.\n\nBest regards,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/""",
    """Hi {name},\n\nI was recently exploring {company} and found your work particularly interesting.\n\nI’m currently working on AI/ML systems, especially in RAG pipelines, and I’m keen to understand how teams like yours approach scaling such solutions.\n\nBest,\nKhushi Malik""",
    """Hi {name},\n\nI had a quick question regarding how your team at {company} is currently approaching AI/ML development.\n\nI’ve been working on similar systems involving Generative AI, and I’m always looking to learn from professionals building impactful solutions.\n\nBest regards,\nKhushi Malik"""
]

def is_human_time():
    now = datetime.now()
    if not (WORK_START <= now.hour <= WORK_END):
        print(f"🌙 Outside work hours ({now.hour}:00). Skipping.")
        return False
    if now.strftime('%A') in ['Saturday', 'Sunday']:
        print("☀️ Weekend skip.")
        return False
    return True

def human_delay(long_break=False):
    wait = random.randint(300, 800) if long_break else random.randint(45, 150)
    print(f"⏳ Waiting {wait} seconds...")
    time.sleep(wait)

def load_contacts():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    df = pd.read_csv(CSV_FILE).dropna(subset=['Email', 'Name'])
    if os.path.exists(SENT_FILE):
        sent = pd.read_csv(SENT_FILE)
        df = df[~df['Email'].isin(sent['Email'])]
    return df

def save_sent(sent_list):
    if not sent_list: return
    new_df = pd.DataFrame(sent_list)
    if os.path.exists(SENT_FILE):
        old_df = pd.read_csv(SENT_FILE)
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = new_df
    final_df.drop_duplicates(subset=['Email'], inplace=True)
    final_df.to_csv(SENT_FILE, index=False)

def send_emails():
    if not is_human_time() or not YOUR_APP_PASSWORD:
        return

    contacts = load_contacts()
    if contacts.empty:
        print("No new contacts.")
        return

    # Session limit: 8 to 14 emails per run
    session_batch = contacts.sample(frac=1).reset_index(drop=True).head(random.randint(8, 14))
    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
    sent_emails = []

    for i, row in session_batch.iterrows():
        try:
            name, email = row['Name'], row['Email']
            company = row['Company'] if pd.notna(row['Company']) else "your team"
            
            subject = random.choice(SUBJECTS).format(company=company)
            body = random.choice(TEMPLATES).format(name=name, company=company)

            yag.send(to=email, subject=subject, contents=body)
            print(f"✅ [{i+1}] Sent to {name}")

            sent_emails.append({
                'Name': name, 'Email': email, 'Company': company, 
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            if (i + 1) % random.randint(3, 5) == 0:
                print("☕ Taking a coffee break...")
                human_delay(long_break=True)
            else:
                human_delay(long_break=False)

        except Exception as e:
            print(f"❌ Failed: {e}")
            time.sleep(60)

    save_sent(sent_emails)

if __name__ == "__main__":
    send_emails()
