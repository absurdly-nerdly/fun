import subprocess
import argparse
import sys
import os
import shutil # Added for file copying

def run_command(command, cwd=None):
    """Runs a shell command and returns its stdout, stderr, and return code."""
    try:
        process = subprocess.run(
            command,
            shell=True,
            check=True, # Raise CalledProcessError on non-zero exit code
            capture_output=True,
            text=True,
            cwd=cwd # Run command in the specified directory if provided
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except subprocess.CalledProcessError as e:
        # Return details for caller to handle
        return e.stdout.strip(), e.stderr.strip(), e.returncode
    except Exception as e:
        print(f"An unexpected error occurred running command '{command}': {e}", file=sys.stderr)
        return "", str(e), 1 # Indicate failure

def main():
    parser = argparse.ArgumentParser(description="Create a release archive and git tag for an application.")
    parser.add_argument("app_name", help="The name of the application (e.g., 'balloon-puff').")
    parser.add_argument("version_tag", help="The version tag to create (e.g., '1.0.0').")
    args = parser.parse_args()

    app_name = args.app_name
    version_tag = args.version_tag # This is just the version number like '1.0.0'
    full_tag_name = f"{app_name}-v{version_tag}" # Git tag includes app name and 'v' prefix

    # --- Determine Paths ---
    git_root, _, exit_code = run_command("git rev-parse --show-toplevel")
    if exit_code != 0:
        print(f"Error: Could not determine Git repository root.", file=sys.stderr)
        sys.exit(1)

    games_dir = os.path.join(git_root, 'games')
    app_dir = os.path.join(games_dir, app_name)
    working_dir = os.path.join(app_dir, 'working')
    releases_dir = os.path.join(app_dir, 'releases')
    release_version_dir = os.path.join(releases_dir, version_tag) # Directory named just '1.0.0'

    print(f"Starting release process for {app_name} version {version_tag}")
    print(f"Repository Root: {git_root}")
    print(f"Working Directory: {working_dir}")
    print(f"Target Release Directory: {release_version_dir}")

    # --- Pre-checks ---
    if not os.path.isdir(working_dir):
        print(f"Error: Working directory not found: {working_dir}", file=sys.stderr)
        print("Ensure the game follows the structure defined in .roo/rules/rules.md", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(release_version_dir):
        print(f"Error: Release directory already exists: {release_version_dir}", file=sys.stderr)
        print("Delete the existing directory or choose a different version tag.", file=sys.stderr)
        sys.exit(1)

    # --- 1. Copy Files ---
    try:
        print(f"Copying files from {working_dir} to {release_version_dir}...")
        # ignore_dangling_symlinks=True might be needed on some systems if symlinks cause issues
        shutil.copytree(working_dir, release_version_dir, symlinks=False, ignore=None)
        print("Files copied successfully.")
    except OSError as e:
        print(f"Error copying files: {e}", file=sys.stderr)
        # Clean up potentially partially created directory
        if os.path.exists(release_version_dir):
            try:
                shutil.rmtree(release_version_dir)
                print(f"Cleaned up partially created directory: {release_version_dir}")
            except OSError as cleanup_e:
                print(f"Error cleaning up directory {release_version_dir}: {cleanup_e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during file copy: {e}", file=sys.stderr)
        sys.exit(1)

    # --- 2. Git Tagging ---
    print(f"\nAttempting to create and push Git tag: {full_tag_name}")

    # Check if tag already exists
    print(f"Checking if tag '{full_tag_name}' already exists...")
    stdout, stderr, exit_code = run_command(f"git tag -l {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error checking for existing tag: {stderr}", file=sys.stderr)
        # Consider rolling back file copy? For now, exit.
        sys.exit(1)
    if stdout:
        print(f"Error: Tag '{full_tag_name}' already exists. Files were copied, but tag was not created.", file=sys.stderr)
        # Files are copied, but tag exists. This is an inconsistent state.
        # Maybe offer to delete the copied files? For now, exit.
        sys.exit(1)
    print("Tag does not exist. Proceeding...")

    # Create the tag
    print(f"Creating tag '{full_tag_name}'...")
    stdout, stderr, exit_code = run_command(f"git tag {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error creating tag: {stderr}", file=sys.stderr)
        # Attempt to clean up if tag creation failed partially
        run_command(f"git tag -d {full_tag_name}", cwd=git_root)
        # Consider rolling back file copy? For now, exit.
        sys.exit(1)
    print(f"Tag '{full_tag_name}' created locally.")

    # Push the tag to remote 'fun'
    print(f"Pushing tag '{full_tag_name}' to remote 'fun'...")
    stdout, stderr, exit_code = run_command(f"git push fun {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error pushing tag to fun: {stderr}", file=sys.stderr)
        print(f"Warning: Failed to push tag '{full_tag_name}' to remote. Local tag still exists.", file=sys.stderr)
        # Files copied, local tag created, but push failed. Exit with error.
        sys.exit(1) # Indicate failure

    print(f"\nSuccessfully copied files, created and pushed tag '{full_tag_name}'.")
    sys.exit(0) # Indicate success

if __name__ == "__main__":
    main()