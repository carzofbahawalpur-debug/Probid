# UET Lahore Project Portal - Rectified and Enhanced Version

import json
import os
os.chdir(r'C:\Users\mubas\OneDrive\Desktop\PF PROJECT DATA')

print("This script is running in:", os.getcwd())
input("Press Enter to continue...") # This pauses the script so you can see the output
import random
import string
import time
from datetime import datetime, timedelta
from colorama import init, Fore, Style, Back

# Initialize colorama
init(autoreset=True)

# --- Localization and Branding ---
PROJECT_TITLE = "UET Lahore Project Portal"
WELCOME_MESSAGE = "Welcome to the official UET Lahore Project Portal for students and vendors."

# Color definitions with enhanced combinations
INFO = Fore.CYAN
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARN = Fore.YELLOW
TITLE = Fore.MAGENTA + Style.BRIGHT
HIGHLIGHT = Back.BLUE + Fore.WHITE
RESET = Style.RESET_ALL

# Files
USER_FILE = "users.json"
PROPOSAL_FILE = "proposals.json"
BID_FILE = "bids.json"
PROJECT_FILE = "projects.json"
LOG_FILE = "system_log.txt"
NOTIFICATION_FILE = "notifications.json"

# --- VISUAL ENHANCEMENT FUNCTIONS ---
def print_banner(title, subtitle=""):
    """Print a fancy banner with title and optional subtitle"""
    width = 70
    print(HIGHLIGHT + " " * width + RESET)
    print(TITLE + f"{title.center(width)}" + RESET)
    if subtitle:
        print(INFO + f"{subtitle.center(width)}" + RESET)
    print(HIGHLIGHT + " " * width + RESET)
    print()

def print_section(title):
    """Print a section header"""
    print("\n" + Fore.BLUE + Style.BRIGHT + f"--- {title.upper()} ---" + RESET)

def display(msg, t="info"):
    """Display a message with appropriate color and formatting"""
    color = INFO
    if t == "success": color = SUCCESS
    elif t == "error": color = ERROR
    elif t == "warn": color = WARN
    elif t == "title": color = TITLE
    
    # Add some visual flair based on message type
    if t == "error":
        print(f"❌ {color}{msg}{RESET}")
    elif t == "success":
        print(f"✅ {color}{msg}{RESET}")
    elif t == "warn":
        print(f"⚠️  {color}{msg}{RESET}")
    else:
        print(f"{color}{msg}{RESET}")

# --- CORE SYSTEM FUNCTIONS ---
def log_action(action):
    """Logs actions to a file for auditing."""
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {action}\n")

# --- Input Validation Functions ---
def validate_password(password):
    """Validate password complexity"""
    if len(password) < 8: return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    return has_upper and has_lower and has_digit and has_symbol

def validate_email(email):
    """Validate email format"""
    if '@' not in email or email.count('@') != 1: return False
    return '.' in email.split('@')[1]

# --- Data Handling Functions ---
def load_json(file, default):
    """Load JSON data from file with error handling"""
    if not os.path.exists(file):
        save_json(file, default)
        return default
    try:
        with open(file, "r") as f:
            data = json.load(f)
            if file == USER_FILE:
                for role in ["admins", "vendor", "freelancer"]:
                    if role not in data: data[role] = {}
                    for username, details in data.get(role, {}).items():
                        if isinstance(details, str):
                            data[role][username] = {"password": details, "email": "", "rating": 0, "score": 0}
                        elif "rating" not in details: data[role][username]["rating"] = 0
                        elif "score" not in details: data[role][username]["score"] = 0
                save_json(file, data)
            if isinstance(default, dict):
                for key, value in default.items():
                    if key not in data:
                        data[key] = value
                        save_json(file, data)
            return data
    except (json.JSONDecodeError, Exception) as e:
        display(f"Error loading {file}. Using default data. Error: {e}", "error")
        if os.path.exists(file): os.rename(file, f"{file}.bak")
        save_json(file, default)
        return default

def save_json(file, data):
    """Save data to JSON file"""
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def input_str(msg, allow_empty=False):
    """Get string input with validation"""
    while True:
        v = input(msg).strip()
        if not allow_empty and v == "":
            display("This field cannot be empty.", "error")
        else:
            return v

