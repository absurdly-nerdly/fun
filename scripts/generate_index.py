# Purpose: Generates the root index.html file by finding all releases
#          of each game in the games/ directory, linking to the latest,
#          and providing a dropdown for all versions.
# Usage: Run this script from the repository root to update index.html
#        for static hosting (like GitHub Pages).

import os
import sys
import re
try:
    from packaging.version import parse as parse_version
except ImportError:
    print("Error: The 'packaging' library is required.", file=sys.stderr)
    print("Please install it using: pip install packaging", file=sys.stderr)
    sys.exit(1)

# --- Helper functions ---

def find_latest_version(versions):
   """Finds the latest version from a list of version strings."""
   if not versions:
       return None
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

# --- Main index generation function ---

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
       for version in versions: # Iterate through sorted versions (latest first)
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


if __name__ == "__main__":
    # Determine project root (assuming script is in 'scripts' subdir)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    # Call the main generation function
    update_root_index(project_root)