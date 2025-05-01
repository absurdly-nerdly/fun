document.addEventListener('DOMContentLoaded', () => {
    const appList = document.getElementById('app-list');
    const messageArea = document.getElementById('message-area');
    const appsContainer = document.getElementById('apps-container'); // To replace the "Loading..." message

    function displayMessage(message, details = '', isError = false) {
        messageArea.innerHTML = ''; // Clear previous messages
        messageArea.textContent = message;
        messageArea.className = 'message-area'; // Reset classes
        messageArea.classList.add(isError ? 'error' : 'success');

        if (details) {
            const pre = document.createElement('pre');
            pre.textContent = details;
            messageArea.appendChild(pre);
        }

        messageArea.style.display = 'block';
        // Optional: Auto-hide message after some time
        // setTimeout(() => { messageArea.style.display = 'none'; }, 5000);
    }

    function handleReleaseClick(event) {
        const button = event.target;
        const appItem = button.closest('.app-item');
        const appName = appItem.dataset.appName;
        const versionInput = appItem.querySelector('.version-input');
        const versionTag = versionInput.value.trim(); // This is the version string like '1.0.0'

        if (!versionTag) {
            displayMessage('Please enter a version (e.g., 1.0.0).', '', true);
            versionInput.focus();
            return;
        }

        // Basic validation for version format (optional, can be improved)
        if (!/^\d+\.\d+\.\d+$/.test(versionTag)) {
             displayMessage('Version should be in format X.Y.Z (e.g., 1.0.0).', '', true);
             versionInput.focus();
             return;
        }

        button.disabled = true; // Prevent double clicks
        button.textContent = 'Releasing...';
        messageArea.style.display = 'none'; // Hide old messages

        fetch('/api/release', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // Send app_name and the version string as version_tag
            body: JSON.stringify({ app_name: appName, version_tag: versionTag }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayMessage(data.message, data.details || '', false);
                versionInput.value = ''; // Clear input on success
                // Reload app list to show new version
                loadApps();
            } else {
                displayMessage(data.message || 'An unknown error occurred.', data.details || '', true);
            }
        })
        .catch(error => {
            console.error('Error creating release:', error);
            displayMessage('Failed to communicate with the server.', error.toString(), true);
        })
        .finally(() => {
            button.disabled = false; // Re-enable button
            button.textContent = 'Create Release';
        });
    }

    function loadApps() {
        fetch('/api/apps')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(apps => {
                appsContainer.innerHTML = ''; // Clear "Loading..."
                appList.innerHTML = ''; // Clear previous list items

                if (apps.error) {
                     appsContainer.innerHTML = `<p class="message-area error">Error loading apps: ${apps.error}</p>`;
                     return;
                }
                if (apps.length === 0) {
                    appsContainer.innerHTML = '<p>No applications found in the /games directory.</p>';
                    return;
                }


                apps.forEach(app => {
                    const li = document.createElement('li');
                    li.classList.add('app-item');
                    li.dataset.appName = app.name; // Store app name for later use

                    let statusText = 'Ready to release.';
                    if (app.has_updates) {
                        li.classList.add('has-updates');
                        statusText = 'Working directory has uncommitted changes (Commit manually before releasing).';
                    }

                    // Show version information using latest_version
                    const versionInfo = app.latest_version ?
                        `Latest Release: <span class="latest-tag">${app.latest_version}</span>` : // Use latest_version
                        'No releases yet';

                    // Populate dropdown with all_versions
                    const versionsDropdown = app.all_versions && app.all_versions.length > 0 ? `
                        <div class="version-selector">
                            <select class="version-select">
                                <option value="">Select a version...</option>
                                ${app.all_versions.map(version => `<option value="${version}">${version}</option>`).join('')}
                            </select>
                            <button class="view-version-button">View Version</button>
                        </div>
                    ` : '';

                    li.innerHTML = `
                        <h2>${app.name}</h2>
                        <div class="version-info">
                            <p>${versionInfo}</p>
                            ${versionsDropdown}
                        </div>
                        <p class="status">${statusText}</p>
                        <div class="release-form">
                            <label for="version-${app.name}">New Version (e.g., 1.0.0):</label>
                            <input type="text" id="version-${app.name}" class="version-input" placeholder="X.Y.Z">
                            <button class="release-button">Create Release</button>
                        </div>
                    `;
                    appList.appendChild(li);
                });
                 appsContainer.appendChild(appList); // Add the list back

                // Add event listeners after elements are created
                document.querySelectorAll('.release-button').forEach(button => {
                    button.addEventListener('click', handleReleaseClick);
                });

                // Add event listeners for version selector buttons
                document.querySelectorAll('.view-version-button').forEach(button => {
                    button.addEventListener('click', (event) => {
                        const appItem = event.target.closest('.app-item');
                        const appName = appItem.dataset.appName;
                        const select = appItem.querySelector('.version-select');
                        const selectedVersion = select.value;

                        if (!selectedVersion) {
                            displayMessage('Please select a version to view.', '', true);
                            return;
                        }

                        // Construct URL to the release version served locally
                        // Assumes entry point is <app_name>.html or index.html
                        // TODO: Make entry point configurable or detectable?
                        const entryPoint = `${appName}.html`; // Or 'index.html' if that's standard
                        const releaseUrl = `/games/${appName}/releases/${selectedVersion}/${entryPoint}`;

                        console.log(`Opening release URL: ${releaseUrl}`);
                        window.open(releaseUrl, '_blank');
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching apps:', error);
                 appsContainer.innerHTML = `<p class="message-area error">Failed to load applications from the server. Is it running? Error: ${error.message}</p>`;
            });
    }

    // Initial load
    loadApps();
});