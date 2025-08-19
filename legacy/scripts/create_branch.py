#!/usr/bin/env python3
"""
Jarvis AI Branch Creator

This script helps developers create branches following the Jarvis AI branching strategy.
It creates branches with the correct naming convention and ensures they are created from
the development branch.
"""

import argparse
import os
import subprocess
import time
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True, shell=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Error output: {e.stderr}")
        exit(1)

def create_branch(branch_type, number, description, autonomous=False):
    """Create a branch following the Jarvis AI branching strategy."""
    # Validate branch type
    valid_types = ["feature", "bugfix", "refactor"]
    if not autonomous and branch_type not in valid_types:
        print(f"Error: Branch type must be one of {valid_types}")
        return False
    
    # Format branch name
    if autonomous:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        branch_name = f"jarvis/auto-{timestamp}-{description}"
    else:
        # Replace spaces with hyphens in description and make lowercase
        description = description.replace(" ", "-").lower()
        branch_name = f"{branch_type}/{number}-{description}"
    
    # Check if we're already on the development branch
    current_branch = run_command("git rev-parse --abbrev-ref HEAD")
    
    if current_branch != "development":
        # Switch to development branch and pull latest changes
        print("Switching to development branch...")
        run_command("git checkout development")
        print("Pulling latest changes...")
        run_command("git pull origin development")
    
    # Create the new branch
    print(f"Creating branch: {branch_name}")
    run_command(f"git checkout -b {branch_name}")
    
    print(f"\nSuccessfully created branch: {branch_name}")
    print("\nNext steps:")
    print("1. Make your changes")
    print("2. Commit your changes: git commit -m 'Your message'")
    print("3. Push your branch: git push -u origin " + branch_name)
    print("4. Create a pull request to merge into development")
    
    return True

def main():
    """Main function to parse arguments and create branch."""
    parser = argparse.ArgumentParser(
        description="Create a branch following the Jarvis AI branching strategy"
    )
    
    # Create subparsers for different branch types
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Feature branch parser
    feature_parser = subparsers.add_parser("feature", help="Create a feature branch")
    feature_parser.add_argument("number", help="Issue or feature number")
    feature_parser.add_argument("description", help="Brief description of the feature")
    
    # Bugfix branch parser
    bugfix_parser = subparsers.add_parser("bugfix", help="Create a bugfix branch")
    bugfix_parser.add_argument("number", help="Issue or bug number")
    bugfix_parser.add_argument("description", help="Brief description of the bug fix")
    
    # Refactor branch parser
    refactor_parser = subparsers.add_parser("refactor", help="Create a refactor branch")
    refactor_parser.add_argument("number", help="Issue or refactor number")
    refactor_parser.add_argument("description", help="Brief description of the refactor")
    
    # Autonomous branch parser
    auto_parser = subparsers.add_parser("auto", help="Create an autonomous branch")
    auto_parser.add_argument("description", help="Brief description of the autonomous task")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    if args.command == "auto":
        create_branch("jarvis", None, args.description, autonomous=True)
    else:
        create_branch(args.command, args.number, args.description)

if __name__ == "__main__":
    main()
