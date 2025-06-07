const apiBaseUrl = 'http://localhost:5000';

// Utility function to create list item elements
function createListItem(text, className = '') {
    const li = document.createElement('li');
    li.textContent = text;
    if (className) {
        li.classList.add(className);
    }
    return li;
}

// Fetch and display donors
async function loadDonors() {
    const res = await fetch(`${apiBaseUrl}/donors`);
    const donors = await res.json();
    const donorsList = document.getElementById('donors-list');
    donorsList.innerHTML = '';
    donors.forEach(donor => {
        donorsList.appendChild(createListItem(`${donor.name} (${donor.blood_group}) - Phone: ${donor.contact || '-'} Email: ${donor.email || '-'}`));
    });
}

// Fetch and display requests with status and action buttons
async function loadRequests() {
    const res = await fetch(`${apiBaseUrl}/requests`);
    const requests = await res.json();
    const requestsList = document.getElementById('requests-list');
    requestsList.innerHTML = '';
    requests.forEach(req => {
        const li = document.createElement('li');
        li.textContent = `${req.patient_name || 'Unknown'} - ${req.blood_group} - ${req.quantity} units - Status: `;
        const statusSpan = document.createElement('span');
        statusSpan.textContent = req.status;
        statusSpan.classList.add(`status-${req.status}`);
        li.appendChild(statusSpan);

        if (req.status === 'pending') {
            const approveBtn = document.createElement('button');
            approveBtn.textContent = 'Approve';
            approveBtn.onclick = () => updateRequestStatus(req.id, 'approved');

            const rejectBtn = document.createElement('button');
            rejectBtn.textContent = 'Reject';
            rejectBtn.onclick = () => updateRequestStatus(req.id, 'rejected');

            const btnContainer = document.createElement('span');
            btnContainer.classList.add('status-buttons');
            btnContainer.appendChild(approveBtn);
            btnContainer.appendChild(rejectBtn);
            li.appendChild(btnContainer);
        }
        requestsList.appendChild(li);
    });
}

// Add donor form submission
document.getElementById('donor-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('donor-name').value.trim();
    const blood_group = document.getElementById('donor-blood-type').value.trim();
    const phone = document.getElementById('donor-phone').value.trim();
    const email = document.getElementById('donor-email').value.trim();

    const res = await fetch(`${apiBaseUrl}/donors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, blood_group, contact: phone, email })
    });
    if (res.ok) {
        alert('Donor added successfully');
        e.target.reset();
        loadDonors();
    } else {
        const error = await res.json();
        alert('Error: ' + error.error);
    }
});

// Add request form submission
document.getElementById('request-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const patient_name = document.getElementById('request-patient-name').value.trim();
    const blood_group = document.getElementById('request-blood-type').value.trim();
    const quantity = parseInt(document.getElementById('request-quantity').value);

    const res = await fetch(`${apiBaseUrl}/requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_name, blood_group, quantity })
    });
    if (res.ok) {
        alert('Request added successfully');
        e.target.reset();
        loadRequests();
    } else {
        const error = await res.json();
        alert('Error: ' + error.error);
    }
});

// Update request status
async function updateRequestStatus(requestId, status) {
    const res = await fetch(`${apiBaseUrl}/requests/${requestId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
    });
    if (res.ok) {
        alert('Request status updated');
        loadRequests();
    } else {
        const error = await res.json();
        alert('Error: ' + error.error);
    }
}

// Initial load
window.onload = () => {
    loadDonors();
    loadRequests();
};
