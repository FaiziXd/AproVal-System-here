from flask import Flask, render_template_string, redirect, url_for, request
from datetime import datetime, timedelta

app = Flask(__name__)

# Data structures to hold approval requests and approvals
approval_history = {}
approval_data = {}

# HTML for the welcome page
welcome_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: url('https://raw.githubusercontent.com/FaiziXd/AproVal-System-here/refs/heads/main/296618a7fcc2574f667c59e3f2b83f72.jpg') no-repeat center center fixed;
            background-size: cover;
        }
        .welcome-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }
        .welcome-text {
            font-size: 36px;
            font-weight: bold;
            color: #fff;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        .visit-btn {
            background-color: #4CAF50;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
        }
        .visit-btn:hover {
            background-color: #3e8e41;
        }
    </style>
</head>
<body>
    <div class="welcome-container">
        <h1 class="welcome-text">Welcome!</h1>
        <a href="https://herf-2-faizu-apk.onrender.com" target="_blank">
            <button class="visit-btn">Visit Now</button>
        </a>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Approval System</title>
            <style>
                body { font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; background-color: #f7f7f7; }
                .container { max-width: 600px; margin: auto; padding: 20px; }
                h1, h2 { color: #444; }
                .button { background-color: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-top: 10px; }
                .button.reject { background-color: #dc3545; }
                .form-group { margin: 15px 0; }
                input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ddd; }
                #adminPanel { display: none; margin-top: 20px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
                .user-request { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .contact-link { margin-top: 20px; display: block; text-align: center; color: #007bff; text-decoration: none; }
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
                    <a href="https://www.facebook.com/The.drugs.ft.chadwick.67" class="contact-link">Contact Admin</a>
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
                        document.getElementById("requestStatus").innerText = "Your approval request has been sent!";
                        fetch('/request_approval', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ name: userName })
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
                    fetch('/admin_requests')
                        .then(response => response.json())
                        .then(data => {
                            let requestsHTML = data.map(req => `
                                <div class="user-request">
                                    <p><strong>Name:</strong> ${req.name}</p>
                                    <button class="button" onclick="approveRequest('${req.name}')">Approve</button>
                                    <button class="button reject" onclick="rejectRequest('${req.name}')">Reject</button>
                                </div>
                            `).join('');
                            document.getElementById("approvalRequests").innerHTML = requestsHTML;
                        });
                }

                function approveRequest(name) {
                    fetch(`/approve/${name}`, {
                        method: 'POST'
                    }).then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;  // Redirect to the welcome page
                        } else {
                            alert(`Request for ${name} approved!`);
                            loadRequests();  // Reload the requests
                        }
                    });
                }

                function rejectRequest(name) {
                    fetch(`/reject/${name}`, {
                        method: 'POST'
                    }).then(() => {
                        alert(`Request for ${name} rejected!`);
                        loadRequests();  // Reload the requests
                    });
                }
            </script>
        </body>
        </html>
    ''')

@app.route('/request_approval', methods=['POST'])
def request_approval():
    data = request.json
    user_name = data.get('name')
    approval_history[user_name] = datetime.now()
    return '', 204

@app.route('/admin_requests')
def admin_requests():
    return {'requests': [{'name': name} for name in approval_history]}

@app.route('/approve/<name>', methods=['POST'])
def approve_request(name):
    if name in approval_history:
        approval_data[name] = datetime.now() + timedelta(days=90)  # 3 months approval
        del approval_history[name]  # Remove from pending approvals
        print(f'Approved: {name}')  # Debugging line
        return redirect(url_for('welcome', name=name))
    return '', 204

@app.route('/reject/<name>', methods=['POST'])
def reject_request(name):
    if name in approval_history:
        del approval_history[name]
    return '', 204

@app.route('/welcome/<name>')
def welcome(name):
    print(f'Welcome page accessed for: {name}')  # Debugging line
    if name in approval_data and approval_data[name] > datetime.now():
        return render_template_string(welcome_page)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
