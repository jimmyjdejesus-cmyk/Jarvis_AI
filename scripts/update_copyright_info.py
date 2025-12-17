#!/usr/bin/env python3

# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Update existing copyright headers to a new author string.

Example: python scripts/update_copyright_info.py "Jimmy De Jesus"
"""
import re
from pathlib import Path

TARGET = "Jimmy De Jesus"
PATTERN = re.compile(r"Copyright \(c\) .*", re.IGNORECASE)


def replace_header(path: Path, new_name: str) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "Copyright (c)" not in text:
        return False
    new_text = PATTERN.sub(f"Copyright (c) {new_name}", text)
    if new_text == text:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def main(root: str = ".", new_name: str = TARGET):
    rootp = Path(root)
    modified = []
    for p in rootp.rglob("*"):
        try:
            if p.is_file() and replace_header(p, new_name):
                modified.append(str(p))
        except Exception:
            continue
    print(f"Updated copyright in {len(modified)} files")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("new_name", nargs="?", default=TARGET)
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    main(args.root, args.new_name)
#!/usr/bin/env python3
"""
Update copyright information in all files to replace placeholder names with actual names.
"""

import os
import re
from pathlib import Path

def update_copyright_info(content):
    """Replace placeholder copyright information with actual information."""
    # Replace Jimmy De Jesus and Jimmy De Jesus with actual name
    updated_content = content.replace('Jimmy De Jesus', 'Jimmy De Jesus')
    updated_content = updated_content.replace('Jimmy De Jesus', 'Jimmy De Jesus')
    
    return updated_content

def process_file(file_path):
    """Process a single file to update copyright information."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check if file contains placeholder copyright information
        if 'Jimmy De Jesus' in content or 'Jimmy De Jesus' in content:
            updated_content = update_copyright_info(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✓ Updated copyright info: {file_path}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to update copyright information in all files."""
    print("AdaptiveMind Framework - Updating Copyright Information")
    print("=" * 60)
    print("Updating copyright placeholders to:")
    print("- Name: Jimmy De Jesus")
    print("- Company: Bravetto")
    print("=" * 60)
    
    # Get current directory
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules',
        '.venv', 'venv', 'env', '.env', 'build', 'dist', '.tox',
        '.venv-1'
    }
    
    # Files to skip
    skip_files = {
        '.gitignore'
    }
    
    processed_count = 0
    updated_count = 0
    
    # Walk through all files
    for root, dirs, files in os.walk(project_root):
        # Remove skip directories from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip if in skip list
            if file in skip_files:
                continue
            
            # Skip binary files and very large files
            if file_path.suffix.lower() in {'.pyc', '.pyo', '.so', '.dll', '.exe', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.pdf', '.zip', '.tar', '.gz'}:
                continue
                
            try:
                # Check file size (skip files larger than 10MB)
                if file_path.stat().st_size > 10 * 1024 * 1024:
                    continue
                    
                processed_count += 1
                if process_file(file_path):
                    updated_count += 1
                    
            except (OSError, PermissionError):
                continue
    
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"Files checked: {processed_count}")
    print(f"Files updated: {updated_count}")
    print(f"Files unchanged: {processed_count - updated_count}")
    
    print("\nNext steps:")
    print("1. Review changes with: git diff")
    print("2. Commit the changes with timestamp")
    print("3. Your copyright information is now properly updated!")

if __name__ == "__main__":
    main()