def input_int(msg):
    """Get integer input with validation"""
    while True:
        try:
            return int(input(msg))
        except ValueError:
            display("Invalid integer input.", "error")

def input_float(msg):
    """Get float input with validation"""
    while True:
        try:
            return float(input(msg))
        except ValueError:
            display("Invalid numeric input.", "error")

def input_choice(msg, choices):
    """Get input from a list of choices - kept for non-menu uses"""
    while True:
        v = input(msg).lower()
        if v in choices:
            return v
        display(f"Invalid choice. Please select from: {', '.join(choices)}", "error")

# --- Data Initialization ---
users = load_json(USER_FILE, {"admins": {}, "vendor": {}, "freelancer": {}})
projects = load_json(PROJECT_FILE, [])
bids = load_json(BID_FILE, [])
notifications = load_json(NOTIFICATION_FILE, {})

# --- User Authentication Functions ---
def find_user(username):
    """Find a user by username and return their role and data"""
    for role, role_data in users.items():
        if username in role_data:
            return role, role_data[username]
    return None, None

def otp_check():
    """Simulate OTP verification with visual feedback (Simplified)"""
    otp = random.randint(1000, 9999)
    display(f"Your OTP is: {otp}", "warn")
    
    user_otp = input_str("Enter OTP: ")
    if user_otp == str(otp):
        display("OTP verified successfully!", "success")
        return True
    else:
        display("Invalid OTP. Please try again.", "error")
        return False

def create_account():
    """Create a new user account"""
    print_section("Create New Account")
    role = input_choice("Role (admins/vendor/freelancer): ", ["admins", "vendor", "freelancer"])
    username = input_str("Choose a Username: ")
    user_store = users[role]
    if username in user_store:
        display(f"Username '{username}' is already taken.", "error")
        return
    while True:
        email = input_str("Enter your Email Address: ")
        if validate_email(email): break
        display("Invalid email format.", "error")
        
    display("Password Requirements:", "warn")
    display("- At least 8 characters, 1 upper, 1 lower, 1 number, 1 symbol")
    while True:
        password = input_str("Enter your Password: ", allow_empty=True)
        if validate_password(password): break
        display("Password does not meet requirements.", "error")
    
    user_store[username] = {"password": password, "email": email, "rating": 0, "score": 0, "created_at": str(datetime.now())}
    save_json(USER_FILE, users)
    log_action(f"New account created: {role} '{username}'")
    display(f"Account for '{username}' created successfully!", "success")

def forgot_password():
    """Recover forgotten password"""
    print_section("Password Recovery")
    recovery_email = input_str("Enter the email address associated with your account: ")
    for role, role_data in users.items():
        for username, details in role_data.items():
            if details.get("email") == recovery_email:
                password = details["password"]
                display("Account found!", "success")
                display(f"Username: {username}")
                display(f"Password: {password}")
                log_action(f"Password recovered for user '{username}'.")
                return
    display("No account found with that email address.", "error")

def delete_account(username, role):
    """Delete user account"""
    print_section("Delete Account")
    display("WARNING: This action is irreversible.", "warn")
    if input_choice(f"Are you sure you want to delete your account '{username}'? (yes/no): ", ["yes", "no"]) != "yes":
        display("Account deletion cancelled.", "info")
        return
    if role == "admins" and len(users["admins"]) == 1:
        display("Cannot delete the only admins account.", "error")
        return
    del users[role][username]
    save_json(USER_FILE, users)
    log_action(f"Account '{username}' ({role}) deleted by user.")
    display("Your account has been deleted successfully.", "success")
    return "logout"

def change_password(username, role):
    """Change user password"""
    print_section("Change Password")
    old_pwd = input_str("Enter your current password: ")
    if users[role][username]["password"] != old_pwd:
        display("Incorrect current password.", "error")
        return
    display("Enter new password (must meet requirements):", "warn")
    while True:
        new_pwd = input_str("New Password: ", allow_empty=True)
        if validate_password(new_pwd): break
        display("Password does not meet requirements.", "error")
    users[role][username]["password"] = new_pwd
    save_json(USER_FILE, users)
    log_action(f"Password changed for user '{username}'.")
    display("Password changed successfully!", "success")

