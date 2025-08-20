#!/usr/bin/env python3
"""
🎮 Jarvis AI - Quick Launcher
The easiest way to interact with your superintelligent AI assistant!
"""

import os
import sys

def main():
    print("🚀 Jarvis AI Phase 5 - Quick Launcher")
    print("=" * 50)
    print()
    print("Choose your interaction method:")
    print()
    print("1. 🎯 Simple Demo (Recommended)")
    print("   - User-friendly interface")
    print("   - No complex dependencies")
    print("   - Perfect for first experience")
    print()
    print("2. 🔬 Full Ecosystem Demo")
    print("   - Complete integrated system")
    print("   - All Phase 5 components")
    print("   - Advanced capabilities")
    print()
    print("3. 💬 Interactive Mode")
    print("   - Direct conversation interface")
    print("   - Real-time responses")
    print("   - Streamlined experience")
    print()
    print("4. 📖 Read Instructions")
    print("   - Complete interaction guide")
    print("   - Tips and examples")
    print("   - Feature overview")
    print()
    print("5. 🚪 Exit")
    print()
    
    while True:
        choice = input("🎯 Your choice (1-5): ").strip()
        
        if choice == "1":
            print("\n🎯 Launching Simple Demo...")
            os.system("python jarvis_simple_demo.py")
            break
        elif choice == "2":
            print("\n🔬 Launching Full Ecosystem...")
            os.system("python demo_phase5_complete.py")
            break
        elif choice == "3":
            print("\n💬 Launching Interactive Mode...")
            os.system("python jarvis_interactive.py")
            break
        elif choice == "4":
            print("\n📖 Opening Instructions...")
            if os.path.exists("HOW_TO_INTERACT.md"):
                with open("HOW_TO_INTERACT.md", "r", encoding="utf-8") as f:
                    print(f.read())
            else:
                print("Instructions file not found!")
            print("\nPress Enter to continue...")
            input()
            main()  # Return to menu
            break
        elif choice == "5":
            print("\n🚪 Goodbye! Thanks for exploring Jarvis AI!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
