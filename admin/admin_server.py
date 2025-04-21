from flask import Flask, jsonify, request, send_from_directory
import subprocess
import os
import sys

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


@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Lists games and checks for uncommitted changes within their specific directories."""
    apps = []
    if not os.path.isdir(GAMES_DIR):
        return jsonify({"error": f"Games directory not found: {GAMES_DIR}"}), 500

    try:
        for app_name in os.listdir(GAMES_DIR):
            app_path = os.path.join(GAMES_DIR, app_name)
            if os.path.isdir(app_path):
                # Check git status specifically for changes *within* this app's directory
                # `git status --porcelain games/app_name` lists changes under that path
                stdout, stderr, exit_code = run_command(f'git status --porcelain "{app_path}"', cwd=REPO_ROOT)

                has_updates = False
                if exit_code == 0 and stdout: # If command succeeded and there's output, there are changes
                    has_updates = True
                elif exit_code != 0:
                    # Handle potential errors if needed, e.g., not a git repo
                    print(f"Warning: git status check failed for {app_name}: {stderr}", file=sys.stderr)
                    # Decide how to represent this - maybe an 'error' status?
                    # For now, assume no updates if status check fails.

                apps.append({"name": app_name, "has_updates": has_updates})
        return jsonify(apps)
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