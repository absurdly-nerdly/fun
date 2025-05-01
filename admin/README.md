# Release Manager (`release_manager.py`)

## Purpose

This script automates the creation and pushing of Git tags for application releases within this project. It is typically invoked via the web-based Admin Panel but can also be run manually.

## Prerequisites

-   This script requires a local Python environment and Git access. It cannot be run directly from a deployed GitHub page.
-   Git must be installed and accessible in your PATH.
-   Your local repository must have a Git remote named `fun` configured to point to the central repository (e.g., on GitHub).

## Workflow (Using Admin Panel - Recommended)

This is the standard process for creating a new release version:

1.  **Start Server:** Run the admin server locally:
    ```bash
    python admin/admin_server.py
    ```
2.  **Access Panel:** Open `http://localhost:5001/admin` in your browser.
3.  **Develop:** Make your code changes to the target application (e.g., `games/balloon-puff/`).
4.  **Commit Changes:** **Crucially, commit all your changes using Git before proceeding.** The Admin Panel will indicate if uncommitted changes exist.
    ```bash
    git add .
    git commit -m "feat: Add new feature to balloon-puff"
    ```
5.  **Create Release via Panel:**
    -   Find your application in the Admin Panel list.
    -   Enter the new semantic version tag (e.g., `1.0.1`) in the "New Version Tag" input field.
    -   Click the "Create Release" button.
6.  **Verification:** The script will create the tag locally (e.g., `balloon-puff-v1.0.1`) and push it to the `fun` remote. The Admin Panel will display success or failure messages.
7.  **Repeat:** For subsequent releases, repeat steps 3-6.

## Workflow (Manual Script Execution - Alternative)

You can bypass the Admin Panel and run the script directly:

1.  **Develop:** Make your code changes.
2.  **Commit Changes:** Commit all changes using Git.
    ```bash
    git add .
    git commit -m "fix: Resolve issue in balloon-puff"
    ```
3.  **Run Script:** Execute the script from the repository root, providing the application name (directory name under `games/`) and the new version tag.
    ```bash
    python admin/release_manager.py <app_name> <version_tag>
    # Example:
    python admin/release_manager.py balloon-puff 1.0.2
    ```
4.  **Verification:** The script will output progress and success/failure messages to the console.
5.  **Repeat:** For subsequent releases, repeat steps 1-4.

## Important Notes

-   **Tagging Only:** This script *only* creates and pushes Git tags. It does **not** handle building, deploying, or serving the application files for different releases. The "View Version" button in the Admin Panel links to the tag on GitHub.
-   **Commit First:** Always commit your code changes *before* creating a release tag. Tagging uncommitted work can lead to inconsistent release states.
-   **Tagging Mechanism:** The `git tag` command, as used by the script, applies the version tag to the Git commit that your `HEAD` is currently pointing to. This is typically the most recent commit on your current branch.