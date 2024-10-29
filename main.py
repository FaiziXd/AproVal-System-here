from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

# Data storage for approvals
approval_data = {}  # Stores approved keys with expiration dates
approval_history = []  # Stores pending approval requests

# HTML Template for Main Page
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Approval System</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #282c34; color: white; }
        .button { background-color: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .admin-panel { display: none; color: white; margin-top: 20px; }
        .user-key { font-size: 1.2em; color: #ffdd57; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Approval System</h1>
    <div id="key-section">
        <button class="button" onclick="sendApproval()">Request Approval</button>
        <div class="user-key" id="keyDisplay"></div>
    </div>
    <button class="button" onclick="showAdminPanel()">Admin Panel</button>
    
    <div id="adminPanel" class="admin-panel">
        <h2>Admin Panel</h2>
        <input type="password" id="adminPassword" placeholder="Enter Admin Password">
        <button class="button" onclick="checkPassword()">Login</button>
        <div id="approvalRequests"></div>
    </div>

    <script>
        function sendApproval() {
            fetch('/send_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("keyDisplay").innerText = `Your Key: ${data.key} (Pending Approval)`;
            });
        }

        function showAdminPanel() {
            document.getElementById("adminPanel").style.display = "block";
        }

        function checkPassword() {
            const password = document.getElementById("adminPassword").value;
            if (password === "THE FAIZU") {
                fetch('/get_requests')
                .then(response => response.json())
                .then(data => {
                    let requestsHTML = data.requests.map(req => `
                        <div>Device: ${req.device}, Key: ${req.key}
                            <button onclick="approveRequest('${req.key}')">Approve</button>
                        </div>`).join('');
                    document.getElementById("approvalRequests").innerHTML = requestsHTML;
                });
            } else {
                alert("Incorrect password!");
            }
        }

        function approveRequest(key) {
            fetch(`/approve/${key}`, { method: 'POST' })
            .then(() => alert('Request approved!'));
        }
    </script>
</body>
</html>
"""

# HTML Template for Welcome Page
welcome_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #282c34; color: white; font-family: Arial, sans-serif; text-align: center; }
        a { background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; }
    </style>
</head>
<body>
    <div>
        <h1>Welcome! Your Approval is Accepted</h1>
        <a href="https://herf-2-faizu-apk.onrender.com/">Visit Your APK</a>
    </div>
</body>
</html>
"""

# Generate unique key for each device
def generate_unique_key():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_key', methods=['POST'])
def send_key():
    key = generate_unique_key()
    device = request.headers.get('User-Agent')
    if key not in approval_data:
        approval_history.append({"key": key, "device": device})
    return jsonify({"key": key})

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": approval_history})

@app.route('/approve/<key>', methods=['POST'])
def approve_request(key):
    if key in [req['key'] for req in approval_history]:
        approval_data[key] = datetime.now() + timedelta(days=90)
    return '', 204

@app.route('/welcome/<key>')
def welcome(key):
    # Check if the key is approved
    if key in approval_data and approval_data[key] > datetime.now():
        return render_template_string(welcome_page)
    else:
        return "Access Denied. Approval required.", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
