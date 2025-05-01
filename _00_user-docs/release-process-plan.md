# Release Process Plan

## 1. Goal

Create a simple web-based admin interface to manage releases for multiple game applications within the `games/` directory by triggering a Python script that handles Git tagging. Commits will be handled manually by the developer before using this tool.

## 2. Proposed Project Structure

```
d:/git/LLM/fun/
├── fun.code-workspace
├── index.html              # Main landing page
├── admin/                  # NEW: Admin UI and Server
│   ├── admin.html          # NEW: The admin interface page
│   ├── admin.js            # NEW: JavaScript for the admin page logic
│   └── admin_server.py     # NEW: Simple web server (e.g., Flask)
├── scripts/                # NEW: Utility scripts
│   └── release_manager.py  # NEW: Python script for Git operations
├── games/
│   └── balloon-puff/
│       └── ... (game files)
│   └── another-game/       # Example of another game
│       └── ...
├── _00_user-docs/
│   └── release-process-plan.md # This file
└── .git/
    └── ...
```

## 3. Components & Workflow

*   **Landing Page (`index.html`):**
    *   Add a small link/button pointing to `/admin`.

*   **Admin Server (`admin/admin_server.py`):**
    *   Lightweight Python web server (Flask recommended for simplicity).
    *   **Endpoint `/admin` (GET):** Serves `admin.html`.
    *   **Endpoint `/api/apps` (GET):**
        *   Lists directories in `games/`.
        *   Checks `git status` for each game directory.
        *   Returns JSON: `[{'name': 'app_name', 'has_updates': boolean}, ...]`.
    *   **Endpoint `/api/release` (POST):**
        *   Accepts JSON: `{'app_name': '...', 'version_tag': '...'}`.
        *   Calls `admin/release_manager.py` via `subprocess`.
        *   Captures script output.
        *   Returns JSON indicating success/failure.

*   **Release Manager Script (`admin/release_manager.py`):**
    *   Command-line Python script.
    *   Accepts `app_name` and `version_tag` arguments.
    *   Constructs full tag (e.g., `app_name-vX.Y.Z`).
    *   Checks if tag already exists (`git tag -l <tag_name>`).
    *   Executes `git tag <full_tag_name>`.
    *   Executes `git push origin <full_tag_name>`.
    *   Prints success/error messages.

*   **Admin UI (`admin/admin.html` + `admin.js`):**
    *   Simple HTML + JavaScript.
    *   On load: Fetch and display apps from `/api/apps`.
    *   Provide input for version tag and a "Create Release" button per app.
    *   On button click: Send POST to `/api/release`.
    *   Display success/failure message from server response.

## 4. Workflow Diagram

```mermaid
graph TD
    A[Developer Commits Changes Manually] --> B(Ready for Release);

    subgraph User Interaction
        C[User visits Landing Page (index.html)] --> D{Admin Link};
        D --> E[User clicks Admin Link];
        E --> F[Browser requests /admin];
    end

    subgraph Admin System
        G[Admin Server (admin_server.py)];
        H[Release Script (release_manager.py)];
        I[Admin UI (admin.html + admin.js)];

        F --> G;
        G -- Serves --> I[Renders Admin UI];

        I -- GET /api/apps --> G;
        G -- Lists games/, checks git status --> I[Displays Apps & Status];

        I -- User enters version, clicks Release --> J[POST /api/release (app, version)];
        J --> G;
        G -- Calls script --> H[Executes git tag, git push];
        H -- Returns output --> G;
        G -- Returns success/error --> I[Displays Result to User];
    end

    style G fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#ccf,stroke:#333,stroke-width:2px
    style I fill:#lightgrey,stroke:#333,stroke-width:1px
```

## 5. V1 Feature Ideas

*   Display existing tags for each app in the admin UI.
*   Basic server-side logging of release attempts.