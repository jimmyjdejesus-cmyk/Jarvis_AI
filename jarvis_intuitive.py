#!/usr/bin/env python3
"""
💬 Jarvis AI - Intuitive Conversational Chat
Natural, flowing conversation with your AI assistant
"""

import time
import random
from datetime import datetime

class IntuitiveChatbot:
    """Truly conversational AI assistant"""
    
    def __init__(self):
        self.conversation_context = []
        self.user_name = None
        self.current_task = None
        self.personality = {
            "helpful": True,
            "casual": True, 
            "proactive": True,
            "remembers_context": True
        }
        
    def chat_naturally(self, user_input):
        """Have a natural conversation"""
        # Track conversation context
        self.conversation_context.append(user_input.lower())
        
        # Determine conversation style
        input_lower = user_input.lower()
        
        # Very casual/short inputs
        if len(user_input.strip()) < 15:
            return self.handle_short_input(user_input)
        
        # Detect if user is frustrated or confused
        if any(word in input_lower for word in ["not working", "broken", "error", "help", "stuck", "confused"]):
            return self.handle_frustrated_user(user_input)
        
        # Check for code/technical requests
        if any(word in input_lower for word in ["code", "script", "function", "bug", "debug"]):
            return self.handle_code_chat(user_input)
        
        # Check for planning/organizing
        if any(word in input_lower for word in ["plan", "organize", "schedule", "project"]):
            return self.handle_planning_chat(user_input)
        
        # Check for learning/explanation requests
        if any(word in input_lower for word in ["explain", "how", "what", "why", "learn"]):
            return self.handle_learning_chat(user_input)
        
        # Default conversational response
        return self.handle_general_chat(user_input)
    
    def handle_short_input(self, user_input):
        """Handle short, casual inputs"""
        input_lower = user_input.lower().strip()
        
        if input_lower in ["hi", "hello", "hey"]:
            return random.choice([
                "Hey! What's on your mind today?",
                "Hi there! What can we work on together?", 
                "Hello! Ready to tackle something interesting?",
                "Hey! What's the plan today?"
            ])
        
        elif input_lower in ["thanks", "thank you", "thx"]:
            return random.choice([
                "You're welcome! Anything else I can help with?",
                "Happy to help! What's next?",
                "No problem! Got any other questions?",
                "Glad I could help! What else are you working on?"
            ])
        
        elif input_lower in ["ok", "okay", "got it", "cool"]:
            return random.choice([
                "Great! What should we do next?",
                "Perfect! Want to tackle something else?",
                "Awesome! Any other questions?",
                "Cool! What else can I help you with?"
            ])
        
        elif input_lower in ["yes", "yeah", "yep", "sure"]:
            return "Perfect! Go ahead and tell me what you need."
        
        elif input_lower in ["no", "nope", "nah"]:
            return "No worries! Let me know if you change your mind or need help with something else."
        
        else:
            return f"I hear you saying '{user_input}' - want to tell me more about what you're thinking?"
    
    def handle_frustrated_user(self, user_input):
        """Handle when user seems frustrated"""
        return f"""I can tell you might be running into some issues. Let's figure this out together!

What you said: "{user_input}"

Here's how I can help:
• If something's not working, I can debug it step by step
• If you're stuck on a concept, I can explain it differently  
• If you need a different approach, I can suggest alternatives
• If you just need to vent, I'm here to listen!

What's the main thing that's bugging you right now?"""
    
    def handle_code_chat(self, user_input):
        """Handle code-related conversation naturally"""
        input_lower = user_input.lower()
        
        # Extract what they want to do
        if "create" in input_lower or "make" in input_lower or "build" in input_lower:
            action = "create"
        elif "fix" in input_lower or "debug" in input_lower or "error" in input_lower:
            action = "debug"
        elif "improve" in input_lower or "optimize" in input_lower:
            action = "optimize"
        else:
            action = "help"
        
        responses = {
            "create": f"""Ah, you want to build something! I love creating code.

From what you said: "{user_input}"

I'm thinking we could approach this by:
1. First figuring out exactly what you want it to do
2. Choosing the right tools and approach
3. Building it step by step
4. Testing it to make sure it works

What's the main goal here? Like, what problem are you trying to solve?""",

            "debug": f"""Debugging time! Nothing more satisfying than fixing code that's acting up.

You mentioned: "{user_input}"

Let's troubleshoot this together:
• What's it supposed to do vs. what's actually happening?
• Any error messages I should know about?
• Want to show me the code that's giving you trouble?

I'm pretty good at spotting these things - let's get it working!""",

            "optimize": f"""Nice! Making code better is one of my favorite things.

Based on what you said: "{user_input}"

We could look at:
• Speed - making it run faster
• Memory - using less resources  
• Readability - making it cleaner
• Functionality - adding cool features

What's your priority here? Performance, cleanliness, or something else?""",

            "help": f"""I'm here to help with whatever coding challenge you've got!

From your message: "{user_input}"

Just let me know:
• What programming language are we working with?
• What's the end goal?
• Are you stuck on a specific part?

No matter how complex or simple - I'm ready to dive in with you!"""
        }
        
        return responses[action]
    
    def handle_planning_chat(self, user_input):
        """Handle planning conversations"""
        return f"""Planning mode activated! I love organizing stuff.

What you're thinking: "{user_input}"

Let me ask a few quick questions to get us rolling:
• Is this a work project, personal goal, or something else?
• What's your timeline looking like?
• Any specific challenges you're anticipating?

I'm great at breaking big things into manageable chunks and keeping track of all the moving pieces. Plus I can help you stay realistic about timelines (I've seen a lot of overly optimistic plans! 😄)

What's the most important thing to get right with this plan?"""
    
    def handle_learning_chat(self, user_input):
        """Handle learning/explanation requests"""
        return f"""Ooh, learning time! I love explaining things.

Your question: "{user_input}"

Before I dive into a long explanation - how familiar are you with this topic? Like:
• Complete beginner - start from the very basics
• Some experience - skip the intro stuff  
• Pretty knowledgeable - just need specific details
• Expert level - let's get technical

Also, are you more of a:
• Visual learner (diagrams, examples)
• Hands-on learner (let's build something)
• Theory person (understand the why first)

I want to explain this in a way that actually clicks for you!"""
    
    def handle_general_chat(self, user_input):
        """Handle general conversation"""
        # Look for context clues
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["tired", "busy", "stressed", "overwhelmed"]):
            return f"""Sounds like you've got a lot going on! 

What you mentioned: "{user_input}"

Want to talk about it? Sometimes it helps to just get things out of your head. Or if you prefer, I can help you tackle whatever's on your plate - maybe break it down into smaller, less overwhelming pieces?

What would be most helpful right now?"""
        
        elif any(word in input_lower for word in ["excited", "pumped", "awesome", "great"]):
            return f"""I love the energy! 

You said: "{user_input}"

That enthusiasm is contagious! What's got you so excited? Is there something cool we could work on together while you're feeling motivated?

I'm ready to dive into whatever you've got in mind!"""
        
        else:
            return f"""I'm listening! 

From what you're saying: "{user_input}"

I'm picking up on a few things here, but I want to make sure I understand what you're really getting at. 

Is this something you want to:
• Work on together right now?
• Plan out for later?
• Just talk through to get clarity?
• Get my thoughts on?

What would be most useful for you?"""

