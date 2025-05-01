# Release Manager (`admin/release_manager.py`)

## Purpose

This script automates the process of creating a new release version for an application by archiving its current state from the `working` directory into a versioned subfolder within the `releases` directory and creating a corresponding Git tag. It is typically invoked via the web-based Admin Panel but can also be run manually.

## Prerequisites

-   Git must be installed and accessible in your PATH.
-   Your local repository must have a Git remote named `fun` configured to point to the central repository (e.g., on GitHub).
-   The application must follow the directory structure defined in `.roo/rules/rules.md` (i.e., having `working` and `releases` subdirectories).

## Workflow (Using Admin Panel - Recommended)

This is the standard process for creating a new release version:

1.  **Start Server:** Run the admin server locally:
    ```bash
    python admin/admin_server.py
    ```
2.  **Access Panel:** Open `http://localhost:5001/admin` in your browser.
3.  **Develop:** Make your code changes to the target application within its `working` directory (e.g., `games/balloon-puff/working/`).
4.  **Commit Changes:** **Crucially, commit all your changes using Git before proceeding.** The Admin Panel will indicate if uncommitted changes exist in the `working` directory.
    ```bash
    git add .
    git commit -m "feat: Add new feature to balloon-puff"
    ```
5.  **Create Release via Panel:**
    -   Find your application in the Admin Panel list.
    -   Enter the new semantic version (e.g., `1.1.0`) in the "New Version" input field.
    -   Click the "Create Release" button.
6.  **Verification:** The script will:
    -   Copy all files from `games/<app_name>/working/` to `games/<app_name>/releases/<version>/`.
    -   Create a Git tag locally (e.g., `balloon-puff-v1.1.0`).
    -   Push the Git tag to the `fun` remote.
    The Admin Panel will display success or failure messages.
7.  **View Released Version:** Use the version dropdown and "View Version" button in the Admin Panel to open the locally archived release in your browser (e.g., `http://localhost:5001/games/balloon-puff/releases/1.1.0/balloon-puff.html`).
8.  **Repeat:** For subsequent releases, repeat steps 3-7.

## Workflow (Manual Script Execution - Alternative)

You can bypass the Admin Panel and run the script directly:

1.  **Develop:** Make your code changes in the `working` directory.
2.  **Commit Changes:** Commit all changes using Git.
    ```bash
    git add .
    git commit -m "fix: Resolve issue in balloon-puff"
    ```
3.  **Run Script:** Execute the script from the repository root, providing the application name (directory name under `games/`) and the new version.
    ```bash
    python admin/release_manager.py <app_name> <version>
    # Example:
    python admin/release_manager.py balloon-puff 1.1.0
    ```
4.  **Verification:** The script will output progress and success/failure messages to the console. It will copy files and create/push the Git tag.
5.  **Repeat:** For subsequent releases, repeat steps 1-4.

## Important Notes

-   **Local Archiving and Tagging:** This script archives the `working` directory content into a versioned folder within `releases` and creates a corresponding Git tag.
-   **Local Serving:** The Admin Server (`admin/admin_server.py`) is required to serve these local release archives via HTTP (e.g., `http://localhost:5001/games/...`).
-   **Deployment:** This script and the local archiving process do **not** handle deploying your application releases to a web hosting service like GitHub Pages. A separate deployment strategy is needed to make specific release versions accessible online.
-   **Commit First:** Always commit your code changes *before* creating a release. Tagging uncommitted work can lead to inconsistent release states.
-   **Tagging Mechanism:** The `git tag` command, as used by the script, applies the version tag to the Git commit that your `HEAD` is currently pointing to. This is typically the most recent commit on your current branch.
-   **Root Index Update:** After a successful release, the script automatically updates the root `index.html` file to link to the latest released version of all games found in the `games/` directory. This is intended for static hosting like GitHub Pages.