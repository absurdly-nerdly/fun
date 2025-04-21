from flask import Flask, jsonify, request, send_from_directory
import subprocess
import os
import sys
# NOTE: You might need to install this: pip install packaging
from packaging import version as packaging_version

app = Flask(__name__)

# Determine the absolute path to the project root (one level up from 'admin')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(PROJECT_ROOT) # Assuming admin is directly under repo root
GAMES_DIR = os.path.join(REPO_ROOT, 'games')
SCRIPTS_DIR = os.path.join(REPO_ROOT, 'scripts')
ADMIN_DIR = os.path.join(REPO_ROOT, 'admin') # For serving admin.html/js

def run_command(command, cwd=None):
    """Runs a shell command and returns its stdout, stderr, and return code."""
    try:
        # Ensure the command list is correctly formatted if needed, but shell=True handles strings
        process = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd or REPO_ROOT # Default to repo root if no cwd specified
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except subprocess.CalledProcessError as e:
        # Don't print errors here, let the caller handle interpretation
        return e.stdout.strip(), e.stderr.strip(), e.returncode
    except Exception as e:
        return "", str(e), 1 # Indicate failure

@app.route('/')
def index_page():
    """Serves the main index HTML page."""
    return send_from_directory(REPO_ROOT, 'index.html')

@app.route('/admin')
def admin_page():
    """Serves the main admin HTML page."""
    return send_from_directory(ADMIN_DIR, 'admin.html')

@app.route('/admin.js')
def admin_js():
    """Serves the admin JavaScript file."""
    return send_from_directory(ADMIN_DIR, 'admin.js')

@app.route('/games/<path:filename>')
def serve_game_file(filename):
    """Serves files from the games directory."""
    return send_from_directory(GAMES_DIR, filename)

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """
    Lists games, checks for uncommitted changes, and retrieves release tags.
    """
    apps_data = []
    if not os.path.isdir(GAMES_DIR):
        return jsonify({"error": f"Games directory not found: {GAMES_DIR}"}), 500

    try:
        for app_name in os.listdir(GAMES_DIR):
            app_path = os.path.join(GAMES_DIR, app_name)
            if os.path.isdir(app_path):
                # --- Check git status ---
                status_stdout, status_stderr, status_exit_code = run_command(f'git status --porcelain "{app_path}"', cwd=REPO_ROOT)
                has_updates = False
                if status_exit_code == 0 and status_stdout:
                    has_updates = True
                elif status_exit_code != 0:
                    print(f"Warning: git status check failed for {app_name}: {status_stderr}", file=sys.stderr)

                # --- Get release tags ---
                tag_prefix = f"{app_name}-v"
                tags_stdout, tags_stderr, tags_exit_code = run_command(f'git tag --list "{tag_prefix}*"', cwd=REPO_ROOT)

                all_tags = []
                latest_tag = None

                if tags_exit_code == 0 and tags_stdout:
                    # Split tags by newline and filter out empty strings
                    raw_tags = list(filter(None, tags_stdout.splitlines()))

                    # Parse and sort tags using packaging.version
                    parsed_tags = []
                    for tag in raw_tags:
                        try:
                            # Extract version part after prefix (e.g., '1.0.1' from 'app-v1.0.1')
                            version_str = tag[len(tag_prefix):]
                            parsed_tags.append((packaging_version.parse(version_str), tag))
                        except packaging_version.InvalidVersion:
                            print(f"Warning: Could not parse version from tag '{tag}'. Skipping.", file=sys.stderr)
                            # Optionally include unparseable tags if needed
                            # all_tags.append(tag)

                    # Sort by version, highest first
                    parsed_tags.sort(key=lambda x: x[0], reverse=True)

                    # Extract sorted tag names
                    all_tags = [tag for version, tag in parsed_tags]
                    if all_tags:
                        latest_tag = all_tags[0] # Highest version is the first after reverse sort

                elif tags_exit_code != 0:
                    print(f"Warning: git tag check failed for {app_name}: {tags_stderr}", file=sys.stderr)

                apps_data.append({
                    "name": app_name,
                    "has_updates": has_updates,
                    "latest_tag": latest_tag,
                    "all_tags": all_tags
                })

        return jsonify(apps_data)
    except Exception as e:
        print(f"Error listing apps: {e}", file=sys.stderr)
        return jsonify({"error": "Failed to list applications."}), 500


@app.route('/api/release', methods=['POST'])
def create_release():
    """Triggers the release manager script."""
    data = request.get_json()
    if not data or 'app_name' not in data or 'version_tag' not in data:
        return jsonify({"error": "Missing 'app_name' or 'version_tag' in request body"}), 400

    app_name = data['app_name']
    version_tag = data['version_tag']
    script_path = os.path.join(SCRIPTS_DIR, 'release_manager.py')

    if not os.path.isfile(script_path):
         return jsonify({"error": f"Release script not found: {script_path}"}), 500

    try:
        # Use sys.executable to ensure we're using the same Python interpreter
        command = f'"{sys.executable}" "{script_path}" "{app_name}" "{version_tag}"'
        print(f"Running command: {command}") # Log the command being run

        # Run the script from the repository root
        stdout, stderr, exit_code = run_command(command, cwd=REPO_ROOT)

        print(f"Script stdout:\n{stdout}")
        print(f"Script stderr:\n{stderr}")
        print(f"Script exit code: {exit_code}")

        if exit_code == 0:
            return jsonify({"success": True, "message": f"Release {version_tag} for {app_name} created successfully.", "details": stdout})
        else:
            # Combine stdout and stderr for a more complete error message from the script
            error_details = f"Exit Code: {exit_code}\nOutput:\n{stdout}\nError Output:\n{stderr}"
            return jsonify({"success": False, "message": f"Failed to create release {version_tag} for {app_name}.", "details": error_details}), 500

    except Exception as e:
        print(f"Error calling release script: {e}", file=sys.stderr)
        return jsonify({"success": False, "message": "An unexpected error occurred while trying to create the release."}), 500

if __name__ == '__main__':
    # Make sure Flask runs on 0.0.0.0 to be accessible from network if needed,
    # and choose a port (e.g., 5001 to avoid conflicts). Debug=True is helpful during development.
    app.run(host='0.0.0.0', port=5001, debug=True)