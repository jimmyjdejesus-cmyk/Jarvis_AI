#!/usr/bin/env python3

# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/



"""
Utility script to set the OpenAI API key for AdaptiveMind AI
"""
from .tools.key_manager import save_api_key

def main():
    print("AdaptiveMind AI - OpenAI API Key Setup")
    print("=================================")
    print()
    print("This will securely store your OpenAI API key in your system's keyring.")
    print("The key will be used for cloud-based AI features when available.")
    print()

    api_key = input("Enter your OpenAI API key: ").strip()

    if not api_key:
        print("No API key provided. Exiting.")
        return

    if not api_key.startswith("sk-"):
        print("Warning: API key doesn't start with 'sk-'. This might not be a valid OpenAI API key.")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Setup cancelled.")
            return

    success = save_api_key(api_key)
    if success:
        print("✅ OpenAI API key has been securely saved!")
        print("You can now use cloud-based AI features in AdaptiveMind AI.")
    else:
        print("❌ Failed to save API key. Please try again.")

if __name__ == "__main__":
    main()
