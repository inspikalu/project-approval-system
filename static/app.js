let currentUser = null;
let currentSubmissions = [];
let csrfToken = null;  // Store CSRF token

// Init
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('submission-form').addEventListener('submit', handleSubmission);
    
    document.querySelectorAll('.logout-btn').forEach(btn => {
        btn.addEventListener('click', handleLogout);
    });
});

async function checkAuth() {
    try {
        const response = await fetch('/api/user');
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showDashboard();
        } else {
            showScreen('login-screen');
        }
    } catch (err) {
        console.error('Auth check failed:', err);
        showScreen('login-screen');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('login-error');
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            csrfToken = data.csrf_token;  // Store CSRF token
            errorEl.classList.add('hidden');
            showDashboard();
        } else {
            errorEl.classList.remove('hidden');
        }
    } catch (err) {
        errorEl.classList.remove('hidden');
        errorEl.textContent = "Server error. Try again.";
    }
}

async function handleLogout() {
    await fetch('/api/logout', { 
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken }
    });
    currentUser = null;
    csrfToken = null;  // Clear CSRF token
    showScreen('login-screen');
}

function showDashboard() {
    if (currentUser.role === 'student') {
        document.getElementById('student-username').textContent = currentUser.username;
        showScreen('student-dashboard');
        refreshSubmissions();
    } else {
        document.getElementById('staff-username').textContent = currentUser.username;
        showScreen('staff-dashboard');
        refreshSubmissions();
    }
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));
    document.getElementById(screenId).classList.remove('hidden');
}

async function refreshSubmissions() {
    const response = await fetch('/api/submissions');
    const data = await response.json();
    currentSubmissions = data;
    
    if (currentUser.role === 'student') {
        renderStudentSubmissions();
    } else {
        renderStaffSubmissions();
    }
}

function renderStudentSubmissions() {
    const listEl = document.getElementById('student-submissions-list');
    listEl.innerHTML = currentSubmissions.length ? '' : '<p class="text-muted">No submissions found.</p>';
    
    currentSubmissions.forEach(s => {
        const item = document.createElement('div');
        item.className = 'submission-item';
        item.innerHTML = `
            <div>
                <strong>${s.type}</strong>
                <p class="text-muted" style="font-size: 0.875rem;">${s.content.substring(0, 50)}${s.content.length > 50 ? '...' : ''}</p>
            </div>
            <span class="status-badge status-${s.status.toLowerCase()}">${s.status}</span>
        `;
        listEl.appendChild(item);
    });
}

function renderStaffSubmissions() {
    const listEl = document.getElementById('staff-submissions-list');
    if (!currentSubmissions.length) {
        listEl.innerHTML = '<p class="text-muted">No submissions pending review.</p>';
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Student</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    currentSubmissions.forEach(s => {
        html += `
            <tr>
                <td>${s.id}</td>
                <td>${s.student_id}</td>
                <td>${s.type}</td>
                <td><span class="status-badge status-${s.status.toLowerCase()}">${s.status}</span></td>
                <td>
                    <button class="btn-link" onclick="reviewSubmission(${s.id})">Review</button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    listEl.innerHTML = html;
}

// Modals
let currentModalType = '';
globalThis.openModal = (type) => {
    currentModalType = type;
    document.getElementById('modal-title').textContent = `Submit ${type}`;
    document.getElementById('submission-content').value = '';
    document.getElementById('submission-modal').classList.remove('hidden');
};

globalThis.closeModal = () => {
    document.getElementById('submission-modal').classList.add('hidden');
};

async function handleSubmission(e) {
    e.preventDefault();
    const content = document.getElementById('submission-content').value;
    
    const response = await fetch('/api/submissions', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken  // Include CSRF token
        },
        body: JSON.stringify({ type: currentModalType, content })
    });
    
    if (response.ok) {
        closeModal();
        refreshSubmissions();
    }
}

// Staff Review
let currentReviewId = null;
globalThis.reviewSubmission = (id) => {
    const sub = currentSubmissions.find(s => s.id === id);
    if (!sub) return;
    
    currentReviewId = id;
    const details = document.getElementById('submission-review-details');
    details.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <p><strong>Student:</strong> ${sub.student_id}</p>
            <p><strong>Type:</strong> ${sub.type}</p>
            <div style="background: var(--bg-dark); padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem;">
                ${sub.content}
            </div>
        </div>
    `;
    document.getElementById('staff-comment').value = sub.response || '';
    document.getElementById('response-modal').classList.remove('hidden');
};

globalThis.closeResponseModal = () => {
    document.getElementById('response-modal').classList.add('hidden');
};

globalThis.submitResponse = async (status) => {
    const response = document.getElementById('staff-comment').value;
    
    const res = await fetch('/api/submissions/respond', {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken  // Include CSRF token
        },
        body: JSON.stringify({ id: currentReviewId, status, response })
    });
    
    if (res.ok) {
        closeResponseModal();
        refreshSubmissions();
    }
};
