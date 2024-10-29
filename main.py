from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

# Data storage for approvals
approval_data = {}  # Stores approved keys with expiration dates
approval_history = {}  # Stores pending approval requests

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
        <input type="text" id="userName" placeholder="Enter Your Name" />
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
            const userName = document.getElementById("userName").value;
            fetch('/send_key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: userName })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("keyDisplay").innerText = data.message;
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
                        <div>Device: ${req.device}, Name: ${req.name}
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
                    window.location.href = response.url;  // Redirect to user welcome page
                } else {
                    alert('Request could not be approved.');
                }
            });
        }
    </script>
</body>
</html>
"""

# HTML Template for Welcome Page
def welcome_page(name, contact):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Welcome</title>
        <style>
            body {{ display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #282c34; color: white; font-family: Arial, sans-serif; text-align: center; }}
            a {{ background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; }}
            .contact {{ margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div>
            <h1>Welcome {name}! Your Approval is Accepted</h1>
            <div class="contact">
                <a href="https://www.facebook.com/The.drugs.ft.chadwick.67">Contact Us</a>
            </div>
            <a href="https://herf-2-faizu-apk.onrender.com/">Visit Your APK</a>
        </div>
    </body>
    </html>
    """

# HTML Template for Approval Page
def approval_page(name):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Approval Page</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; background-color: #282c34; color: white; }}
            .button {{ background-color: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>Approval Pending for {name}</h1>
        <p>Your approval request has been sent. Please wait for the admin to accept your request.</p>
        <div class="contact">
            <a href="https://www.facebook.com/The.drugs.ft.chadwick.67">Contact Admin</a>
        </div>
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

    # Check if the device already has an approved key
    if device in approval_data and approval_data[device] > datetime.now():
        return jsonify({"message": "Aapka approval abhi tak valid hai. Agle 3 mahine tak koi naya request nahi karna."})

    key = generate_unique_key()
    
    # Store the key with device info and user details
    approval_history[key] = {"device": device, "name": name}
    return redirect(url_for('approval_page_display', name=name))

@app.route('/approval_page/<name>')
def approval_page_display(name):
    return render_template_string(approval_page(name))

@app.route('/get_requests')
def get_requests():
    return jsonify({"requests": [{"key": k, "device": v['device'], "name": v['name']} for k, v in approval_history.items()]})

@app.route('/approve/<key>', methods=['POST'])
def approve_request(key):
    if key in approval_history:
        # Store approval for device
        device = approval_history[key]['device']
        name = approval_history[key]['name']
        approval_data[device] = datetime.now() + timedelta(days=90)  # Valid for 3 months
        del approval_history[key]  # Remove from pending requests
        
        # Redirect to welcome page
        return redirect(url_for('welcome', key=key, name=name, contact='https://www.facebook.com/The.drugs.ft.chadwick.67'))
    return '', 204

@app.route('/welcome/<key>/<name>/<contact>')
def welcome(key, name, contact):
    # Check if the key is approved
    if key in approval_data:
        return render_template_string(welcome_page(name, contact))
    return "Access Denied. Approval required.", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
