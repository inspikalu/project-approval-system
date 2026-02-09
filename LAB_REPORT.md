# Lab Report: Secure Project Topic and Background Approval System

## 1. Overview
This system is designed to facilitate secure submission and approval of project topics and background of study documents. Students can safely submit their research ideas and supporting backgrounds, while staff can review and either approve or reject these submissions. Security is integrated at every stage of the development lifecycle.

## 2. Security Requirements
- **SR1: Authentication**: All users must authenticate with a username and password before accessing any system features.
- **SR2: Data Confidentiality**: Passwords must never be stored in plain text; they must be hashed using a strong, salted cryptographic algorithm.
- **SR3: Role-Based Access Control (RBAC)**: Distinct roles (Student, Staff) must exist, and users must only access functionalities relevant to their role.
- **SR4: Input Validation**: All system inputs (topics, backgrounds, credentials) must be sanitized to prevent injection attacks.
- **SR5: Audit Logging**: Key activities such as login attempts and submission statuses should be minimally recorded.
- **SR6: Session Security**: Application state must reset upon logout to prevent unauthorized access.
- **SR7: Data Integrity**: Submissions and approval statuses must not be modifiable by unauthorized roles.

## 3. User Stories and Tasks

### User Story 1: Student Login
*As a student, I want to securely log into the system so that I can submit my project details.*
- **Task 1.1**: Implement a login GUI with concealed password input.
- **Task 1.2**: Create a backend check against hashed credentials in `users.json`.

### User Story 2: Submit Project Topic
*As a student, I want to submit my proposed project topic so that it can be reviewed by staff.*
- **Task 2.1**: Create a dedicated form for Topic submission.
- **Task 2.2**: Save topic to `submissions.json` with "Pending" status.

### User Story 3: Submit Background of Study
*As a student, I want to submit my research background so that staff can evaluate my project scope.*
- **Task 3.1**: Create a dedicated form for Background submission.
- **Task 3.2**: Save background to `submissions.json` linked to the student.

### User Story 4: Staff Review
*As a staff member, I want to review all pending topics and backgrounds so that I can guide student research.*
- **Task 4.1**: Create a staff dashboard that lists all submissions.
- **Task 4.2**: Implement a detail view to read the full text of topics/backgrounds.

### User Story 5: Approval Action
*As a staff member, I want to approve or reject a submission so that the student can proceed or revise.*
- **Task 5.1**: Provide "Approve" and "Reject" actions on the staff view.
- **Task 5.2**: Update submission status in `submissions.json`.

## 4. Design Artifacts

### A. Use Case Diagram
```
[Student] --(Login)--> [System]
[Student] --(Submit Topic)--> [System]
[Student] --(Submit Background)--> [System]

[Staff]   --(Login)--> [System]
[Staff]   --(Review Submissions)--> [System]
[Staff]   --(Approve/Reject)--> [System]
```

### B. Class Diagram
```
+---------------+       +-------------------+
|     User      |       |    Submission     |
+---------------+       +-------------------+
| username      |       | student_id        |
| password_hash |       | type (Topic/BG)   |
| role          |       | content           |
+---------------+       | status            |
                        | staff_response    |
                        +-------------------+
```

### C. Sequence Diagram: Student Submitting Topic
```
Student -> GUI: Enter Topic Content
GUI -> Validator: Sanitize Input
Validator -> GUI: Input OK
GUI -> Storage: Write to submissions.json (type="Topic")
Storage -> GUI: Success
GUI -> Student: Show Confirmation
```

### D. Threat Model (STRIDE)
| Threat | Security Control |
|---|---|
| **Spoofing** | PBKDF2 Hashing with unique salt. |
| **Tampering** | Role-based logic prevents students from approving their own work. |
| **Information Disclosure** | Data filtered by owner; staff see all, students see only theirs. |

## 5. Implementation Algorithm
1. Initialize Application Environment (Check/Create JSON files).
2. Load Login Screen.
3. On Login: Determine role and load Dashboard.
4. Student Dashboard:
    a. Button 1: Load "Topic Submission" form.
    b. Button 2: Load "Background Submission" form.
    c. Action: Save to `submissions.json` with `type` and `status="Pending"`.
5. Staff Dashboard:
    a. Load all entries from `submissions.json`.
    b. Select entry -> Read full content -> Action: Approve/Reject.
6. Enforce logout.

## 6. Python Implementation
(See `main.py` for full implementation)

## 7. Validation
(Results based on new scenario)

| Test Case ID | Description | Input | Expected Outcome | Result |
|---|---|---|---|---|
| TC-01 | Submit Topic | "AI in Healthcare" | Entry saved in submissions.json with type 'Topic' | **PASS** |
| TC-02 | Submit Background | "Long text about..." | Entry saved in submissions.json with type 'Background' | **PASS** |
| TC-03 | Staff Approval | Select ID 1 -> Approve | Status updated to 'Approved' | **PASS** |
| TC-04 | Logic Guard | Student trying to act | Action denied via GUI role check | **PASS** |
