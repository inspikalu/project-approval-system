from shared import (
    load_json, save_json, sanitize_input, hash_password,
    USERS_FILE, SUBMISSIONS_FILE, SALT_LEGACY as SALT
)

# Note: DATA_DIR and other internal shared constants are now managed in shared.py

# --- App Logic ---
class ProjectApprovalSystemCLI:
    def __init__(self):
        self.current_user = None

    def login(self):
        print("\n--- Project Approval System Login ---")
        user = input("Username: ").strip()
        pw = input("Password: ").strip()
        
        users = load_json(USERS_FILE)
        match = next((u for u in users if u['username'] == user), None)
        
        if match:
            # Hash use the stored salt
            hashed, _ = hash_password(pw, match.get('salt', SALT))
            if match['pw'] == hashed:
                self.current_user = match
                print(f"Logged in as {match['username']} ({match['role']})")
                if match['role'] == 'student':
                    self.student_menu()
                else:
                    self.staff_menu()
                return
        
        print("Error: Invalid credentials.")

    def student_menu(self):
        while True:
            print(f"\n--- Student Menu ({self.current_user['username']}) ---")
            print("1. Submit Project Topic")
            print("2. Submit Background of Study")
            print("3. View My Submissions")
            print("4. Logout")
            choice = input("Choice: ")
            
            if choice in ['1', '2']:
                sub_type = "Topic" if choice == '1' else "Background"
                content = sanitize_input(input(f"Enter {sub_type} content: "))
                if content:
                    subs = load_json(SUBMISSIONS_FILE)
                    subs.append({
                        "id": len(subs) + 1,
                        "student_id": self.current_user['username'],
                        "type": sub_type,
                        "content": content,
                        "status": "Pending",
                        "response": ""
                    })
                    save_json(SUBMISSIONS_FILE, subs)
                    print(f"{sub_type} submitted.")
            elif choice == '3':
                subs = load_json(SUBMISSIONS_FILE)
                print("\nYour Submissions:")
                for s in subs:
                    if s.get('student_id') == self.current_user['username']:
                        s_type = s.get('type', 'Unknown')
                        s_status = s.get('status', 'Pending')
                        s_content = s.get('content', 'No content')
                        print(f"[{s_type}] Status: {s_status} | Content: {s_content[:30]}...")
            elif choice == '4':
                break

    def staff_menu(self):
        while True:
            print("\n--- Staff Menu ---")
            print("1. View All Submissions")
            print("2. Respond to Submission")
            print("3. Logout")
            choice = input("Choice: ")
            
            if choice == '1':
                subs = load_json(SUBMISSIONS_FILE)
                print("\nAll Submissions:")
                for s in subs:
                    print(f"[{s['id']}] {s['student_id']} - {s['type']} ({s['status']})")
            elif choice == '2':
                try:
                    sub_id = int(input("Enter Submission ID: "))
                    subs = load_json(SUBMISSIONS_FILE)
                    target = next((s for s in subs if s['id'] == sub_id), None)
                    if target:
                        print(f"\nType: {target['type']}\nContent: {target['content']}")
                        action = input("1. Approve, 2. Reject: ")
                        target['status'] = "Approved" if action == '1' else "Rejected"
                        target['response'] = sanitize_input(input("Enter comment: "))
                        save_json(SUBMISSIONS_FILE, subs)
                        print("Decision recorded.")
                    else:
                        print("ID not found.")
                except ValueError:
                    print("Invalid ID.")
            elif choice == '3':
                break

if __name__ == "__main__":
    app = ProjectApprovalSystemCLI()
    while True:
        app.login()
