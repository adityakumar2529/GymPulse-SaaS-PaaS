import os
from flask import Flask, request, render_template_string, redirect, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "saas-demo-secret-key")

#=================================================================================
# USER LOGIN DATA
#=================================================================================

USERS = {
    "alpha": {
        "password": "alpha123",
        "branch": "GymPulse Downtown"
    },
    "beta": {
        "password": "beta123",
        "branch": "GymPulse Karama"
    }
}

#=================================================================================
# SAAS DATA 
#================================================================================

DATA = {
    "GymPulse Downtown": {
        "revenue": 35000,
        "members": 1000,
        "classes_today": 9,
        "capacity": "82%",
        "member_data": [
            ("p-101", "David Watkins", "VIP Access", "Active"),
            ("p-102", "Samuel Jackson", "Regular", "Active"),
            ("p-103", "Emily Smith", "Regular", "Pending Renewal"),
            ("p-104", "Sarah Jacob", "Yoga", "Active")
        ],
        "schedule": [
            ("08:00 AM", "Morning HIIT Blitz", "Coach Ryan", "Studio A"),
            ("10:30 AM", "Power Yoga", "Priya Patel", "Studio B"),
            ("05:00 PM", "CrossFit Foundations", "Coach Mark", "Main Floor"),
            ("07:00 PM", "Spin & Cardio", "Jack Grace", "Cycle Room")
        ]
},
    "GymPulse Karama": {
        "revenue": 28900,
        "members": 850,
        "classes_today": 11,
        "capacity": "90%",
        "member_data": [
            ("p-201", "Liam Johnson", "Regular", "Active"),
            ("p-202", "Olivia Brown", "VIP Access", "Expired"),
            ("p-203", "Noah Davis", "Personal Training", "Active"),
            ("p-204", "Emma Wilson", "Regular", "Pending Renewal")
        ],
        "schedule": [
            ("7:00 AM", "Sunrise Yoga", "Priya Patel", "Studio B"),
            ("09:00 AM", "Strength & Conditioning", "Coach Mark", "Main Floor"),
            ("06:00 PM", "Zumba Dance Party", "Coach Tyson", "Studio A"),
            ("08:00 PM", "Evening HIIT Blitz", "Coach Ryan", "Main Floor")
        ]
    }
}

#=================================================================================
#LOGIN PAGE HTML
#=================================================================================

LOGIN_HTML = """

<!DOCTYPE html>
<html>
<head>

<title>GymPulse SaaS - Login</title>

<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: #333; }
    .login-card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); width: 340px; }
    .logo { text-align: center; font-size: 26px; font-weight: bold; color: #0284c7; margin-bottom: 20px; }
    label { font-size: 14px; font-weight: 600; color: #475569; }
    input { width: 100%; padding: 12px; margin: 8px 0 18px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
    button { width: 100%; padding: 12px; background: #0284c7; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
    button:hover { background: #0369a1; }
    .error { color: #dc2626; text-align: center; font-size: 14px; margin-bottom: 15px; }
    .demo-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; border-radius: 6px; font-size: 13px; margin-top: 20px; }
</style>

</head>

<body>
    <div class = "login-card">
        <div class = "logo">GymPulse SaaS</div>
        {% if error %}<div class = "error">{{error}}</div>{% endif %}
        <form method = "post">
            <label>Username</label>
            <input type = "text" name = "username" placeholder = "Enter Username" required>
            
            <label>Password</label>
            <input type = "password" name = "password" placeholder = "Enter Password" required>
            <button type = "submit">Sign In to GymPulse Portal</button>
        </form>
        
        <div class = "demo-box">
            <b>Demo Branch Accounts:</b><br>
            Downtown: <code>gym_alpha</code> / <code>alpha123</code><br>
            Marina: <code>gym_beta</code> / <code>beta123</code><br>
        </div>
    </div>

</body>
</html>
"""

#======================================================================================
#DASHBOARD PAGE HTML
#======================================================================================

BASE_PAGE = """
<!DOCTYPE HTML>
<html>
<head>
<title>GymPulse Cloud Platform</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
    body {margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f1f5f9; color: #0f172a; }
    .sidebar { width: 230px; background: #0f172a; height: 100vh; position: fixed; color: white; padding: 25px 20px; box-sizing: border-box; }
    .logo { font-size: 22px; font-weight: bold; color: #38bdf8; margin-bottom: 35px; }
    .menu-item { display: block; color: #94a3b8; text-decoration: none; padding: 12px; margin: 8px 0; border-radius: 6px; font-weight: 500; }
    .menu-item:hover, .active { background: #0284c7; color: white; }
    .logout { margin-top: 60px; color: #f87171 !important; }
    .main { margin-left: 250px; padding: 35px; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; }
    .branch-tag { background: #e0f2fe; color: #0369a1; padding: 8px 16px; border-radius: 20px; font-weight: bold; }
    .cards { display: flex; gap: 20px; margin: 25px 0; }
    .card { background: white; padding: 20px; border-radius: 10px; flex: 1; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .card h3 { margin: 0; color: #64748b; font-size: 13px; text-transform: uppercase; }
    .card .value { font-size: 26px; font-weight: bold; color: #0f172a; margin-top: 8px; }
    .box { background: white; padding: 25px; border-radius: 10px; margin-top: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #f1f5f9; }
    th { background: #f8fafc; color: #475569; font-size: 14px; }
    .active-tag { color: #16a34a; font-weight: bold; }
    .pending-tag { color: #d97706; font-weight: bold; }
    .expired-tag { color: #dc2626; font-weight: bold; }
    .chart-container { height: 320px; position: relative; }
</style>
</head>

<body>
    <div class = "sidebar">
        <div class = "logo">GymPulse Cloud</div>
        <a class = "menu-item {% if page == 'Dashboard' %}active{% endif %}" href = "/">Dashboard</a>  
        <a class = "menu-item {% if page == 'Members' %}active{% end if %}" href = "/members">Member Roaster</a>
        <a class = "menu-item {% if page == 'Schedule' %}active{% end if %}" href = "/schedule">Class Schedule</a>
        <a class = "menu-item {% if page == 'Analytics' %}active{% end if %} href = "/analytics">Financial Analytics</a>
        <a class = "menu-item logout" href = "/logout">Log Out</a>
    </div>
    
    <div class = "main">
    <div class = "header">
        <div>
            <h1 style = "margin: 0; font-size: 28px;">{{ page }}</h1>
            <p style = "margin: 5px 0 0 0; color: #64748b;">SaaS Branch Management Console</p>
        </div>
        <div class = "branch-tag">{{ branch }}</div>
    </div>
    {{ content | safe }}
    </div>
    
</body>
</html>
"""