# --- Project and Proposal Functions ---
def create_project():
    """Create a new project"""
    print_section("Create New Project")
    title = input_str("Project Title: ")
    desc = input_str("Project Description: ")
    budget = input_float("Project Budget (PKR): ")
    min_bid = input_float("Minimum Bid Amount (PKR): ")
    days = input_float("Deadline (in days): ")
    project = {
        "id": len(projects) + 1, "title": title, "desc": desc, "budget": budget,
        "min_bid": min_bid, "created": str(datetime.now()),
        "deadline": str(datetime.now() + timedelta(days=days)), "status": "OPEN", "assigned_to": None
    }
    projects.append(project)
    save_json(PROJECT_FILE, projects)
    log_action(f"Project created: {title}")
    display("Project posted successfully.", "success")

def view_projects(filter_status="all"):
    """View projects with optional status filter"""
    filtered_projects = projects if filter_status == "all" else [p for p in projects if p["status"] == filter_status]
    if not filtered_projects:
        display("No projects found with the current filter.", "warn")
        return
    print_section(f"Projects (Status: {filter_status.upper()})")
    for p in filtered_projects:
        status_color = SUCCESS if p["status"] == "OPEN" else WARN
        print(f"ID: {p['id']} | Title: {p['title']} | Budget: {p['budget']} PKR | Status: {status_color}{p['status']}{RESET}")

def close_project():
    """Close a project and assign to winning bidder"""
    view_projects("open")
    if not any(p["status"] == "OPEN" for p in projects): return
    pid = input_int("Enter Project ID to close: ")
    project = next((p for p in projects if p["id"] == pid), None)
    if not project or project["status"] != "OPEN":
        display("Invalid or already closed project ID.", "error")
        return
    project_bids = [b for b in bids if b["project_id"] == pid]
    if not project_bids:
        display("No bids for this project. Closing without assigning.", "warn")
        project["status"] = "CLOSED"
        save_json(PROJECT_FILE, projects)
        return
    valid_bids = [b for b in project_bids if b["amount"] >= project["min_bid"]]
    if not valid_bids:
        display("No valid bids. Closing project.", "warn")
        project["status"] = "CLOSED"
        save_json(PROJECT_FILE, projects)
        return
    sorted_bids = sorted(valid_bids, key=lambda x: (x["amount"], x["delivery_days"], -users[x["vendor_role"]][x["vendor"]].get("score", 0)))
    winning_bid = sorted_bids[0]
    winner = winning_bid["vendor"]
    project["status"] = "CLOSED"
    project["assigned_to"] = winner
    project["winning_bid"] = winning_bid["amount"]
    if winner not in notifications: notifications[winner] = []
    notifications[winner].append(f"Congratulations! You won the bid for project '{project['title']}'.")
    save_json(NOTIFICATION_FILE, notifications)
    display(f"\nProject awarded to {winner}!", "success")
    rating = input_int(f"Please rate {winner}'s performance (1-5): ")
    user_role, user_data = find_user(winner)
    if user_role and 1 <= rating <= 5:
        current_rating = users[user_role][winner].get("rating", 0)
        users[user_role][winner]["rating"] = rating if current_rating == 0 else (current_rating + rating) / 2
        users[user_role][winner]["score"] += 10
        save_json(USER_FILE, users)
    save_json(PROJECT_FILE, projects)
    log_action(f"Project {pid} awarded to {winner}")

def edit_project():
    """Edit an existing project"""
    view_projects("open")
    pid = input_int("Enter Project ID to edit: ")
    project = next((p for p in projects if p["id"] == pid and p["status"] == "OPEN"), None)
    if not project:
        display("Invalid project ID or project cannot be edited.", "error")
        return
    print_section(f"Editing project: {project['title']}")
    new_title = input_str(f"New Title [{project['title']}]: ", allow_empty=True)
    if new_title: project['title'] = new_title
    new_desc = input_str(f"New Description [{project['desc']}]: ", allow_empty=True)
    if new_desc: project['desc'] = new_desc
    new_budget = input_str(f"New Budget [{project['budget']}]: ", allow_empty=True)
    if new_budget:
        try: project['budget'] = float(new_budget)
        except: display("Invalid budget value. Keeping original.", "error")
    new_min_bid = input_str(f"New Min Bid [{project['min_bid']}]: ", allow_empty=True)
    if new_min_bid:
        try: project['min_bid'] = float(new_min_bid)
        except: display("Invalid minimum bid value. Keeping original.", "error")
    save_json(PROJECT_FILE, projects)
    log_action(f"Project {pid} edited.")
    display("Project updated successfully.", "success")

