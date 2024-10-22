from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# Sample data
criminal_details = [
    {'name': 'John Doe', 'crime': 'Robbery', 'trial_duration': '6 months'},
    {'name': 'Jane Smith', 'crime': 'Fraud', 'trial_duration': '1 year'},
    {'name': 'Alice Johnson', 'crime': 'Assault', 'trial_duration': '3 months'}
]

guardian_details = [
    {'name': 'Michael Doe', 'relation': 'Father', 'contact': '123-456-7890', 'criminal_name': 'John Doe'},
    {'name': 'Emily Smith', 'relation': 'Mother', 'contact': '987-654-3210', 'criminal_name': 'Jane Smith'},
    {'name': 'Robert Johnson', 'relation': 'Brother', 'contact': '555-555-5555', 'criminal_name': 'Alice Johnson'}
]

lawyer_requests = []

lawyers = {
    'Robbery': [
        {'name': 'Lawyer A', 'contact': '111-111-1111'},
        {'name': 'Lawyer B', 'contact': '222-222-2222'}
    ],
    'Fraud': [
        {'name': 'Lawyer C', 'contact': '333-333-3333'},
        {'name': 'Lawyer D', 'contact': '444-444-4444'}
    ],
    'Assault': [
        {'name': 'Lawyer E', 'contact': '555-555-5555'},
        {'name': 'Lawyer F', 'contact': '666-666-6666'}
    ]
}

users = {
    'criminal': {'username': 'criminal', 'password': 'password'},
    'guardian': {'username': 'guardian', 'password': 'password'},
    'lawyer': {'username': 'lawyer', 'password': 'password', 'requests': []}
}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    if username in users and users[username]['password'] == password:
        if role == 'criminal':
            return redirect(url_for('criminal_dashboard'))
        elif role == 'guardian':
            return redirect(url_for('guardian_dashboard'))
        elif role == 'lawyer':
            return redirect(url_for('lawyer_dashboard'))
    
    return 'Invalid credentials', 401

@app.route('/criminal_dashboard')
def criminal_dashboard():
    details = random.choice(criminal_details)
    return render_template('criminal_dashboard.html', details=details)

@app.route('/guardian_dashboard')
def guardian_dashboard():
    details = random.choice(guardian_details)
    # Ensure crime type is included in the details if needed
    criminal_info = next((c for c in criminal_details if c['name'] == details['criminal_name']), None)
    details['crime'] = criminal_info['crime'] if criminal_info else 'Unknown'
    
    return render_template('guardian_dashboard.html', details=details)

@app.route('/lawyer_dashboard')
def lawyer_dashboard():
    # If there are no requests, add some test data
    if not lawyer_requests:
        lawyer_requests.append({
            'criminal_name': 'John Doe',
            'status': 'pending'  # Default status for testing
        })
        lawyer_requests.append({
            'criminal_name': 'Jane Smith',
            'status': 'pending'  # Default status for testing
        })
        lawyer_requests.append({
            'criminal_name': 'Alice Johnson',
            'status': 'pending'  # Default status for testing
        })
    # Enrich requests with criminal details
    enriched_requests = []
    for request in lawyer_requests:
        criminal_info = next((c for c in criminal_details if c['name'] == request['criminal_name']), None)
        if criminal_info:
            request['crime'] = criminal_info['crime']
            request['trial_duration'] = criminal_info['trial_duration']
            enriched_requests.append(request)

    # Collect all unique crime types from requests to get corresponding lawyers
    crime_types = {req['crime'] for req in enriched_requests}
    all_lawyers = []
    for crime in crime_types:
        all_lawyers.extend(lawyers.get(crime, []))

    return render_template('lawyer_dashboard.html', requests=enriched_requests, lawyers=all_lawyers)


@app.route('/request_lawyer', methods=['POST'])
def request_lawyer():
    criminal_name = request.form['criminal_name']
    crime_type = request.form['crime_type']

    # Redirecting to a confirmation or selection page
    return render_template('lawyer_list.html', crime_type=crime_type, criminal_name=criminal_name, lawyers=lawyers.get(crime_type, []))

@app.route('/request_lawyer_for_criminal', methods=['POST'])
def request_lawyer_for_criminal():
    lawyer_name = request.form['lawyer_name']
    criminal_name = request.form['criminal_name']
    
    # Store the lawyer request
    lawyer_requests.append({
        'criminal_name': criminal_name,
        'lawyer_name': lawyer_name,
        'status': 'pending'
    })

    requested_message = "Lawyer requested successfully."
    details = next((c for c in criminal_details if c['name'] == criminal_name), None)
    
    return render_template('criminal_dashboard.html', details=details, message=requested_message)

@app.route('/respond_request', methods=['POST'])
def respond_request():
    action = request.form['action']
    criminal_name = request.form['criminal_name']
    
    request_to_handle = next((req for req in lawyer_requests if req['criminal_name'] == criminal_name), None)

    if request_to_handle:
        if action == 'accept':
            request_to_handle['status'] = 'accepted'
            print(f"{criminal_name}'s request has been accepted.")
        elif action == 'reject':
            request_to_handle['status'] = 'rejected'
            print(f"{criminal_name}'s request has been rejected.")

    return redirect(url_for('lawyer_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
