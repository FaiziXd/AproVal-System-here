from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Track approved keys and approval history
approval_data = {}  # Stores approval expiration
approval_history = []  # Tracks each approval request

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
    </style>
</head>
<body>

    <button class="button" id="adminButton" onclick="showAdminPanel()">Admin Panel</button>
    <div id="welcome-section">
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
                        if (!acceptedKeys.has(request.key)) {
                            requestsHTML += `<div>Device: ${request.device}, Key: ${request.key}
                                <button onclick="acceptRequest('${request.key}')">Accept</button>
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
    device = request.headers.get('User-Agent')
    if key not in approval_data:
        approval_data[key] = datetime.now() + timedelta(days=90)
        approval_history.append({'key': key, 'device': device})
    return json.dumps({'key': key})

@app.route('/get_requests')
def get_requests():
    requests = [{'key': entry['key'], 'device': entry['device']} for entry in approval_history if entry['key'] not in approval_data]
    return json.dumps({'requests': requests})

@app.route('/accept_request/<key>', methods=['POST'])
def accept_request(key):
    if key in approval_data:
        approval_data[key] = datetime.now() + timedelta(days=90)
    return '', 204

@app.route('/welcome')
def welcome():
    return """
    <html><body style="display: flex; justify-content: center; align-items: center; height: 100vh; background-image: url('https://iili.io/2BSHySR.jpg'); background-size: cover; color: white; font-family: Arial, sans-serif; text-align: center;">
    <div><h1>Welcome Dear, Now Your Approval is Accepted. Visit Your Own APK.</h1>
    <a href="https://herf-2-faizu-apk.onrender.com/" style="background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Visit</a></div></body></html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