# --- Bidding Functions ---

def submit_bid(user_name, user_role):
    """Submit a bid for a project (ROBUST VERSION)"""
    # First, check if there are any open projects at all
    open_projects = [p for p in projects if p["status"] == "OPEN"]
    if not open_projects:
        display("There are no open projects to bid on at the moment.", "warn")
        return

    print_section("Open Projects Available for Bidding")
    for p in open_projects:
        print(f"ID: {p['id']} | Title: {p['title']} | Budget: {p['budget']} PKR | Min Bid: {p['min_bid']} PKR")
    
    pid = input_int("Enter Project ID to bid on: ")
    project = next((p for p in open_projects if p["id"] == pid), None)
    
    if not project:
        display("Invalid project ID. Please choose from the list above.", "error")
        return
        
    # --- ROBUST BID CHECK ---
    # Safely check for existing bids without crashing on corrupted data
    existing_bid = None
    for b in bids:
        # Ensure the bid dictionary has the necessary keys before trying to use them
        if "project_id" in b and "vendor" in b:
            if b["project_id"] == pid and b["vendor"] == user_name:
                existing_bid = b
                break
    
    if existing_bid:
        display("You have already bid on this project.", "warn")
        if input_choice("Update your bid? (y/n): ", ["y", "n"]) != "y": 
            return
        # Safely remove the old bid
        try:
            bids.remove(existing_bid)
        except ValueError:
            display("Warning: Could not remove old bid, but you can still submit a new one.", "warn")
        
    print_section(f"Bidding on: {project['title']} (Min Bid: {project['min_bid']} PKR)")
    amount = input_float(f"Your Bid Amount (PKR): ")
    if amount < project["min_bid"]:
        display(f"Your bid must be at least {project['min_bid']} PKR.", "error")
        return
    days = input_float("Your Delivery Time (in days): ")
    bid = {"project_id": pid, "vendor": user_name, "vendor_role": user_role, "amount": amount, "delivery_days": days, "bid_time": str(datetime.now())}
    bids.append(bid)
    save_json(BID_FILE, bids)
    log_action(f"Bid submitted by {user_name} on project {pid}")
    display("Bid submitted successfully.", "success")





def view_my_bids(user_name):
    """View all bids submitted by the user"""
    my_bids = [b for b in bids if b["vendor"] == user_name]
    if not my_bids:
        display("You haven't placed any bids yet.", "warn")
        return
    print_section("Your Bids")
    for b in my_bids:
        project = next((p for p in projects if p["id"] == b["project_id"]), None)
        project_title = project["title"] if project else "Unknown Project"
        project_status = project["status"] if project else "Unknown"
        status_color = SUCCESS if project_status == "OPEN" else WARN
        print(f"Project: {project_title} | Amount: {b['amount']} PKR | Status: {status_color}{project_status}{RESET}")

def view_my_won_projects(user_name):
    """View all projects won by the user"""
    won_projects = [p for p in projects if p.get("assigned_to") == user_name]
    if not won_projects:
        display("You haven't won any projects yet.", "warn")
        return
    print_section("Your Won Projects")
    for p in won_projects:
        print(f"Title: {p['title']} | Winning Bid: {p.get('winning_bid', 'N/A')} PKR")

def view_project_bids():
    """View all bids for a specific project"""
    view_projects("open")
    pid = input_int("Enter Project ID to view bids for: ")
    project_bids = [b for b in bids if b["project_id"] == pid]
    if not project_bids:
        display("No bids for this project.", "warn")
        return
    print_section(f"Bids for Project ID {pid}")
    for b in project_bids:
        user_role, user_data = find_user(b["vendor"])
        rating = user_data.get("rating", 0) if user_data else 0
        score = user_data.get("score", 0) if user_data else 0
        print(f"Vendor: {b['vendor']} | Amount: {b['amount']} PKR | Delivery: {b['delivery_days']} days | Rating: {rating:.1f}/5 | Score: {score}")

