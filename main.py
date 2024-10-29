from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Data storage for approvals
approval_data = {}  # Stores approved keys with their expiration
approval_history = []  # Stores pending approval requests

# HTML template
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
        let generatedKey = "";

        function sendApproval() {
            fetch('/send_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("keyDisplay").innerText = `Your Key: ${data.key} (Valid for 3 months)`;
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

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_key', methods=['POST'])
def send_key():
    key = "unique-key-1234"  # Static key for all users
    device = request.headers.get('User-Agent')
    expiration_date = datetime.now() + timedelta(days=90)
    approval_data[key] = expiration_date
    approval_history.append({"key": key, "device": device})
    return jsonify({"key": key})

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": approval_history})

@app.route('/approve/<key>', methods=['POST'])
def approve_request(key):
    if key in approval_data:
        approval_data[key] = datetime.now() + timedelta(days=90)  # Update expiration
    return '', 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
