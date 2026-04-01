from flask import Flask, render_template, request, redirect, url_for
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE_DIR, 'jobs.json')
LOG_FILE = os.path.join(BASE_DIR, 'email_log.txt')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Form submitted!")  # Debug print
        job = {
            'num_to_send': int(request.form.get('num_to_send', 0)),
            'delay_seconds': int(request.form.get('delay_seconds', 0))
        }
        print(f"Job to write: {job}")  # Debug print
        try:
            with open(JOBS_FILE, 'w') as f:
                json.dump(job, f)
            print("jobs.json updated successfully.")  # Debug print
        except Exception as e:
            print(f"Failed to write jobs.json: {e}")  # Debug print
        return redirect(url_for('index'))
    return render_template('form.html')

@app.route('/logs')
def logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_content = f.read()
    else:
        log_content = 'No logs yet.'
    return f"<pre>{log_content}</pre>"

if __name__ == '__main__':
    app.run(debug=True) 