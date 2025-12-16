#!/usr/bin/env python3
"""
Utility script to set the OpenAI API key for Jarvis AI
"""
from .tools.key_manager import save_api_key

def main():
    print("Jarvis AI - OpenAI API Key Setup")
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
        print("You can now use cloud-based AI features in Jarvis AI.")
    else:
        print("❌ Failed to save API key. Please try again.")

if __name__ == "__main__":
    main()
