import subprocess
import argparse
import sys
import os
import shutil # Added for file copying
import re # Add re for version regex matching
from packaging.version import parse as parse_version # Use packaging for robust version comparison

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

# --- Helper functions for index generation ) ---

def find_latest_version(versions):
   """Finds the latest version from a list of version strings."""
   if not versions:
       return None
   # Use packaging.version.parse for robust semantic version comparison
   return max(versions, key=parse_version)

def format_game_name(app_name):
   """Formats the app directory name into a display name."""
   return ' '.join(word.capitalize() for word in app_name.split('-'))

def find_entry_point(directory, app_name):
   """Finds the entry HTML file (app_name.html or index.html) in a directory."""
   preferred_entry = f"{app_name}.html"
   if os.path.exists(os.path.join(directory, preferred_entry)):
       return preferred_entry
   elif os.path.exists(os.path.join(directory, "index.html")):
       return "index.html"
   else:
       return None # No entry point found

# --- Function to update the root index.html ---

def update_root_index(project_root):
   """Generates the root index.html based on latest game releases, including version dropdowns."""
   print("\n--- Starting Root Index Generation ---")
   games_root_dir = os.path.join(project_root, 'games')
   template_path = os.path.join(project_root, 'index.template.html')
   output_path = os.path.join(project_root, 'index.html')

   print(f"Scanning for games in: {games_root_dir}")
   game_list_items_html = [] # Changed variable name for clarity

   if not os.path.exists(games_root_dir):
       print(f"Error: Games directory not found at {games_root_dir}", file=sys.stderr)
       print("Warning: Skipping root index generation.")
       return

   if not os.path.exists(template_path):
       print(f"Error: Template file not found at {template_path}", file=sys.stderr)
       print("Warning: Skipping root index generation.")
       return

   # Iterate through potential game directories
   for app_name in sorted(os.listdir(games_root_dir)): # Sort app names alphabetically
       app_dir = os.path.join(games_root_dir, app_name)
       if not os.path.isdir(app_dir):
           continue

       releases_dir = os.path.join(app_dir, 'releases')
       if not os.path.isdir(releases_dir):
           continue

       # Find and sort all valid version directories
       versions = sorted(
           [
               d for d in os.listdir(releases_dir)
               if os.path.isdir(os.path.join(releases_dir, d)) and re.match(r'^\d+\.\d+\.\d+$', d)
           ],
           key=parse_version,
           reverse=True # Sort descending (latest first)
       )

       if not versions:
           continue

       latest_version = versions[0] # Latest is the first after descending sort
       print(f"  Found game: {app_name}, Versions: {', '.join(versions)}")

       latest_release_dir = os.path.join(releases_dir, latest_version)
       latest_entry_point = find_entry_point(latest_release_dir, app_name)

       if not latest_entry_point:
           print(f"Warning: Could not find entry point for latest version '{latest_version}' of '{app_name}'. Skipping game.")
           continue

       display_name = format_game_name(app_name)
       latest_link_path = f"games/{app_name}/releases/{latest_version}/{latest_entry_point}"

       # Generate dropdown links
       dropdown_links_html = []
       for version in versions:
           version_dir = os.path.join(releases_dir, version)
           entry_point = find_entry_point(version_dir, app_name)
           if entry_point:
               link_path = f"games/{app_name}/releases/{version}/{entry_point}"
               # target="_blank" to open in new window
               dropdown_links_html.append(f'                <a href="{link_path}" target="_blank">{version}</a>')
           else:
                # Optionally add a disabled entry or skip
                dropdown_links_html.append(f'                <span class="disabled-version">{version} (No entry)</span>')


       # Generate the full list item HTML with dropdown structure
       # Using data-target attribute for JS hook
       list_item_html = f"""\
           <li class="game-item">
               <a href="{latest_link_path}" class="game-link">{display_name}</a>
               <div class="version-dropdown-container">
                   <button class="versions-button" data-target="dropdown-{app_name}">Versions</button>
                   <div id="dropdown-{app_name}" class="versions-dropdown-content">
{chr(10).join(dropdown_links_html)}
                   </div>
               </div>
           </li>"""
       game_list_items_html.append(list_item_html)


   if not game_list_items_html:
       print("Warning: No games with valid releases found. Output index.html will have an empty list.")
       generated_list_html = "            <!-- No games found -->"
   else:
       # Indent the generated list items correctly
       generated_list_html = "\n".join(f"    {line}" for item in game_list_items_html for line in item.splitlines())


   # Read template and replace placeholder
   print(f"Reading template file: {template_path}")
   try:
       with open(template_path, 'r', encoding='utf-8') as f:
           template_content = f.read()
   except Exception as e:
       print(f"Error reading template file: {e}", file=sys.stderr)
       print("Warning: Skipping root index generation.")
       return

   print("Generating final index.html content...")
   # Ensure placeholder has correct indentation if needed, but usually it's fine
   final_content = template_content.replace('            <!-- GAME_LIST_PLACEHOLDER -->', generated_list_html)

   # Write the final index.html
   print(f"Writing output file: {output_path}")
   try:
       with open(output_path, 'w', encoding='utf-8') as f:
           f.write(final_content)
       print("Successfully generated index.html.")
   except Exception as e:
       print(f"Error writing output file: {e}", file=sys.stderr)
       print("Warning: Failed to update root index.html.") # Don't exit script

   print("--- Finished Root Index Generation ---")


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

    # --- 3. Generate Root Index ---
    # Check for packaging library before calling update_root_index
    try:
        import packaging.version
    except ImportError:
        print("\nError: The 'packaging' library is required for index generation.", file=sys.stderr)
        print("Please install it using: pip install packaging", file=sys.stderr)
        print("Warning: Skipping root index.html generation.", file=sys.stderr)
    else:
       update_root_index(git_root) # Pass the determined git_root

    sys.exit(0) # Indicate success


if __name__ == "__main__":
    main()