def export_data():
    """Export system data to a text file"""
    print_section("Export Data")
    choice = input_choice("Export (users/projects/bids)? ", ["users", "projects", "bids"])
    filename = f"export_{choice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    data_to_export = []
    if choice == "users":
        for role, role_data in users.items():
            for user, details in role_data.items():
                data_to_export.append(f"Role: {role}, User: {user}, Email: {details.get('email')}, Rating: {details.get('rating')}, Score: {details.get('score')}")
    elif choice == "projects":
        for p in projects:
            data_to_export.append(f"ID: {p['id']}, Title: {p['title']}, Status: {p['status']}, Assigned To: {p.get('assigned_to', 'N/A')}")
    elif choice == "bids":
        for b in bids:
            data_to_export.append(f"Project ID: {b['project_id']}, Vendor: {b['vendor']}, Amount: {b['amount']}, Delivery: {b['delivery_days']}")
    with open(filename, "w") as f:
        f.write("\n".join(data_to_export))
    log_action(f"Data exported to {filename}")
    display(f"Data successfully exported to {filename}", "success")

# --- Analytics and Menus ---
def analytics():
    """Display system analytics"""
    print_section("System Analytics")
    total_budget_open = sum(p['budget'] for p in projects if p['status'] == 'OPEN')
    avg_bid = sum(b['amount'] for b in bids) / len(bids) if bids else 0
    print(f"Total Projects: {len(projects)} | Open: {sum(1 for p in projects if p['status'] == 'OPEN')} | Closed: {sum(1 for p in projects if p['status'] == 'CLOSED')}")
    print(f"Total Budget of Open Projects: {total_budget_open} PKR")
    print(f"Total Bids: {len(bids)} | Average Bid Amount: {avg_bid:.2f} PKR")
    print(f"Total Users: {len(users['admins'])} Admins, {len(users['vendor'])} Vendors, {len(users['freelancer'])} Freelancers")

def view_profile(username, role):
    """View user profile"""
    user_data = users[role][username]
    score = user_data.get("score", 0)
    print_section("My Profile")
    print(f"Username: {username}")
    print(f"Role: {role.capitalize()}")
    print(f"Email: {user_data.get('email')}")
    print(f"Rating: {user_data.get('rating', 0):.1f}/5")
    if role != "admins": print(f"Score: {score}")
    print(f"Member Since: {user_data.get('created_at', 'Unknown')}")

def view_notifications(username):
    """View user notifications"""
    user_notifs = notifications.get(username, [])
    if not user_notifs:
        display("You have no new notifications.", "info")
        return
    print_section("Your Notifications")
    for notif in user_notifs: print(f"- {notif}")
    notifications[username] = []
    save_json(NOTIFICATION_FILE, notifications)

# --- Login Function (RECTIFIED) ---
def login():
    """Main login function with corrected logic flow."""
    while True:
        print_banner(PROJECT_TITLE, WELCOME_MESSAGE)
        print_section("Main Menu")
        print("1. Login")
        print("2. Create Account")
        print("3. Guest View")
        print("4. Forgot Password")
        print("5. Exit")
        
        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 5:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 5.", "error")
            continue

        if choice == "1":
            print_section("Login")
            username = input_str("Username: ")
            pwd = input_str("Password: ")
            
            role, user_data = find_user(username)
            
            if not role:
                display("Account does not exist.", "error")
                continue
            
            if user_data.get("password") != pwd:
                display("Wrong password entered.", "error")
                if input_choice("Forgot Password? (y/n): ", ["y", "n"]) == "y":
                    forgot_password()
                continue
            
            if otp_check():
                if role == "admins": admin_menu(username)
                elif role == "vendor": vendor_menu(username)
                elif role == "freelancer": freelancer_menu(username)
                    
        elif choice == "2": create_account()
        elif choice == "3": guest_menu()
        elif choice == "4": forgot_password()
        elif choice == "5":
            display("Exiting system. Goodbye!", "success")
            break

