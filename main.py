from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Track approved keys and approval history
approval_data = {}
approval_history = []

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

        /* Animation styles */
        .fade-in {
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Image animation */
        .image-container {
            position: relative;
            width: 100%;
            height: 300px;
            overflow: hidden;
            margin: 20px 0;
        }
        .image {
            position: absolute;
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0;
            animation: fade 6s infinite;
        }
        .image:nth-child(1) { animation-delay: 0s; }
        .image:nth-child(2) { animation-delay: 3s; }

        @keyframes fade {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
        }
    </style>
</head>
<body>

    <button class="button" id="adminButton" onclick="showAdminPanel()">Admin Panel</button>
    <div id="welcome-section" class="fade-in">
        <div class="user-key" id="keyDisplay"></div>
        <button class="button" id="sendApproval" onclick="generateKey()">Send Approval</button>
        <div class="image-container" id="approvalImage" style="display:none;">
            <img class="image" src="https://example.com/your_image_url1.jpg" alt="Approval Image 1" />
            <img class="image" src="https://example.com/your_image_url2.jpg" alt="Approval Image 2" />
        </div>
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
                document.getElementById("keyDisplay").innerText = `Your Key: ${generatedKey} (Valid for 3 months)`;
                document.getElementById("approvalImage").style.display = "block"; // Show approval images
                fetch('/send_key', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ key: generatedKey }) })
                    .then(response => response.json())
                    .then(data => alert(`Key sent: ${data.key}`));
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
    approval_data[key] = datetime.now() + timedelta(days=90)
    return '', 204

@app.route('/welcome')
def welcome():
    return """
    <html><body style="display: flex; justify-content: center; align-items: center; height: 100vh; background-image: url('https://raw.githubusercontent.com/FaiziXd/AproVal-System-here/refs/heads/main/aba8e123f7e1a97a1d35e50cab476b79.jpg'); background-size: cover; color: white; font-family: Arial, sans-serif; text-align: center;">
    <div><h1>Welcome Dear, Now Your Approval is Accepted. Visit Your Own APK.</h1>
    <a href="https://herf-2-faizu-apk.onrender.com/" style="background-color: #dc3545; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Visit</a>
    </div></body></html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