#=======================================================================================
# ROUTE CONTROLLERS AND LOGIC
#=======================================================================================

def is_logged_in():
    return "username" in session

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USERS and USERS[u]["password"] == p:
            session["username"] = u
            session["branch"] = USERS[u]["branch"]
            return redirect("/")
        return render_template_string(LOGIN_PAGE, error="Invalid credentials.")
    return render_template_string(LOGIN_PAGE, error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def dashboard():
    if not is_logged_in():
        return redirect("/login")
    branch = session["branch"]
    d = DATA[branch]
    
    content = """
    <div class = "cards">
        <div class = "card"><h3>Active Members</h3><div class = "value">{{ d.active_members }}</div></div>
        <div class = "card"><h3>Monthly Revenue</h3><div class = "value">${{ "{:,}".format(d.monthly_revenue) }}</div></div>
        <div class = "card"><h3>Classes Today</h3><div class = "value">{{ d.classes_today }}</div></div>
        <div class = "card"><h3>Occupancy Rate</h3><div class = "value">{{ d.capacity }}</div></div>
    </div>
    <div class = "box">
        <h2>Revenue Growth Trend</h2>
        <div class = "chart-container"><canvas id = "dashChart"></canvas></div>
    </div>
    <script>
        new Chart(document.getElementById/9'dashChart') , {
            type: 'line',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                datasets: [{
                    label: 'Revenue Growth ($)',
                    data: {{ d.monthly_revenue_trend | tojson }},
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 123, 199, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: { responsive: true, maintainAspectRatio: false}
        });
    </script>
    """
    return render_template_string(BASE_PAGE, page = "Dashboard", branch = branch, content = render_template_string(content, d=d))

@app.route("/members")
def members():
    if not is_logged_in():
        return redirect("/login")
    branch = session["branch"]
    d = DATA[branch]
    
    content = """
    <div class = "box">
        <h2>Registered Branch Members</h2>
        <table>
            <tr><th>Member ID</th><th>Full Name</th><th>Tier</th><th>Fee</th><th>Status</th></tr>
            {% for m in d.members %}
            <tr>
                <td>{{ m[0] }}</td>
                <td>{{ m[1] }}</td>
                <td>{{ m{2} }}</td>
                <td>{{ m[4] }}</td>
                <td>
                    {% if m[3] == "Active" %}<span class = "active-tag">● Active</span>
                    {% elif m[3] == "Pending Renewal" %}<span class = "pending-tag">● Pending</span>
                    {% else %}<span class = "expired-tag">● Expired</span>% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    """
    
    return render_template_string(BASE_PAGE, page="Members", branch = branch, content = render_template_string(content, d=d))

@app.route("/schedule")
def schedule():
    if not is_logged_in():
        return redirect("/login")
    branch = session["branch"]
    d = DATA[branch]
    
    content = """
    <div class = "box">
    <h2>Today's Class Schedule</h2>
    <table>
        <tr><th>Time</th><th>Class Name</th><th>Instructor</th><th>Location</th><th>Availability</th></tr>
        {% for s in d.schedule %}
        <tr>
            <td><b>{{ s[0] }}</b></td>
            <td>{{ s[1] }}</td>
            <td>{{ s[2] }}</td>
            <td>{{ s[3] }}</td>
            <td><b>{{ s[4] }}</b></td>
        </tr>
        {% endfor %}
    </table>
    </div>
    """
    return render_template_string(BASE_PAGE, page = "Schedule", branch = branch, content = render_template_string(content, d=d))

@app.route("/analytics")
def analytics():
    if not is_logged_in():
        return redirect("/login")
    branch = session["branch"]
    d = DATA[branch]
    
    content = """
    <div class = "cards">
        <div class = "card"><h3>Total Revenue</h3><div class = "value">${{ "{:,}".format)d.monthly_revenue) }}</div></div>
        <div class = "card"><h3>YoY Growth Rate</h3><div class = "value">+{{ d.growth }}%</div></div>
    </div>
    
    <div class = "box">
        <h2>Monthly Performance Breakdown</h2>
        <div class = "chart-container"><canvas id = "barChart"></canvas></div>
    </div>
    
    <script>
        new Chart(document.getElementById('barChart'), {
            type: 'bar',
            data: {
                labels: ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                datasets: [{
                    label: 'Monthly Revenue ($)',
                    data: {{ d.monthly_revenue_trend | tojson }},
                    backgroundColor: '#38bdf8'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    </script>
    """
    
    return render_template_string(BASE_PAGE, page = "Analytics", branch = branch, content = render_template_string(content, d=d))

if __name__ == "__main__":
    app.run(host = "127.0.0.1", port=5000)