from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Track approved keys and approval history
approval_data = {}
approval_history = []

# Global key to be shared across all users
global_key = None

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
            if (generatedKey === "") {  // Check if a key has already been generated
                fetch('/get_key')
                    .then(response => response.json())
                    .then(data => {
                        generatedKey = data.key;
                        document.getElementById("keyDisplay").innerText = `Your Key: ${generatedKey} (Valid for 3 months)`;
                    });
            } else {
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
                    window.open('/welcome', '_blank');
                });
        }
    </script>
</body>
</html>
"""

# Store and send the key to users
@app.route('/get_key')
def get_key():
    global global_key
    if not global_key:
        global_key = generate_unique_key()
        approval_data[global_key] = datetime.now() + timedelta(days=90)  # Valid for 3 months
    return json.dumps({'key': global_key})

def generate_unique_key():
    return os.urandom(4).hex()  # Generate a random 8-character hex key

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_key', methods=['POST'])
def send_key():
    global global_key
    if not global_key:
        global_key = generate_unique_key()
        approval_data[global_key] = datetime.now() + timedelta(days=90)
    device = request.headers.get('User-Agent')
    approval_history.append({'key': global_key, 'device': device})
    return json.dumps({'key': global_key})

@app.route('/get_requests')
def get_requests():
    requests = [{'key': entry['key'], 'device': entry['device']} for entry in approval_history if entry['key'] not in approval_data]
    return json.dumps({'requests': requests})

@app.route('/accept_request/<key>', methods=['POST'])
def accept_request(key):
    approval_data[key] = datetime.now() + timedelta(days=90)
    return '', 204

@app.route('/welcome')
def welcome():
    return """
    <html><body style="display: flex; justify-content: center; align-items: center; height: 100vh; background-image: url('https://raw.githubusercontent.com/FaiziXd/AproVal-System-here/refs/heads/main/aba8e123f7e1a97a1d35e50cab476b79.jpg'); background-size: cover; color: white; font-family: Arial, sans-serif; text-align: center;">
    <div><h1>Welcome Dear, Now Your Approval is Accepted. Visit Your Own APK.</h1>
    <a href="https://herf-2-faizu-apk.onrender.com/" style="background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Visit</a>
    <button class="button" id="adminButton" onclick="showAdminPanel()">Admin Panel</button>
    </div></body>
    </html
>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