# --- MENUS WITH RECTIFIED INPUT LOGIC ---
def admin_menu(name):
    """admins menu"""
    while True:
        print_banner(f"admins Panel - {name}")
        print_section("admins Options")
        print("1. User Management 2. Create Project 3. View/Edit Projects 4. Close Project")
        print("5. View Bids 6. Analytics 7. Export Data 8. My Profile 9. Change Password")
        print("10. Delete Account 11. Logout")
        
        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 11:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 11.", "error")
            continue

        if choice == "1": manage_users(name)
        elif choice == "2": create_project()
        elif choice == "3":
            sub_choice = input_choice("View Projects (v) or Edit Project (e)? ", ["v", "e"])
            if sub_choice == 'v': view_projects("all")
            elif sub_choice == 'e': edit_project()
        elif choice == "4": close_project()
        elif choice == "5": view_project_bids()
        elif choice == "6": analytics()
        elif choice == "7": export_data()
        elif choice == "8": view_profile(name, "admins")
        elif choice == "9": change_password(name, "admins")
        elif choice == "10":
            if delete_account(name, "admins") == "logout": break
        elif choice == "11": break

def vendor_menu(name):
    """Vendor menu"""
    while True:
        print_banner(f"Vendor Panel - {name}")
        print_section("Vendor Options")
        print("1. View Projects 2. Submit Bid 3. My Bids 4. Won Projects 5. My Score")
        print("6. My Profile 7. Notifications 8. Change Password 9. Delete Account 10. Logout")

        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 10:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 10.", "error")
            continue

        if choice == "1": view_projects("open")
        elif choice == "2": submit_bid(name, "vendor")
        elif choice == "3": view_my_bids(name)
        elif choice == "4": view_my_won_projects(name)
        elif choice == "5":
            score = users["vendor"][name].get("score", 0)
            display(f"Your current score: {score}", "success")
        elif choice == "6": view_profile(name, "vendor")
        elif choice == "7": view_notifications(name)
        elif choice == "8": change_password(name, "vendor")
        elif choice == "9":
            if delete_account(name, "vendor") == "logout": break
        elif choice == "10": break

def freelancer_menu(name):
    """Freelancer menu"""
    while True:
        print_banner(f"Freelancer Panel - {name}")
        print_section("Freelancer Options")
        print("1. View Projects 2. Submit Bid 3. My Bids 4. Won Projects 5. My Score")
        print("6. My Profile 7. Notifications 8. Change Password 9. Delete Account 10. Logout")

        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 10:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 10.", "error")
            continue

        if choice == "1": view_projects("open")
        elif choice == "2": submit_bid(name, "freelancer")
        elif choice == "3": view_my_bids(name)
        elif choice == "4": view_my_won_projects(name)
        elif choice == "5":
            score = users["freelancer"][name].get("score", 0)
            display(f"Your current score: {score}", "success")
        elif choice == "6": view_profile(name, "freelancer")
        elif choice == "7": view_notifications(name)
        elif choice == "8": change_password(name, "freelancer")
        elif choice == "9":
            if delete_account(name, "freelancer") == "logout": break
        elif choice == "10": break

def guest_menu():
    """Guest menu"""
    while True:
        print_banner("Guest View")
        print_section("Guest Options")
        print("1. View Open Projects 2. Exit to Main Menu")
        
        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 2:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 2.", "error")
            continue

        if choice == "1": view_projects("open")
        elif choice == "2": break

def manage_users(admin_name):
    """User management for admins"""
    while True:
        print_section("User Management")
        print("1. View All Users 2. Delete User 3. Back")
        
        choice_str = input("Choice: ")
        if choice_str.isdigit() and 1 <= int(choice_str) <= 3:
            choice = choice_str
        else:
            display("Invalid choice. Please enter a number between 1 and 3.", "error")
            continue

        if choice == "1":
            print_section("All Users")
            for role, role_data in users.items():
                print(f"\n--- {role.upper()}S ---")
                for user, details in role_data.items():
                    score = details.get("score", 0)
                    print(f"User: {user}, Email: {details.get('email')}, Rating: {details.get('rating',0):.1f}, Score: {score}")
        elif choice == "2":
            username_to_delete = input_str("Username to delete: ")
            role_to_delete, _ = find_user(username_to_delete)
            if not role_to_delete:
                display("User not found.", "error")
                continue
            if username_to_delete == admin_name:
                display("Cannot delete your own account from here.", "error")
                continue
            del users[role_to_delete][username_to_delete]
            save_json(USER_FILE, users)
            log_action(f"User '{username_to_delete}' deleted by admins '{admin_name}'.")
            display(f"User '{username_to_delete}' deleted.", "success")
        elif choice == "3": break

#ADDED FLASK API INTEGRATION

if __name__ == "__main__":
    login()