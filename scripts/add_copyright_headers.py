#!/usr/bin/env python3
"""
Walk the repository and add a simple CC-BY 4.0 notice header to text files that are missing it.

This is a helper script for zero-cost IP protection. Use carefully — review diffs before committing.
"""
import os
from pathlib import Path

HEADER = """
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.
"""

EXCLUDE = {".git", "venv", "env", "__pycache__", "node_modules"}


def should_process(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part in EXCLUDE for part in path.parts):
        return False
    if path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".tar"}:
        return False
    return True


def has_header(text: str) -> bool:
    return "Copyright (c)" in text or "Creative Commons" in text


def add_header(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if has_header(text):
        return False
    new = HEADER + "\n" + text
    path.write_text(new, encoding="utf-8")
    return True


def main(root: str = "."):
    rootp = Path(root)
    modified = []
    for p in rootp.rglob("*"):
        try:
            if should_process(p) and add_header(p):
                modified.append(str(p))
        except Exception:
            continue
    print(f"Added headers to {len(modified)} files")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    main(args.root)
#!/usr/bin/env python3
"""
Add copyright headers to all code files in the AdaptiveMind framework.
This script adds the required copyright notice to Python, JavaScript, YAML, and other code files.
"""

import os
import re
from pathlib import Path

# Copyright header template
COPYRIGHT_HEADER = '''# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

'''

# File extensions to process
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
    '.yml', '.yaml', '.json', '.toml', '.ini', '.cfg', '.conf'
}

def has_copyright_header(content):
    """Check if file already has copyright header."""
    return 'AdaptiveMind Framework' in content and 'Copyright (c) 2025' in content

def add_copyright_header(content, file_path):
    """Add copyright header to file content."""
    # Skip if already has header
    if has_copyright_header(content):
        return content, False
    
    # Add header after shebang if present
    lines = content.split('\n')
    
    # Check for shebang
    if lines and lines[0].startswith('#!'):
        header_lines = COPYRIGHT_HEADER.split('\n')
        new_lines = [lines[0]] + [''] + header_lines + [''] + lines[1:]
    else:
        header_lines = COPYRIGHT_HEADER.split('\n')
        new_lines = header_lines + [''] + lines
    
    return '\n'.join(new_lines), True

def process_file(file_path):
    """Process a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        new_content, was_modified = add_copyright_header(content, file_path)
        
        if was_modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✓ Added copyright header: {file_path}")
            return True
        else:
            print(f"⚬ Already has header: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to add copyright headers to all code files."""
    print("AdaptiveMind Framework - Copyright Header Addition")
    print("=" * 50)
    
    # Get current directory
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    
    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules',
        '.venv', 'venv', 'env', '.env', 'build', 'dist', '.tox'
    }
    
    # Files to skip
    skip_files = {
        'LICENSE', 'README.md', '.gitignore', 'setup.py', 'pyproject.toml',
        'requirements.txt', 'package.json', '.gitmodules'
    }
    
    processed_count = 0
    modified_count = 0
    
    # Walk through all files
    for root, dirs, files in os.walk(project_root):
        # Remove skip directories from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            
            # Skip if in skip list
            if file in skip_files:
                continue
            
            # Check if file has code extension
            if any(file_path.suffix.lower() == ext for ext in CODE_EXTENSIONS):
                processed_count += 1
                if process_file(file_path):
                    modified_count += 1
    
    print("\n" + "=" * 50)
    print(f"Processing complete!")
    print(f"Files processed: {processed_count}")
    print(f"Files modified: {modified_count}")
    print(f"Files unchanged: {processed_count - modified_count}")
    
    print("\nNext steps:")
    print("1. Replace 'Jimmy De Jesus' with your actual name in all files")
    print("2. Replace '[username]' with your GitHub username")
    print("3. Review the changes with: git diff")
    print("4. Commit the changes with timestamp")

if __name__ == "__main__":
    main()
