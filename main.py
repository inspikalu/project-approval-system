import tkinter as tk
from tkinter import messagebox, ttk
import json
import hashlib
import os
import secrets

# --- Security & Data Constants ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.json")
SALT = b"salt123" # Legacy salt for migration

# --- Security Utilities ---
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    if isinstance(salt, str):
        salt_bytes = salt.encode()
    else:
        salt_bytes = salt
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt_bytes, 100000).hex(), salt

def load_json(filepath):
    if not os.path.exists(filepath): return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except: return []

def save_json(filepath, data):
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def sanitize_input(text):
    return text.strip()[:1000]

# --- App Logic ---
class ProjectApprovalSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Approval System")
        self.root.geometry("650x500")
        self.current_user = None
        self.show_login()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        tk.Label(self.root, text="Project Approval System Login", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Username").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.handle_login).pack(pady=20)

    def handle_login(self):
        user = sanitize_input(self.username_entry.get())
        pw = self.password_entry.get()
        users = load_json(USERS_FILE)
        match = next((u for u in users if u['username'] == user), None)
        
        if match:
            # Hash use the stored salt
            hashed, _ = hash_password(pw, match.get('salt', SALT))
            if match['pw'] == hashed:
                self.current_user = match
                if match['role'] == 'student':
                    self.show_student_dashboard()
                else:
                    self.show_staff_dashboard()
                return
        
        messagebox.showerror("Error", "Invalid credentials.")

    def show_student_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text=f"Student Dashboard: {self.current_user['username']}", font=("Arial", 14)).pack(pady=10)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Submit Project Topic", width=25, 
                  command=lambda: self.show_submission_form("Topic")).pack(pady=5)
        tk.Button(btn_frame, text="Submit Background of Study", width=25, 
                  command=lambda: self.show_submission_form("Background")).pack(pady=5)

        tk.Label(self.root, text="Your Submissions:", font=("Arial", 10, "bold")).pack(pady=5)
        
        scroll_frame = tk.Frame(self.root)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        canvas = tk.Canvas(scroll_frame)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        submissions = load_json(SUBMISSIONS_FILE)
        for s in submissions:
            if s.get('student_id') == self.current_user['username']:
                s_type = s.get('type', 'Unknown')
                s_content = s.get('content', 'No content')
                s_status = s.get('status', 'Pending')
                color = "green" if s_status == "Approved" else "red" if s_status == "Rejected" else "black"
                tk.Label(scrollable_frame, text=f"[{s_type}] {s_content[:30]}... | Status: {s_status}", 
                         fg=color).pack(anchor="w")

        tk.Button(self.root, text="Logout", command=self.show_login).pack(pady=10)

    def show_submission_form(self, sub_type):
        form = tk.Toplevel(self.root)
        form.title(f"Submit {sub_type}")
        form.geometry("400x350")
        
        tk.Label(form, text=f"Enter {sub_type} Details:", font=("Arial", 10, "bold")).pack(pady=10)
        text_area = tk.Text(form, height=10, width=45)
        text_area.pack(padx=10, pady=10)
        
        def submit():
            content = sanitize_input(text_area.get("1.0", tk.END))
            if not content:
                messagebox.showwarning("Warning", "Content cannot be empty.")
                return
            
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
            messagebox.showinfo("Success", f"{sub_type} submitted successfully.")
            form.destroy()
            self.show_student_dashboard()

        tk.Button(form, text="Submit", command=submit, width=15).pack(pady=10)

    def show_staff_dashboard(self):
        self.clear_screen()
        tk.Label(self.root, text="Staff Dashboard - Submissions Review", font=("Arial", 14)).pack(pady=10)
        
        self.tree = ttk.Treeview(self.root, columns=("ID", "Student", "Type", "Status"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.heading("Student", text="Student")
        self.tree.heading("Type", text="Type"); self.tree.heading("Status", text="Status")
        self.tree.column("ID", width=30); self.tree.column("Student", width=100)
        self.tree.column("Type", width=100); self.tree.column("Status", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10)

        self.load_submissions()

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Refresh", command=self.load_submissions, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Respond to Selected", command=self.respond_submission, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(self.root, text="Logout", command=self.show_login).pack(pady=5)

    def load_submissions(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for s in load_json(SUBMISSIONS_FILE):
            self.tree.insert("", "end", values=(
                s.get('id', '??'), 
                s.get('student_id', 'Unknown'), 
                s.get('type', 'Unknown'), 
                s.get('status', 'Pending')
            ))

    def respond_submission(self):
        selected = self.tree.selection()
        if not selected: return
        item_id = self.tree.item(selected)['values'][0]
        
        subs = load_json(SUBMISSIONS_FILE)
        sub = next((s for s in subs if s['id'] == item_id), None)
        if not sub: return

        form = tk.Toplevel(self.root)
        form.title("Review Submission")
        form.geometry("450x400")
        
        tk.Label(form, text=f"{sub['type']} from {sub['student_id']}:", font=("Arial", 10, "bold")).pack(pady=5)
        
        content_box = tk.Text(form, height=8, width=50, bg="#f0f0f0", relief=tk.SUNKEN)
        content_box.insert(tk.END, sub['content'])
        content_box.config(state=tk.DISABLED)
        content_box.pack(pady=10, padx=10)

        tk.Label(form, text="Staff Comments:").pack()
        resp_entry = tk.Entry(form, width=50)
        resp_entry.pack(pady=5, padx=10)

        def update(action):
            for s in subs:
                if s['id'] == item_id:
                    s['status'] = action
                    s['response'] = sanitize_input(resp_entry.get())
            save_json(SUBMISSIONS_FILE, subs)
            form.destroy(); self.load_submissions()
            messagebox.showinfo("Status", f"Submission {action}")

        btn_frame = tk.Frame(form)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Approve", bg="green", fg="white", width=12, command=lambda: update("Approved")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Reject", bg="red", fg="white", width=12, command=lambda: update("Rejected")).pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectApprovalSystem(root)
    root.mainloop()
