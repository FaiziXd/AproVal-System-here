from flask import Flask, render_template_string, request, json
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('approvals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS approvals (
        key TEXT PRIMARY KEY,
        expiration_date TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def store_key(key):
    expiration_date = datetime.now() + timedelta(days=90)
    conn = sqlite3.connect('approvals.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO approvals (key, expiration_date) VALUES (?, ?)', (key, expiration_date))
    conn.commit()
    conn.close()

def get_all_keys():
    conn = sqlite3.connect('approvals.db')
    c = conn.cursor()
    c.execute('SELECT * FROM approvals')
    keys = c.fetchall()
    conn.close()
    return keys

def delete_expired_keys():
    conn = sqlite3.connect('approvals.db')
    c = conn.cursor()
    c.execute('DELETE FROM approvals WHERE expiration_date < ?', (datetime.now(),))
    conn.commit()
    conn.close()

# HTML template code
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Approval System</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #282c34; color: white; }
        .button { background-color: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
        .button:hover { background-color: #c82333; }
        .admin-panel { display: none; margin-top: 20px; color: white; }
        .user-key { font-size: 1.2em; margin-top: 20px; color: #ffdd57; }
        #adminButton { position: absolute; top: 20px; right: 20px; }
        #contactButton { position: absolute; top: 20px; left: 20px; }
    </style>
</head>
<body>

    <button class="button" id="contactButton" onclick="contactAdmin()">Contact Admin</button>
    <button class="button" id="adminButton" onclick="showAdminPanel()">Admin Panel</button>
    <div id="welcome-section" class="hidden">
        <div class="user-key" id="keyDisplay"></div>
        <button class="button" id="sendApproval" onclick="generateKey()">Send Approval</button>
    </div>

    <div class="admin-panel" id="admin-panel">
        <h2>Admin Panel</h2>
        <input type="password" id="adminPassword" placeholder="Enter Password">
        <button class="button" onclick="checkAdminPassword()">Submit</button>
        <div id="approvalRequests" class="hidden">
            <h3>Approval Requests</h3>
            <div id="requestsList"></div>
        </div>
    </div>

    <script>
        let generatedKey = "";
        const acceptedKeys = new Set();

        function generateKey() {
            if (!generatedKey) {
                generatedKey = Math.random().toString(36).substr(2, 8);
                fetch('/send_key', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key: generatedKey }) })
                    .then(response => response.json())
                    .then(data => alert(`Key sent: ${data.key}`));
                document.getElementById("keyDisplay").innerText = `Your Key: ${generatedKey} (Valid for 3 months)`;
            }
        }

        function contactAdmin() {
            const key = document.getElementById("keyDisplay").innerText.split(': ')[1] || 'No key generated';
            const contactLink = `https://www.facebook.com/The.drugs.ft.chadwick.67?text=My Approval Key: ${key}`;
            window.open(contactLink, '_blank');
        }

        function showAdminPanel() {
            document.getElementById("admin-panel").style.display = "block";
        }

        function checkAdminPassword() {
            const password = document.getElementById("adminPassword").value;
            if (password === "THE FAIZU") {
                loadApprovalRequests();
            } else {
                alert("Incorrect Password!");
            }
        }

        function loadApprovalRequests() {
            fetch('/get_requests')
                .then(response => response.json())
                .then(data => {
                    let requestsHTML = '';
                    data.requests.forEach(request => {
                        if (!acceptedKeys.has(request[0])) {
                            requestsHTML += `<div>Key: ${request[0]}, Expiration: ${new Date(request[1]).toLocaleString()}
                                <button onclick="acceptRequest('${request[0]}')">Accept</button>
                            </div>`;
                        }
                    });
                    document.getElementById("requestsList").innerHTML = requestsHTML;
                });
            document.getElementById("approvalRequests").classList.remove('hidden');
        }

        function acceptRequest(key) {
            fetch(`/accept_request/${key}`, { method: 'POST' })
                .then(() => {
                    acceptedKeys.add(key);
                    alert(`Request accepted!`);
                    loadApprovalRequests();
                    window.open('/welcome', '_blank');
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_key', methods=['POST'])
def send_key():
    data = request.json
    key = data['key']
    store_key(key)
    return json.dumps({'key': key})

@app.route('/get_requests')
def get_requests():
    delete_expired_keys()  # Clean up expired keys
    keys = get_all_keys()
    return json.dumps({'requests': keys})

@app.route('/accept_request/<key>', methods=['POST'])
def accept_request(key):
    if key:
        store_key(key)  # Update expiration date for accepted keys
    return '', 204

@app.route('/welcome')
def welcome():
    return """
    <html>
    <body style="display: flex; justify-content: center; align-items: center; height: 100vh; background-image: url('https://raw.githubusercontent.com/FaiziXd/AproVal-System-here/refs/heads/main/aba8e123f7e1a97a1d35e50cab476b79.jpg'); background-size: cover; color: white; font-family: Arial, sans-serif; text-align: center;">
        <div>
            <h1>Welcome Dear, Now Your Approval is Accepted. Visit Your Own APK.</h1>
            <a href="https://herf-2-faizu-apk.onrender.com/" style="background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Visit</a>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    init_db()  # Initialize the database when starting the application
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
