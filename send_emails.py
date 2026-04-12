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

# Recommended: Set these in your environment variables for security
YOUR_EMAIL = os.environ.get('SENDER_EMAIL', 'Khushimalik511263@gmail.com')
YOUR_APP_PASSWORD = os.environ.get('APP_PASSWORD')

# --- HUMAN LOGIC SETTINGS ---
WORK_START = 9  # 9 AM
WORK_END = 19   # 7 PM

SUBJECTS = [
    "Quick question about your team",
    "Regarding opportunities at {company}",
    "Loved your recent work at {company}",
    "Interested in your AI/ML work",
    "Exploring roles at {company}"
]

TEMPLATES = [
    "Hi {name},\n\nI came across your work at {company} and genuinely liked what your team is building in the AI/ML space.\n\nI’m currently working on Generative AI and RAG-based systems, focusing on improving model performance.\n\nI’d really appreciate the opportunity to connect and explore if I could contribute.\n\nBest regards,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/",
    "Hi {name},\n\nYour work at {company} caught my attention while I was exploring teams working on impactful AI/ML solutions.\n\nI’m building systems around Generative AI and scalable ML pipelines. I would love to connect and get your valuable feedback on my work.\n\nBest regards,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/",
    "Hi {name},\n\nI was recently exploring {company} and found your work particularly interesting.\n\nI’m currently working on AI/ML systems, especially in RAG pipelines, and I’m keen to understand how teams like yours approach scaling such solutions.\n\nBest,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/",
    "Hi {name},\n\nI had a quick question regarding how your team at {company} is currently approaching AI/ML development.\n\nI’ve been working on similar systems involving Generative AI, and I’m always looking to learn from professionals building impactful solutions.\n\nBest regards,\nKhushi Malik\nLinkedIn: https://www.linkedin.com/in/khushi-6b972b280/"
]

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def is_human_time():
    now = datetime.now()
    if not (WORK_START <= now.hour <= WORK_END):
        log_message(f"🌙 Outside work hours ({now.hour}:00). Skipping.")
        return False
    if now.strftime('%A') in ['Saturday', 'Sunday']:
        log_message("☀️ Weekend skip.")
        return False
    return True

def human_delay(long_break=False):
    wait = random.randint(300, 800) if long_break else random.randint(45, 150)
    log_message(f"⏳ Waiting {wait} seconds...")
    time.sleep(wait)

def load_contacts():
    if not os.path.exists(CSV_FILE):
        log_message(f"❌ Error: {CSV_FILE} not found.")
        return pd.DataFrame()
    
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip() # Clean headers
    df = df.dropna(subset=['Email', 'Name'])
    
    if os.path.exists(SENT_FILE):
        sent = pd.read_csv(SENT_FILE)
        df = df[~df['Email'].isin(sent['Email'])]
    return df

def update_sent_file(record):
    """Appends a single record to the sent file immediately."""
    new_df = pd.DataFrame([record])
    if not os.path.exists(SENT_FILE):
        new_df.to_csv(SENT_FILE, index=False)
    else:
        new_df.to_csv(SENT_FILE, mode='a', header=False, index=False)

def send_emails():
    if not is_human_time():
        return
    
    if not YOUR_APP_PASSWORD:
        log_message("❌ Error: APP_PASSWORD not found in environment variables.")
        return

    contacts = load_contacts()
    if contacts.empty:
        log_message("✅ No new contacts to process.")
        return

    # Randomize batch size (8 to 14)
    batch_count = random.randint(8, 14)
    session_batch = contacts.sample(frac=1).reset_index(drop=True).head(batch_count)
    
    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
    log_message(f"🚀 Starting session. Batch size: {len(session_batch)}")

    for i, row in session_batch.iterrows():
        try:
            name, email = row['Name'], row['Email']
            company = row['Company'] if pd.notna(row['Company']) else "your team"
            
            subject = random.choice(SUBJECTS).format(company=company)
            body = random.choice(TEMPLATES).format(name=name, company=company)

            yag.send(to=email, subject=subject, contents=body)
            log_message(f"✅ [{i+1}/{len(session_batch)}] Sent to {name} ({email})")

            # Save immediately so we don't repeat if script stops
            update_sent_file({
                'Name': name, 'Email': email, 'Company': company, 
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Break logic
            if (i + 1) == len(session_batch):
                log_message("🏁 Session complete.")
            elif (i + 1) % random.randint(3, 5) == 0:
                log_message("☕ Taking a coffee break...")
                human_delay(long_break=True)
            else:
                human_delay(long_break=False)

        except Exception as e:
            log_message(f"❌ Failed to send to {name}: {str(e)}")
            time.sleep(60) # Wait a minute before trying the next one

if __name__ == "__main__":
    send_emails()
