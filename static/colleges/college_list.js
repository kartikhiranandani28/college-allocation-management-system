function updatePreference(collegeId) {
    const button = document.querySelector(`#college-${collegeId} .toggle-button`);
    const action = button.innerText === 'Add' ? 'add' : 'remove';

    fetch("{% url 'update_preference' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: new URLSearchParams({ college_id: collegeId, action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            button.innerText = 'Remove';
            button.classList.add('remove');
            addToPreferenceList(collegeId, button.previousElementSibling.innerText);
        } else if (data.status === 'removed') {
            button.innerText = 'Add';
            button.classList.remove('remove');
            removeFromPreferenceList(collegeId);
        }
    })
    .catch(error => console.error('Error:', error));
}

function addToPreferenceList(collegeId, collegeName) {
    const preferenceList = document.getElementById('preference-items');
    const noPreference = document.getElementById('no-preference');

    if (noPreference) {
        noPreference.remove();
    }

    const listItem = document.createElement('li');
    listItem.id = `preference-${collegeId}`;
    listItem.innerHTML = `
        ${collegeName}
        <button onclick="updatePreference('${collegeId}')">Remove</button>
    `;
    preferenceList.appendChild(listItem);
}

function removeFromPreferenceList(collegeId) {
    const listItem = document.getElementById(`preference-${collegeId}`);
    listItem.remove();

    const preferenceList = document.getElementById('preference-items');
    if (!preferenceList.hasChildNodes()) {
        const noPreference = document.createElement('li');
        noPreference.id = 'no-preference';
        noPreference.innerText = 'No preferences selected yet.';
        preferenceList.appendChild(noPreference);
    }
}
