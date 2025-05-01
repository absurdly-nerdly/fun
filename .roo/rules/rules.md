# Project Structure Rules

## Game Directory Structure

To ensure compatibility with the Admin Panel and Release Manager, all games/applications must adhere to the following structure within the main `games/` directory:

```
games/
└── <app_name>/              # Root folder for the specific game (e.g., balloon-puff)
    ├── working/             # Contains all current development files for the app
    │   ├── index.html       # Or the main entry point HTML file (e.g., balloon-puff.html)
    │   ├── script.js
    │   ├── style.css
    │   └── ...              # Other game assets, scripts, etc.
    │
    └── releases/            # Contains archived, immutable release versions (Managed by release_manager.py)
        ├── <version_tag>/   # Subfolder for a specific release (e.g., 1.0.0)
        │   ├── index.html   # Copy of the entry point at the time of release
        │   ├── script.js    # Copy of script.js at the time of release
        │   ├── style.css    # Copy of style.css at the time of release
        │   └── ...          # Copy of other assets at the time of release
        │
        └── <another_version_tag>/ # e.g., 1.0.1
            └── ...
```

-   **`games/<app_name>/working/`**: All active development must occur within this directory. The release manager copies files *from* here when creating a new release.
-   **`games/<app_name>/releases/`**: This directory is managed by the `release_manager.py` script. Do not manually modify its contents. Each subfolder represents a point-in-time snapshot of the `working` directory.
-   **Entry Point:** Ensure each game (both in `working` and each `releases/<version>`) has a clear HTML entry point (e.g., `index.html`, `<app_name>.html`).

Failure to follow this structure will prevent the Admin Panel from correctly identifying applications, versions, and managing releases.



## Balloon Puff:

### Sound Asset Rules:

-   **Format:** Use WAV format.
-   **Duration:** Keep sounds short (e.g., typically under 1-2 seconds).
-   **Style:** Prefer retro-style 8-bit sounds.
-   **File Size:** Keep file sizes small (e.g., typically under 100KB each).