from flask import Flask, request, redirect, render_template_string, jsonify, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# Data Storage
requests_data = {}  # Stores pending requests with names and devices
approved_users = {}  # Stores approved users with expiration date

# HTML Templates
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Approval System</title>
    <style>
        body { font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; background-color: #f7f7f7; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        h1, h2 { color: #444; }
        .button { background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .button.reject { background-color: #dc3545; }
        .form-group { margin: 15px 0; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
        #adminPanel { display: none; background: #fff; padding: 20px; border-radius: 10px; }
        .user-request { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Approval System</h1>
        <div id="userRequestForm">
            <h2>Request Approval</h2>
            <div class="form-group">
                <label for="userName">Enter Your Name</label>
                <input type="text" id="userName" placeholder="Your Name">
            </div>
            <button class="button" onclick="sendApproval()">Send Approval Request</button>
            <p id="requestStatus" style="color: green; margin-top: 10px;"></p>
            <a href="https://www.facebook.com/The.drugs.ft.chadwick.67" class="button">Contact Admin</a>
        </div>

        <button class="button" onclick="toggleAdminPanel()">Open Admin Panel</button>
        <div id="adminPanel">
            <h2>Admin Panel</h2>
            <div class="form-group">
                <input type="password" id="adminPassword" placeholder="Enter Admin Password">
                <button class="button" onclick="adminLogin()">Login</button>
            </div>
            <div id="approvalRequests"></div>
        </div>
    </div>

    <script>
        function sendApproval() {
            const userName = document.getElementById("userName").value;
            if (userName) {
                fetch('/send_approval', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: userName })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("requestStatus").innerText = data.message;
                });
            } else {
                alert("Please enter your name.");
            }
        }

        function toggleAdminPanel() {
            document.getElementById("adminPanel").style.display = 
                document.getElementById("adminPanel").style.display === "block" ? "none" : "block";
        }

        function adminLogin() {
            const password = document.getElementById("adminPassword").value;
            if (password === "THE_FAIZU") {
                loadRequests();
            } else {
                alert("Incorrect password!");
            }
        }

        function loadRequests() {
            fetch('/get_requests')
            .then(response => response.json())
            .then(data => {
                let requestsHTML = data.requests.map(req => `
                    <div class="user-request">
                        <p><strong>Name:</strong> ${req.name}</p>
                        <p><strong>Device:</strong> ${req.device}</p>
                        <button class="button" onclick="approveRequest('${req.name}')">Approve</button>
                        <button class="button reject" onclick="rejectRequest('${req.name}')">Reject</button>
                    </div>
                `).join('');
                document.getElementById("approvalRequests").innerHTML = requestsHTML;
            });
        }

        function approveRequest(name) {
            fetch(`/approve/${name}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => alert(data.message));
        }

        function rejectRequest(name) {
            alert(`Request for ${name} rejected.`);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_approval', methods=['POST'])
def send_approval():
    data = request.json
    name = data.get('name')
    device = request.headers.get('User-Agent')

    if name in requests_data or name in approved_users:
        return jsonify({"message": "Request already sent or user already approved!"})

    requests_data[name] = {"device": device}
    return jsonify({"message": "Your approval request has been sent!"})

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": [{"name": k, "device": v["device"]} for k, v in requests_data.items()]})

@app.route('/approve/<name>', methods=['POST'])
def approve_request(name):
    if name in requests_data:
        approved_users[name] = datetime.now() + timedelta(days=90)  # 3 months validity
        del requests_data[name]
        return jsonify({"message": f"User '{name}' approved successfully!"})
    return jsonify({"message": "User not found in requests!"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
