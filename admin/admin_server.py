from flask import Flask, jsonify, request, send_from_directory, abort, Response
import subprocess
import os
import sys
import re # For replacing placeholder
# NOTE: You might need to install this: pip install packaging
from packaging import version as packaging_version

app = Flask(__name__)

# Determine the absolute path to the project root (one level up from 'admin')
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(PROJECT_ROOT) # Assuming admin is directly under repo root
GAMES_DIR = os.path.join(REPO_ROOT, 'games')
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

def get_game_details():
    """
    Scans the GAMES_DIR, gathers details about each game including versions and git status.
    Returns a list of dictionaries, one for each game.
    """
    apps_data = []
    if not os.path.isdir(GAMES_DIR):
        print(f"Error: Games directory not found: {GAMES_DIR}", file=sys.stderr)
        return [] # Return empty list if games dir doesn't exist

    try:
        for app_name in os.listdir(GAMES_DIR):
            app_path = os.path.join(GAMES_DIR, app_name)
            if os.path.isdir(app_path):
                working_dir = os.path.join(app_path, 'working')
                releases_dir = os.path.join(app_path, 'releases')

                # --- Check git status in 'working' directory ---
                has_updates = False
                if os.path.isdir(working_dir):
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

                        parsed_versions.sort(key=lambda x: x[0], reverse=True)
                        all_versions = [v_str for version, v_str in parsed_versions]
                        if all_versions:
                            latest_version = all_versions[0]
                    except Exception as e:
                         print(f"Error reading releases directory for {app_name}: {e}", file=sys.stderr)

                # --- Determine Entry Point (Simple Guess) ---
                # Assume <app_name>.html or index.html exists in working/release dirs
                # A more robust solution might check for specific files
                entry_point = f"{app_name}.html"
                # Basic check if the assumed entry point exists in working dir, otherwise default to index.html
                # This check isn't perfect as the entry point might differ between versions
                if os.path.isdir(working_dir) and not os.path.exists(os.path.join(working_dir, entry_point)):
                     entry_point = "index.html" # Fallback

                apps_data.append({
                    "name": app_name,
                    "has_updates": has_updates,
                    "latest_version": latest_version,
                    "all_versions": all_versions,
                    "entry_point": entry_point # Store assumed entry point
                })
        return apps_data
    except Exception as e:
        print(f"Error scanning games directory: {e}", file=sys.stderr)
        return [] # Return empty list on error

# --- Static File Serving ---

@app.route('/')
def index_page():
    """Serves the main index HTML page, dynamically injecting game links."""
    try:
        template_path = os.path.join(REPO_ROOT, 'index.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        game_details = get_game_details()
        game_list_html = ""

        if not game_details:
            game_list_html = "<li>No games found or error loading games.</li>"
        else:
            for game in game_details:
                app_name = game['name']
                entry_point = game['entry_point']
                link_url = f"/games/{app_name}/working/{entry_point}" # Default to working
                link_text = f"{app_name.replace('-', ' ').title()} (Working)"

                if game['latest_version']:
                    link_url = f"/games/{app_name}/releases/{game['latest_version']}/{entry_point}"
                    link_text = f"{app_name.replace('-', ' ').title()} (v{game['latest_version']})"
                elif not os.path.isdir(os.path.join(GAMES_DIR, app_name, 'working')):
                     link_text = f"{app_name.replace('-', ' ').title()} (No working or released version found)"
                     link_url = "#" # No valid link

                # Basic structure, assuming similar style to original index.html
                # TODO: Add creation date/author if needed (would require storing metadata)
                game_list_html += f"""
                <li>
                    <a href="{link_url}">{link_text}</a>
                </li>
                """

        # Replace placeholder in the template
        # Use a specific, unique placeholder comment
        placeholder = "<!-- GAME_LIST_PLACEHOLDER -->"
        final_content = template_content.replace(placeholder, game_list_html)

        return Response(final_content, mimetype='text/html')

    except FileNotFoundError:
        print(f"Error: index.html template not found at {template_path}", file=sys.stderr)
        abort(404)
    except Exception as e:
        print(f"Error generating index page: {e}", file=sys.stderr)
        abort(500)


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
         abort(404)
    if '..' in filename or filename.startswith('/'): abort(400)
    return send_from_directory(working_dir, filename)

# Serve files from a game's specific release version directory
@app.route('/games/<app_name>/releases/<version>/<path:filename>')
def serve_game_release_file(app_name, version, filename):
    """Serves files from a specific release version of a game."""
    release_dir = os.path.join(GAMES_DIR, app_name, 'releases', version)
    if not os.path.exists(os.path.join(release_dir, filename)):
        abort(404)
    if '..' in filename or filename.startswith('/'): abort(400)
    return send_from_directory(release_dir, filename)

# --- API Endpoints ---

@app.route('/api/apps', methods=['GET'])
def get_apps():
    """API endpoint to get game details."""
    apps_data = get_game_details()
    if not apps_data:
        # You might want to return a specific error structure if get_game_details failed internally
        # For now, just return empty list or a generic error if needed
        pass # get_game_details handles printing errors
    return jsonify(apps_data)


@app.route('/api/release', methods=['POST'])
def create_release():
    """Triggers the release manager script."""
    data = request.get_json()
    if not data or 'app_name' not in data or 'version_tag' not in data:
        return jsonify({"error": "Missing 'app_name' or 'version_tag' in request body"}), 400

    app_name = data['app_name']
    version_tag = data['version_tag']
    script_path = os.path.join(ADMIN_DIR, 'release_manager.py') # Path inside admin dir

    if not os.path.isfile(script_path):
         return jsonify({"error": f"Release script not found: {script_path}"}), 500

    try:
        command = f'"{sys.executable}" "{script_path}" "{app_name}" "{version_tag}"'
        print(f"Running command: {command}")
        stdout, stderr, exit_code = run_command(command, cwd=REPO_ROOT)
        print(f"Script stdout:\n{stdout}")
        print(f"Script stderr:\n{stderr}")
        print(f"Script exit code: {exit_code}")

        if exit_code == 0:
            return jsonify({"success": True, "message": f"Release {version_tag} for {app_name} created successfully.", "details": stdout})
        else:
            error_details = f"Exit Code: {exit_code}\nOutput:\n{stdout}\nError Output:\n{stderr}"
            return jsonify({"success": False, "message": f"Failed to create release {version_tag} for {app_name}.", "details": error_details}), 500

    except Exception as e:
        print(f"Error calling release script: {e}", file=sys.stderr)
        return jsonify({"success": False, "message": "An unexpected error occurred while trying to create the release."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)