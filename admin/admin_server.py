from flask import Flask, jsonify, request, send_from_directory, abort
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
# SCRIPTS_DIR = os.path.join(REPO_ROOT, 'scripts') # No longer used for release manager
ADMIN_DIR = os.path.join(REPO_ROOT, 'admin') # For serving admin.html/js

def run_command(command, cwd=None):
    """Runs a shell command and returns its stdout, stderr, and return code."""
    try:
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
        return e.stdout.strip(), e.stderr.strip(), e.returncode
    except Exception as e:
        return "", str(e), 1 # Indicate failure

# --- Static File Serving ---

@app.route('/')
def index_page():
    """Serves the main index HTML page from repo root."""
    return send_from_directory(REPO_ROOT, 'index.html')

@app.route('/admin')
def admin_page():
    """Serves the main admin HTML page."""
    return send_from_directory(ADMIN_DIR, 'admin.html')

@app.route('/admin.js')
def admin_js():
    """Serves the admin JavaScript file."""
    return send_from_directory(ADMIN_DIR, 'admin.js')

# Serve files from a game's 'working' directory
@app.route('/games/<app_name>/working/<path:filename>')
def serve_game_working_file(app_name, filename):
    """Serves files from a game's working directory."""
    working_dir = os.path.join(GAMES_DIR, app_name, 'working')
    if not os.path.exists(os.path.join(working_dir, filename)):
         abort(404) # Return 404 if file doesn't exist in working dir
    # Check for path traversal attempts (basic check)
    if '..' in filename or filename.startswith('/'):
        abort(400)
    return send_from_directory(working_dir, filename)

# Serve files from a game's specific release version directory
@app.route('/games/<app_name>/releases/<version>/<path:filename>')
def serve_game_release_file(app_name, version, filename):
    """Serves files from a specific release version of a game."""
    release_dir = os.path.join(GAMES_DIR, app_name, 'releases', version)
    if not os.path.exists(os.path.join(release_dir, filename)):
        abort(404) # Return 404 if file doesn't exist in release dir
    # Check for path traversal attempts (basic check)
    if '..' in filename or filename.startswith('/'):
        abort(400)
    return send_from_directory(release_dir, filename)

# --- API Endpoints ---

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """
    Lists games based on directory structure, checks for uncommitted changes
    in the 'working' directory, and retrieves release versions from 'releases' folders.
    """
    apps_data = []
    if not os.path.isdir(GAMES_DIR):
        return jsonify({"error": f"Games directory not found: {GAMES_DIR}"}), 500

    try:
        for app_name in os.listdir(GAMES_DIR):
            app_path = os.path.join(GAMES_DIR, app_name)
            if os.path.isdir(app_path):
                working_dir = os.path.join(app_path, 'working')
                releases_dir = os.path.join(app_path, 'releases')

                # --- Check git status in 'working' directory ---
                has_updates = False
                if os.path.isdir(working_dir):
                    # Check status specifically for the working directory path
                    status_stdout, status_stderr, status_exit_code = run_command(f'git status --porcelain "{working_dir}{os.sep}"', cwd=REPO_ROOT)
                    if status_exit_code == 0 and status_stdout:
                        has_updates = True
                    elif status_exit_code != 0:
                        print(f"Warning: git status check failed for {working_dir}: {status_stderr}", file=sys.stderr)
                else:
                     print(f"Warning: Working directory not found for {app_name}: {working_dir}", file=sys.stderr)


                # --- Get release versions from 'releases' subdirectories ---
                all_versions = []
                latest_version = None

                if os.path.isdir(releases_dir):
                    try:
                        version_dirs = [d for d in os.listdir(releases_dir) if os.path.isdir(os.path.join(releases_dir, d))]
                        parsed_versions = []
                        for v_str in version_dirs:
                            try:
                                parsed_versions.append((packaging_version.parse(v_str), v_str))
                            except packaging_version.InvalidVersion:
                                print(f"Warning: Could not parse version from directory name '{v_str}' in {app_name}. Skipping.", file=sys.stderr)

                        # Sort by version, highest first
                        parsed_versions.sort(key=lambda x: x[0], reverse=True)

                        # Extract sorted version strings
                        all_versions = [v_str for version, v_str in parsed_versions]
                        if all_versions:
                            latest_version = all_versions[0] # Highest version is the first after reverse sort

                    except Exception as e:
                         print(f"Error reading releases directory for {app_name}: {e}", file=sys.stderr)

                apps_data.append({
                    "name": app_name,
                    "has_updates": has_updates, # Indicates uncommitted changes in 'working'
                    "latest_version": latest_version, # e.g., '1.0.1'
                    "all_versions": all_versions # List of version strings ['1.0.1', '1.0.0']
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
    # Updated path to release manager script
    script_path = os.path.join(ADMIN_DIR, 'release_manager.py')

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