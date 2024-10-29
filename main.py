from flask import Flask, render_template_string, redirect, url_for, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Storing approval requests and approved data
approval_history = {}  # Pending approvals
approval_data = {}  # Approved users with access expiry date

# HTML templates
index_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Approval System</title>
    <style>
        /* Add your styles here */
    </style>
</head>
<body>
    <h1>Approval System</h1>
    <input type="text" id="userName" placeholder="Enter Your Name">
    <button onclick="sendApproval()">Send Approval Request</button>
    <p id="requestStatus"></p>
    <button onclick="toggleAdminPanel()">Open Admin Panel</button>
    
    <div id="adminPanel" style="display: none;">
        <input type="password" id="adminPassword" placeholder="Enter Admin Password">
        <button onclick="adminLogin()">Login</button>
        <div id="approvalRequests"></div>
    </div>
    
    <script>
        function sendApproval() {
            const userName = document.getElementById("userName").value;
            if (userName) {
                fetch('/request_approval', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: userName })
                }).then(response => response.json())
                  .then(data => document.getElementById("requestStatus").innerText = data.message);
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
                            <button onclick="approveRequest('${req.name}')">Approve</button>
                            <button onclick="rejectRequest('${req.name}')">Reject</button>
                        </div>
                    `).join('');
                    document.getElementById("approvalRequests").innerHTML = requestsHTML;
                });
        }

        function approveRequest(name) {
            fetch(`/approve/${name}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Request approved!") {
                        alert(`Request for ${name} approved!`);
                        loadRequests();
                    }
                });
        }

        function rejectRequest(name) {
            alert(`Request for ${name} rejected!`);
            loadRequests();
        }
    </script>
</body>
</html>
"""

welcome_page = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome</title>
</head>
<body>
    <h1>Welcome, {{ name }}! Your approval is accepted.</h1>
    <a href="https://herf-2-faizu-apk.onrender.com">Visit Now</a>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    return render_template_string(index_page)

@app.route('/request_approval', methods=['POST'])
def request_approval():
    name = request.json.get('name')
    if name and name not in approval_history and name not in approval_data:
        approval_history[name] = datetime.now()
        return jsonify({"message": "Your approval request has been sent!"})
    return jsonify({"message": "Request already sent or approved!"})

@app.route('/approve/<name>', methods=['POST'])
def approve_request(name):
    if name in approval_history:
        approval_data[name] = datetime.now() + timedelta(days=90)
        del approval_history[name]
        return jsonify({"message": "Request approved!"})
    return '', 204

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": [{"name": name} for name in approval_history.keys()]})

@app.route('/welcome/<name>')
def welcome(name):
    if name in approval_data and approval_data[name] > datetime.now():
        return render_template_string(welcome_page, name=name)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
