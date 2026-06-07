# Import the tools we need
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import string
from datetime import datetime, timedelta # <-- ADD timedelta
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return "ProBid API is running successfully!"
@app.route("/api/test")
def test():
    return jsonify({
        "message": "Backend Connected Successfully"
    })

if __name__ == "__main__":
    app.run()    

# --- Helper Functions from your original script ---
def find_user(username):
    # We added a try-except block here to catch errors
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        print("ERROR: users.json not found! Make sure it's in the same folder as api.py")
        return None, None
    except json.JSONDecodeError:
        print("ERROR: users.json is not a valid JSON file. Check for typos.")
        return None, None

    for role, role_data in users.items():
        if username in role_data:
            return role, role_data[username]
    return None, None

# --- Our Buttons (Routes) ---

@app.route('/hello')
def say_hello():
    return "Hello from your Python API!"

@app.route('/projects')
def get_projects():
    with open('projects.json', 'r') as f:
        project_data = json.load(f)
    return jsonify(project_data)

# --- THE LOGIN BUTTON ---
@app.route('/api/login', methods=['POST'])
def login():
    print("--- Login Attempt ---") # This will print in the terminal
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        print(f"Username: {username}, Password: [hidden]")

        role, user_data = find_user(username)

        if not role or user_data.get('password') != password:
            print("Login Failed: Invalid credentials.")
            return jsonify({"success": False, "message": "Invalid username or password."}), 401

        # Login successful!
        print(f"Login Success! Welcome, {role} {username}.")
        return jsonify({
            "success": True,
            "user": {
                "username": username,
                "role": role,
                "email": user_data.get("email"),
                "rating": user_data.get("rating", 0),
                "score": user_data.get("score", 0)
            }
        })
    except Exception as e:
        # This will catch ANY other error and print it
        print(f"An unexpected error occurred: {e}")
        return jsonify({"success": False, "message": "A server error occurred."}), 500

