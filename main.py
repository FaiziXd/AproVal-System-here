from flask import Flask, render_template_string, request, redirect, url_for
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# Track approved keys and approval history
approval_data = {}  # Approved keys with expiration dates
approval_history = []  # List of approval requests (pending and approved)
global_key = "018289e0"  # Fixed key for all users

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

    <div class="user-key" id="keyDisplay">Your Key: {{ global_key }} (Valid for 3 months)</div>
    <button class="button" id="sendApproval" onclick="sendApprovalRequest()">Send Approval</button>

    <button class="button" id="adminButton" onclick="showAdminPanel()">Admin Panel</button>
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
        const acceptedKeys = new Set();

        function sendApprovalRequest() {
            fetch('/send_key', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
                .then(response => response.json())
                .then(data => alert(`Approval request sent with key: ${data.key}`));
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
                })
                .catch(error => console.error("Error fetching requests:", error));
            document.getElementById("approvalRequests").classList.remove('hidden');
        }

        function acceptRequest(key) {
            fetch(`/accept_request/${key}`, { method: 'POST' })
                .then(() => {
                    acceptedKeys.add(key);
                    alert(`Request accepted!`);
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_code, global_key=global_key)

@app.route('/send_key', methods=['POST'])
def send_key():
    device = request.headers.get('User-Agent')
    if global_key not in approval_data:
        approval_data[global_key] = datetime.now() + timedelta(days=90)  # Key is valid for 3 months
    approval_history.append({'key': global_key, 'device': device})
    return json.dumps({'key': global_key})

@app.route('/get_requests')
def get_requests():
    requests = [{'key': entry['key'], 'device': entry['device']} for entry in approval_history if entry['key'] not in approval_data]
    return json.dumps({'requests': requests})

@app.route('/accept_request/<key>', methods=['POST'])
def accept_request(key):
    if key in approval_data:
        approval_data[key] = datetime.now() + timedelta(days=90)  # Extend expiration date
    return '', 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
