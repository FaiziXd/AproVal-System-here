from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

# Data storage for approvals
approval_data = {}  # Stores approved keys with expiration dates
approval_history = {}  # Stores pending approval requests
used_keys = {}  # Stores keys that have been used

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
    <div id="name-section">
        <input type="text" id="userName" placeholder="Enter your name">
        <button class="button" onclick="sendApproval()">Submit</button>
    </div>
    <div id="key-section" style="display: none;">
        <div class="user-key" id="keyDisplay"></div>
        <div id="contactOption" style="display: none;">
            <h2>Contact Option</h2>
            <p>If you have any questions, contact us!</p>
        </div>
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
            const userName = document.getElementById("userName").value;
            if (!userName) {
                alert("Please enter your name.");
                return;
            }
            fetch('/send_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: userName })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("keyDisplay").innerText = data.message;
                document.getElementById("key-section").style.display = "block";
                document.getElementById("contactOption").style.display = "block"; // Show contact option
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
                        <div>Name: ${req.name}, Mobile: ${req.mobile}
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
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;  // Redirect to welcome page
                } else {
                    alert('Request could not be approved.');
                }
            });
        }
    </script>
</body>
</html>
"""

# Function to generate a unique key for each device
def generate_unique_key():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template_string(html_code)

@app.route('/send_key', methods=['POST'])
def send_key():
    device = request.headers.get('User-Agent')
    user_data = request.json
    name = user_data.get('name')

    if not name:
        return jsonify({"message": "Name is required."}), 400

    key = generate_unique_key()

    # Check if the device already has an approved key
    if device in used_keys:
        return jsonify({"message": "You already have an approved key. Wait for 3 months or request a new one."})
    
    # Store the key with device info and user details
    approval_history[key] = {"device": device, "name": name, "mobile": "User Mobile Number Here"}  # Update with mobile number as needed
    return jsonify({"key": key, "message": "Aapka Approval send ho gaya hai! Apna name bata ke approval le sakte hain."})

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": [{"key": k, "device": v['device'], "name": v['name'], "mobile": v['mobile']} for k, v in approval_history.items()]})

@app.route('/approve/<key>', methods=['POST'])
def approve_request(key):
    if key in approval_history:
        approval_data[key] = datetime.now() + timedelta(days=90)  # Valid for 3 months
        used_keys[approval_history[key]['device']] = key  # Mark this device as having used the key
        del approval_history[key]  # Remove from pending requests
        # Redirect to welcome page
        return redirect(url_for('welcome', key=key))
    return '', 204

@app.route('/welcome/<key>')
def welcome(key):
    if key in approval_data and approval_data[key] > datetime.now():
        return render_template_string(welcome_page)  # Ensure welcome page is displayed
    return "Access Denied. Approval required.", 403

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