# --- THE NEW "MY BIDS" BUTTON ---
# --- UPDATED MY BIDS FUNCTION (Includes Status) ---
@app.route('/api/my-bids/<username>')
def get_my_bids(username):
    print(f"--- Requesting bids for user: {username} ---")
    try:
        with open('bids.json', 'r') as f:
            all_bids = json.load(f)
        
        with open('projects.json', 'r') as f:
            all_projects = json.load(f)

        # Filter bids AND add project status
        my_enriched_bids = []
        for bid in all_bids:
            if bid['vendor'] == username:
                # Find matching project to get status
                bid_status = "UNKNOWN"
                for p in all_projects:
                    if p['id'] == bid['project_id']:
                        bid_status = p['status']
                        break
                
                # Add status to the bid object
                bid['project_status'] = bid_status
                my_enriched_bids.append(bid)
        
        print(f"Found {len(my_enriched_bids)} bids for {username}.")
        return jsonify(my_enriched_bids)
    except FileNotFoundError:
        return jsonify({"error": "Bids file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# --- THE NEW "CREATE PROJECT" BUTTON ---
@app.route('/api/projects', methods=['POST'])
def create_project():
    print("--- New Project Creation ---")
    try:
        data = request.get_json()
        title = data.get('title')
        desc = data.get('description')
        budget = data.get('budget')
        min_bid = data.get('minBid')

        # Basic validation
        if not all([title, desc, budget, min_bid]):
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Load existing projects to find the next ID
        with open('projects.json', 'r') as f:
            projects = json.load(f)
        
        # Find the highest existing ID and add 1
        max_id = 0
        for p in projects:
            if p['id'] > max_id:
                max_id = p['id']
        new_id = max_id + 1

        # Create the new project object
        new_project = {
            "id": new_id,
            "title": title,
            "desc": desc,
            "budget": float(budget),
            "min_bid": float(min_bid),
            "created": str(datetime.now()),
            "deadline": str(datetime.now() + timedelta(days=30)), # Default 30-day deadline
            "status": "OPEN",
            "assigned_to": None
        }
        
        projects.append(new_project)

        # Save the updated projects back to the file
        with open('projects.json', 'w') as f:
            json.dump(projects, f, indent=4)

        print(f"Success! New project '{title}' created with ID {new_id}.")
        return jsonify({"success": True, "message": "Project created successfully!", "project": new_project})

    except Exception as e:
        print(f"Error creating project: {e}")
        return jsonify({"success": False, "message": "Server error during project creation."}), 500

# --- THE NEW USER PROFILE BUTTON ---
@app.route('/api/user/<username>')
def get_user_profile(username):
    print(f"--- Requesting profile for user: {username} ---")
    role, user_data = find_user(username)
    
    if not role or not user_data:
        return jsonify({"error": "User not found."}), 404
        
    # Return the user's data along with their role
    profile_data = user_data.copy()
    profile_data['role'] = role
    return jsonify(profile_data)

@app.route('/api/my-earnings/<username>')
def get_my_earnings(username):
    try:
        with open('projects.json', 'r') as f:
            projects = json.load(f)
        
        # Find all projects assigned to the user
        won_projects = [p for p in projects if p.get('assigned_to') == username]
        
        total_earnings = sum(p.get('winning_bid', 0) for p in won_projects)
        
        return jsonify({
            "won_projects": len(won_projects),
            "total_earnings": total_earnings,
            "projects": won_projects
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# --- Add these validation functions at the top of api.py ---

def validate_password(password):
    """Validate password complexity based on your policy."""
    if len(password) < 8: return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    return has_upper and has_lower and has_digit and has_symbol

def validate_email(email):
    """Validate email format."""
    if '@' not in email or email.count('@') != 1: return False
    return '.' in email.split('@')[1]

def find_user_all_roles(username, users):
    """Search for a username across all role sections."""
    for role_key in users:
        if username in users[role_key]:
            return role_key, users[role_key][username]
    return None, None

# --- THE NEW "REGISTER ACCOUNT" BUTTON ---
@app.route('/api/register', methods=['POST'])
def register():
    print("--- New Registration Attempt ---")
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role') # Should be 'admin', 'vendor', or 'freelancer'

        # --- Server-Side Validation ---
        if not all([username, password, email, role]):
            return jsonify({"success": False, "message": "All fields are required."}), 400
        
        if not validate_email(email):
            return jsonify({"success": False, "message": "Invalid email format."}), 400

        if not validate_password(password):
            return jsonify({"success": False, "message": "Password must be at least 8 characters long and contain an uppercase letter, a lowercase letter, a number, and a symbol."}), 400

        # --- Check for Existing Username ---
        with open('users.json', 'r') as f:
            users = json.load(f)
        
        existing_role, _ = find_user_all_roles(username, users)
        if existing_role:
            return jsonify({"success": False, "message": "Username already exists."}), 409

        # --- Create New User ---
        # We will use the singular form for consistency with your recent data
        if role not in ['admins', 'vendor', 'freelancer']:
            return jsonify({"success": False, "message": "Invalid role specified."}), 400

        if role not in users:
            users[role] = {} # Create the role section if it doesn't exist

        users[role][username] = {
            "password": password,
            "email": email,
            "rating": 0,
            "score": 0,
            "created_at": str(datetime.now())
        }

        # --- Save the New User ---
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        print(f"Success! New user '{username}' registered with role '{role}'.")
        return jsonify({"success": True, "message": "Registration successful! Please log in."})

    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"success": False, "message": "A server error occurred."}), 500
#upper has reserved position
# --- THE MISSING ROUTE: PLACE A NEW BID ---
@app.route('/api/bids', methods=['POST'])
def place_bid():
    print("--- Placing New Bid ---")
    try:
        # 1. Get data sent from the HTML form
        data = request.get_json()
        username = data.get('username')
        project_id = data.get('project_id')
        amount = data.get('amount')
        delivery_days = data.get('delivery_days')

        # 2. Check if all fields are present
        if not all([username, project_id, amount, delivery_days]):
            return jsonify({"success": False, "message": "Missing bid details."}), 400

        # 3. Load existing bids
        try:
            with open('bids.json', 'r') as f:
                all_bids = json.load(f)
        except FileNotFoundError:
            # If file doesn't exist yet, create an empty list
            all_bids = []

        # 4. Create the new bid object
        new_bid = {
            "id": len(all_bids) + 1, # Simple ID generation
            "vendor": username,
            "project_id": int(project_id),
            "amount": float(amount),
            "delivery_days": int(delivery_days),
            "bid_time": str(datetime.now())
        }

        # 5. Add to list and save
        all_bids.append(new_bid)
        
        with open('bids.json', 'w') as f:
            json.dump(all_bids, f, indent=4)

        print(f"Success! Bid placed by {username} for Project {project_id}.")
        return jsonify({"success": True, "message": "Bid placed successfully!"})

    except Exception as e:
        print(f"Error placing bid: {e}")
        return jsonify({"success": False, "message": "Server error."}), 500
# --- UPDATE 1: Admin views all bids ---
# --- UPDATE 1: Admin views all bids (ULTIMATE FIX) ---
@app.route('/api/all-bids')
def get_all_bids():
    """Helper for Admin to see everyone's bids."""
    try:
        # 1. Load Bids
        try:
            with open('bids.json', 'r') as f:
                bids = json.load(f)
        except FileNotFoundError:
            return jsonify({"error": "bids.json file not found."}), 404
        except json.JSONDecodeError:
            return jsonify({"error": "bids.json is corrupted (invalid JSON)."}), 500

        # 2. Load Projects
        try:
            with open('projects.json', 'r') as f:
                projects = json.load(f)
        except FileNotFoundError:
            return jsonify({"error": "projects.json file not found."}), 404
        except json.JSONDecodeError:
            return jsonify({"error": "projects.json is corrupted (invalid JSON)."}), 500

        # 3. Safety Check: Ensure data is a List (Array), not Dictionary
        if not isinstance(bids, list):
            print(f"ERROR: bids.json is not a list! It is a {type(bids).__name__}. Content: {bids}")
            return jsonify({"error": "bids.json structure is wrong. Must start with [ ]. Check CMD."}), 500
        
        if not isinstance(projects, list):
            print(f"ERROR: projects.json is not a list! It is a {type(projects).__name__}. Content: {projects}")
            return jsonify({"error": "projects.json structure is wrong. Must start with [ ]. Check CMD."}), 500

        valid_bids = [] 

        # 4. Enrich bids with project titles
        for bid in bids:
            # Check if bid has project_id
            if 'project_id' not in bid:
                print(f"Skipping bad bid (no project_id): {bid}")
                continue

            bid_title = "Unknown Project"
            bid_status = "OPEN"
            
            try:
                for p in projects:
                    # Ensure project has 'id'
                    if 'id' in p and p['id'] == bid['project_id']:
                        bid_title = p.get('title', 'No Title')
                        bid_status = p.get('status', 'OPEN')
                        break
            except Exception as inner_e:
                print(f"Error matching project for bid {bid}: {inner_e}")

            # Add details to bid
            bid['project_title'] = bid_title
            bid['project_status'] = bid_status
            valid_bids.append(bid)

        return jsonify(valid_bids)

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"CRITICAL ERROR in get_all_bids: {e}")
        return jsonify({"error": str(e)}), 500
# --- UPDATE 2: Admin Accepts/Awards a Bid (FINAL SAFE VERSION) ---
@app.route('/api/award-bid', methods=['POST'])
def award_bid():
    """Admin clicks to accept a bid. This closes the project."""
    try:
        data = request.get_json()
        bid_id = data.get('bid_id')
        
        # 1. Load Bids
        try:
            with open('bids.json', 'r') as f:
                all_bids = json.load(f)
        except FileNotFoundError:
            return jsonify({"success": False, "message": "Bids file not found"}), 404
        except json.JSONDecodeError:
             return jsonify({"success": False, "message": "bids.json is corrupted"}), 500

        # 2. Find the bid (SAFE CHECK FOR 'id')
        target_bid = None
        for b in all_bids:
            # We use .get('id') so if a bid has no ID, it skips it instead of crashing
            if b.get('id') == bid_id:
                target_bid = b
                break
        
        if not target_bid:
            print(f"Bid ID {bid_id} not found in bids.json")
            return jsonify({"success": False, "message": "Bid not found"}), 404

        # 3. Load Projects
        try:
            with open('projects.json', 'r') as f:
                projects = json.load(f)
        except FileNotFoundError:
            return jsonify({"success": False, "message": "Projects file not found"}), 404
        
        # 4. Update the Project (SAFE CHECK FOR 'id')
        project_found = False
        for p in projects:
            # We use .get('id') here too
            if p.get('id') == target_bid['project_id']:
                p['status'] = 'CLOSED'
                p['assigned_to'] = target_bid['vendor']
                p['winning_bid'] = target_bid['amount']
                project_found = True
                print(f"--- PROJECT CLOSED ---")
                print(f"Project ID: {p.get('id')} awarded to {target_bid['vendor']}")
                break
        
        if not project_found:
            print(f"Project ID {target_bid['project_id']} not found in projects.json")
            return jsonify({"success": False, "message": "Project not found"}), 404

        # 5. Save updated projects
        try:
            with open('projects.json', 'w') as f:
                json.dump(projects, f, indent=4)
        except Exception as e:
            print(f"Error saving projects: {e}")
            return jsonify({"success": False, "message": "Could not save changes"}), 500

        return jsonify({"success": True, "message": "Project awarded successfully!"})

    except Exception as e:
        # This will catch any remaining unexpected errors
        print(f"CRITICAL Error awarding bid: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# --- The Power Switch ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