def main():
    """Start the intuitive chat experience"""
    print("💬 " + "="*60)
    print("  JARVIS - Let's Chat Naturally")
    print("="*64)
    
    jarvis = IntuitiveChatbot()
    
    print("\n🤖 Hey! I'm Jarvis. Let's just chat - no formalities needed.")
    print("Talk to me like you would a friend who happens to be really good with tech stuff.")
    print("Type 'bye' when you're done.\n")
    
    while True:
        try:
            # Simple, clean input prompt
            user_input = input("💬 ").strip()
            
            if not user_input:
                print("🤖 Still here! What's up?")
                continue
            
            if user_input.lower() in ['bye', 'goodbye', 'quit', 'exit']:
                print("\n🤖 Cool, catch you later! Feel free to come back anytime.")
                break
            
            # Brief thinking indicator
            print("🤔 ", end="", flush=True)
            time.sleep(0.3)  # Just a quick pause, not overwhelming
            print("\b\b", end="", flush=True)  # Clear the thinking indicator
            
            # Get natural response
            response = jarvis.chat_naturally(user_input)
            print(f"🤖 {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n🤖 No worries! Chat with you later! 👋")
            break
        except Exception as e:
            print(f"\n🤖 Oops, something weird happened on my end. Want to try that again?")

if __name__ == "__main__":
    main()
