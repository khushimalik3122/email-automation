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

# --- SUBJECTS (Random selection for variety) ---
SUBJECTS = [
    "Quick question about your team",
    "Regarding opportunities at {company}",
    "Loved your recent work at {company}",
    "Interested in your AI/ML work",
    "Exploring roles at {company}"
]

# --- TEMPLATES (Different styles to avoid spam filters) ---
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

# --- HUMAN LOGIC FUNCTIONS ---
def wait_humanly(min_sec, max_sec):
    wait = random.randint(min_sec, max_sec)
    print(f"⏳ Waiting {wait} seconds...")
    time.sleep(wait)

def is_work_time():
    now = datetime.now()
    # 9 AM to 7 PM and Monday to Friday only
    if now.hour < 9 or now.hour > 19 or now.weekday() >= 5:
        return False
    return True

def load_contacts():
    if not os.path.exists(CSV_FILE): return pd.DataFrame()
    df = pd.read_csv(CSV_FILE).dropna(subset=['Email', 'Name'])
    if os.path.exists(SENT_FILE):
        sent_df = pd.read_csv(SENT_FILE)
        df = df[~df['Email'].isin(sent_df['Email'])]
    return df

def update_sent_file(sent_list):
    if not sent_list: return
    new_df = pd.DataFrame(sent_list)
    if os.path.exists(SENT_FILE):
        old_df = pd.read_csv(SENT_FILE)
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = new_df
    final_df.drop_duplicates(subset=['Email'], inplace=True)
    final_df.to_csv(SENT_FILE, index=False)

# --- MAIN AUTOMATION ---
def send_human_emails():
    if not is_work_time():
        print("🌙 Skipping... Humans are sleeping or it's a weekend.")
        return

    contacts = load_contacts()
    if contacts.empty:
        print("✅ No new contacts to email.")
        return

    # Shuffle and pick a small batch (Session Limit)
    session_batch = contacts.sample(frac=1).reset_index(drop=True).head(random.randint(10, 15))
    
    yag = yagmail.SMTP(YOUR_EMAIL, YOUR_APP_PASSWORD)
    sent_this_session = []

    print(f"🚀 Starting session. Sending {len(session_batch)} emails...")

    for i, row in session_batch.iterrows():
        # Pre-send "Thinking" delay
        wait_humanly(40, 100)

        try:
            name, email, company = row['Name'], row['Email'], row['Company']
            subject = random.choice(SUBJECTS).format(company=company)
            body = random.choice(TEMPLATES).format(name=name, company=company)

            yag.send(to=email, subject=subject, contents=body)
            print(f"[{i+1}] ✅ Sent to {name}")

            sent_this_session.append({
                'Name': name, 'Email': email, 'Company': company, 
                'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # "The Break" Logic
            if (i + 1) % random.randint(3, 5) == 0:
                print("☕ Human Break: Getting some water/coffee...")
                wait_humanly(300, 600) # 5-10 min break

        except Exception as e:
            print(f"❌ Error for {email}: {e}")
            time.sleep(60)

    # Save to CSV (Fixed)
    update_sent_file(sent_this_session)
    print("📁 Progress saved to sent_contacts.csv")

if __name__ == "__main__":
    send_human_emails()
