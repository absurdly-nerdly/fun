import subprocess
import argparse
import sys
import os

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
        print(f"Error running command: {command}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Output:\n{e.stdout}", file=sys.stderr)
        print(f"Error output:\n{e.stderr}", file=sys.stderr)
        return e.stdout, e.stderr, e.returncode
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return "", str(e), 1 # Indicate failure

def main():
    parser = argparse.ArgumentParser(description="Create and push a git tag for an application release.")
    parser.add_argument("app_name", help="The name of the application (e.g., 'balloon-puff').")
    parser.add_argument("version_tag", help="The version tag to create (e.g., '1.0.0').")
    args = parser.parse_args()

    app_name = args.app_name
    version_tag = args.version_tag
    full_tag_name = f"{app_name}-v{version_tag}"

    # Get the root directory of the Git repository
    git_root, _, exit_code = run_command("git rev-parse --show-toplevel")
    if exit_code != 0:
        print(f"Error: Could not determine Git repository root.", file=sys.stderr)
        sys.exit(1)

    print(f"Attempting to create release tag: {full_tag_name}")

    # 1. Check if tag already exists
    print(f"Checking if tag '{full_tag_name}' already exists...")
    stdout, stderr, exit_code = run_command(f"git tag -l {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error checking for existing tag: {stderr}", file=sys.stderr)
        sys.exit(1)
    if stdout:
        print(f"Error: Tag '{full_tag_name}' already exists. Aborting.", file=sys.stderr)
        sys.exit(1)
    print("Tag does not exist. Proceeding...")

    # 2. Create the tag
    print(f"Creating tag '{full_tag_name}'...")
    stdout, stderr, exit_code = run_command(f"git tag {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error creating tag: {stderr}", file=sys.stderr)
        # Attempt to clean up if tag creation failed partially (unlikely but possible)
        run_command(f"git tag -d {full_tag_name}", cwd=git_root)
        sys.exit(1)
    print(f"Tag '{full_tag_name}' created locally.")

    # 3. Push the tag to remote 'fun'
    print(f"Pushing tag '{full_tag_name}' to remote 'fun'...")
    stdout, stderr, exit_code = run_command(f"git push fun {full_tag_name}", cwd=git_root)
    if exit_code != 0:
        print(f"Error pushing tag to fun: {stderr}", file=sys.stderr)
        # If pushing fails, maybe delete the local tag? Or leave it for manual push?
        # Let's leave it for now, but inform the user.
        print(f"Warning: Failed to push tag '{full_tag_name}' to remote. Local tag still exists.", file=sys.stderr)
        sys.exit(1) # Indicate failure to the calling process

    print(f"Successfully created and pushed tag '{full_tag_name}'.")
    sys.exit(0) # Indicate success

if __name__ == "__main__":
    main()