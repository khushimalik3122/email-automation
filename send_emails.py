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
RESUME_FILE = os.path.join(BASE_DIR, 'Khushi(4).pdf')

# Recommended: Set these in your environment variables for security
YOUR_EMAIL = os.environ.get('SENDER_EMAIL', 'Khushimalik511263@gmail.com')
YOUR_APP_PASSWORD = os.environ.get('APP_PASSWORD')

# --- HUMAN LOGIC SETTINGS ---
WORK_START = 23  # 9 AM
WORK_END = 19   # 7 PM

SUBJECTS = [
    "Quick question about your team",
    "Regarding opportunities at {company}",
    "Loved your recent work at {company}",
    "Interested in your AI/ML work",
    "Exploring roles at {company}"
]

TEMPLATES = [
    """Hi {name},

I came across your work at {company} and really liked what your team is building in the AI/ML space.

I wanted to briefly share my experience:

*Internship — Planto AI*
During my internship at Planto AI, I developed AI Coder Pro, a context-aware AI coding assistant integrated within VS Code. I built a Webview-based UI along with a backend extension, and designed agent-based workflows that analyze codebases and automatically generate or modify files. This significantly improved developer productivity and was built with a modular architecture to support multiple AI models.

*Freelance — Zindi (AI/ML Challenges)*
* In the Amini GeoFM “Decoding the Field” challenge, I built an end-to-end crop classification pipeline using Sentinel-2 time-series data. I engineered features like NDVI and SAVI and implemented a PatchTST-based model combined with ensemble methods, achieving a macro F1-score of 0.75.

* In the UNIDO AfricaRice Challenge, I developed an offline rice quality grading system using TensorFlow Lite. I optimized a ConvNeXt-based model with FP16 quantization and graph-level improvements, reducing memory usage by ~75% and enabling accurate on-device inference in low-connectivity environments.

Across these projects, I’ve focused on building practical AI systems — from GenAI-powered developer tools to time-series modeling and edge deployment.

I’ve attached my CV for your review and would really appreciate any feedback.

I’d love the opportunity to connect and learn from your experience at {company}. Would you be open to a quick 10-minute chat this week?

Best regards,
Khushi Malik
📞 +91 95361 10472
LinkedIn: https://www.linkedin.com/in/khushi-6b972b280/"""

    
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
    """Appends a single record to the sent file immediately in the required format."""
    # Define the exact column order based on your requirement
    target_columns = ['Date', 'Name', 'Email', 'Company']
    
    # Automatically add the current date/time if it wasn't passed in the record
    if 'Date' not in record:
        record['Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    # Extract only the required fields, defaulting to an empty string if a field is missing
    formatted_record = {col: record.get(col, '') for col in target_columns}
    
    # Create the DataFrame with the strict column order
    new_df = pd.DataFrame([formatted_record], columns=target_columns)
    
    # Save or append to the CSV
    if not os.path.exists(SENT_FILE):
        # Create new file with headers
        new_df.to_csv(SENT_FILE, index=False)
    else:
        # Append to existing file without adding headers again
        new_df.to_csv(SENT_FILE, mode='a', header=False, index=False)

def send_emails():
    if not is_human_time(): return
    if not YOUR_APP_PASSWORD:
        log_message("❌ Error: APP_PASSWORD environment variable not set.")
        return 
    if not os.path.exists(RESUME_FILE):
        log_message(f"❌ Error: Resume file {RESUME_FILE} not found.")
        return

    contacts = load_contacts()
    if contacts.empty:
        log_message("✅ No new contacts to process.")
        return

    batch_count = random.randint(8, 14)
    session_batch = contacts.sample(frac=1).reset_index(drop=True).head(batch_count)
    
    try:
        yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
        log_message(f"🚀 Starting session. Batch size: {len(session_batch)}")

        for i, (idx, row) in enumerate(session_batch.iterrows()):
            try:
                name, email = row['Name'], row['Email']
                company = row['Company'] if pd.notna(row['Company']) else "your team"
                
                subject = random.choice(SUBJECTS).format(company=company)
                body = random.choice(TEMPLATES).format(name=name, company=company)

                yag.send(to=email, subject=subject, contents=body, attachments=RESUME_FILE)
                log_message(f"✅ [{i+1}/{len(session_batch)}] Sent to {name} ({email})")

                update_sent_file({
                    'Name': name, 'Email': email, 'Company': company, 
                    'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                if (i + 1) == len(session_batch):
                    log_message("🏁 Session complete.")
                else:
                    is_long = (i + 1) % random.randint(3, 5) == 0
                    if is_long: log_message("☕ Taking a coffee break...")
                    human_delay(long_break=is_long)

            except Exception as e:
                log_message(f"❌ Failed for {name}: {str(e)}")
                time.sleep(30)
                
    finally:
        if 'yag' in locals():
            yag.close()
            log_message("🔒 SMTP session closed.")

if __name__ == "__main__":
    send_emails()
