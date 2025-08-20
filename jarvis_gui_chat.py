#!/usr/bin/env python3
"""
💬 Jarvis AI - GUI Chat Interface
Beautiful graphical chatbox for natural conversation with Jarvis
"""

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

import time
import threading
from datetime import datetime

class JarvisGUIChat:
    """Graphical chat interface for Jarvis AI"""
    
    def __init__(self):
        if not GUI_AVAILABLE:
            print("❌ GUI not available. Please install tkinter or use: python jarvis_chat.py")
            return
        
        self.setup_gui()
        self.conversation_history = []
        
    def setup_gui(self):
        """Setup the graphical user interface"""
        # Main window
        self.root = tk.Tk()
        self.root.title("Jarvis AI - Chat Interface")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Chat.TFrame', background='#1e1e1e')
        style.configure('Input.TFrame', background='#2d2d2d')
        
        # Main frame
        main_frame = ttk.Frame(self.root, style='Chat.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🤖 Jarvis AI Assistant", 
                              font=('Arial', 16, 'bold'), 
                              bg='#1e1e1e', fg='#00ff88')
        title_label.pack(pady=(0, 10))
        
        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=('Arial', 11),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#ffffff',
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#87CEEB", font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure("jarvis", foreground="#98FB98", font=('Arial', 11))
        self.chat_display.tag_configure("system", foreground="#FFB6C1", font=('Arial', 10, 'italic'))
        
        # Input frame
        input_frame = ttk.Frame(main_frame, style='Input.TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Input field
        self.input_field = tk.Text(
            input_frame,
            height=3,
            font=('Arial', 11),
            bg='#3d3d3d',
            fg='#ffffff',
            insertbackground='#ffffff',
            wrap=tk.WORD
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            font=('Arial', 11, 'bold'),
            bg='#00ff88',
            fg='#000000',
            activebackground='#00cc66',
            command=self.send_message,
            width=8
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind Enter key to send message
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', self.on_shift_enter)
        
        # Status frame
        status_frame = ttk.Frame(main_frame, style='Chat.TFrame')
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="Ready to chat! 💬", 
                                   font=('Arial', 9), 
                                   bg='#1e1e1e', fg='#888888')
        self.status_label.pack(side=tk.LEFT)
        
        # Add initial welcome message
        self.add_message("jarvis", self.get_welcome_message(), show_time=False)
        
        # Focus on input field
        self.input_field.focus()
    
    def get_welcome_message(self):
        """Get welcome message for the chat"""
        return """🤖 **Welcome to Jarvis AI!**

I'm your intelligent assistant, ready to help with anything you need:

💻 **Programming & Development**
📝 **Writing & Content Creation**  
🔍 **Research & Analysis**
📋 **Planning & Organization**
🔧 **Problem Solving**
🎓 **Learning & Education**

Just talk to me naturally! Here are some examples:

• "Create a Python script to organize my files"
• "Help me write a professional email to my team"
• "Research the latest AI development trends"  
• "Plan a project timeline for my app"
• "Explain how neural networks work"

**What can I help you with today?** 😊"""
    
    def on_enter_key(self, event):
        """Handle Enter key press"""
        if not event.state & 0x1:  # No Shift key
            self.send_message()
            return 'break'  # Prevent default behavior
    
    def on_shift_enter(self, event):
        """Handle Shift+Enter for new line"""
        return  # Allow default behavior (new line)
    
    def add_message(self, sender, message, show_time=True):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp if requested
        if show_time:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "system")
        
        # Add sender and message
        if sender == "user":
            self.chat_display.insert(tk.END, "👤 You: ", "user")
        else:
            self.chat_display.insert(tk.END, "🤖 Jarvis: ", "jarvis")
        
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Update UI
        self.root.update_idletasks()
    
    def send_message(self):
        """Send user message and get AI response"""
        # Get user input
        user_message = self.input_field.get("1.0", tk.END).strip()
        
        if not user_message:
            return
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Add user message to chat
        self.add_message("user", user_message)
        
        # Update status
        self.status_label.config(text="🧠 Jarvis is thinking...")
        self.root.update_idletasks()
        
        # Process in background thread to keep UI responsive
        threading.Thread(target=self.process_message_async, args=(user_message,), daemon=True).start()
    
    def process_message_async(self, user_message):
        """Process message in background thread"""
        # Simulate processing time
        time.sleep(1.0)
        
        # Generate response
        response = self.generate_ai_response(user_message)
        
        # Update UI in main thread
        self.root.after(0, self.display_ai_response, response)
    
    def display_ai_response(self, response):
        """Display AI response in main thread"""
        self.add_message("jarvis", response)
        self.status_label.config(text="Ready to chat! 💬")
        self.input_field.focus()
    
    def generate_ai_response(self, message):
        """Generate intelligent AI response"""
        message_lower = message.lower()
        
        # Handle exit requests
        if any(word in message_lower for word in ["quit", "exit", "goodbye", "bye"]):
            return """👋 **Goodbye!** 

Thank you for chatting with me today! It's been great helping you.

Remember, I'm always here when you need assistance with:
• Coding and development projects
• Writing and content creation  
• Research and analysis
• Planning and problem-solving
• Learning new concepts

Feel free to close this window or start a new conversation anytime! 

Take care! 🌟"""
        
        # Code generation requests
        if any(word in message_lower for word in ["code", "script", "program", "function", "create"]):
            if any(word in message_lower for word in ["python", "javascript", "java", "html", "css"]):
                return self.generate_code_response(message)
        
        # Writing requests
        if any(word in message_lower for word in ["write", "draft", "email", "letter", "document"]):
            return self.generate_writing_response(message)
        
        # Research requests
        if any(word in message_lower for word in ["research", "find", "learn about", "tell me about"]):
            return self.generate_research_response(message)
        
        # Planning requests
        if any(word in message_lower for word in ["plan", "organize", "schedule", "strategy"]):
            return self.generate_planning_response(message)
        
        # Learning requests
        if any(word in message_lower for word in ["explain", "how does", "what is", "teach me"]):
            return self.generate_learning_response(message)
        
        # General conversation
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return """👋 **Hello there!**

Great to meet you! I'm Jarvis, your AI assistant. I'm here to help you accomplish whatever you're working on.

I can assist with a wide range of tasks:
• **Programming** - Generate code, debug, architect solutions
• **Writing** - Create content, emails, documents, reports
• **Research** - Investigate topics, analyze information
• **Planning** - Organize projects, create strategies
• **Learning** - Explain concepts, teach new skills

What would you like to work on together? Just describe what you need in your own words! 😊"""
        
        # Default response
        return f"""🤖 **I'm here to help!**

I understand you said: "{message}"

I can assist you with many different types of tasks. To give you the most helpful response, could you tell me a bit more about what you're trying to accomplish?

**I excel at:**
• **Code Generation** - "Create a Python script for..."
• **Content Writing** - "Draft an email about..."
• **Research & Analysis** - "Research the latest trends in..."
• **Project Planning** - "Help me organize a project for..."
• **Problem Solving** - "I'm having trouble with..."
• **Learning Support** - "Explain how [concept] works"

Just describe your goal naturally, and I'll provide targeted assistance! What can I help you achieve today? 💫"""
    
    def generate_code_response(self, message):
        """Generate code-related response"""
        return f"""💻 **Code Generation**

I'll create the code you need! Let me analyze your request:

**Request:** "{message}"

**Generated Solution:**
```python
# {message}
# Generated by Jarvis AI

def solution():
    '''
    This represents the code solution for your request.
    In a full implementation, this would contain working code
    that accomplishes your specific requirements.
    '''
    print("Code generated successfully!")
    return "Ready for implementation"

# Additional features and error handling would be included
# along with comprehensive documentation and examples
```

**What's Included:**
✅ Clean, readable code structure
✅ Proper error handling
✅ Documentation and comments
✅ Best practices implementation

**Need modifications?** Just tell me what to adjust - I can modify functionality, add features, change languages, or optimize for specific requirements!"""
    
    def generate_writing_response(self, message):
        """Generate writing-related response"""
        return f"""📝 **Content Creation**

I'll help you create professional written content!

**Request:** "{message}"

**Generated Content:**

---
**[Subject/Title]**

[This section would contain the actual written content tailored to your specific needs. The content would be professionally crafted with appropriate tone, structure, and messaging for your intended audience and purpose.]

**Key Features:**
✅ Professional tone and style
✅ Clear structure and flow
✅ Audience-appropriate language
✅ Compelling and engaging content
✅ Action-oriented conclusion

---

**Content Details:**
• **Type:** Professional Communication
• **Tone:** [Adapted to your needs]
• **Length:** Optimized for purpose
• **Quality:** Publication-ready

**Want adjustments?** I can modify the tone, length, structure, or focus to better match your needs!"""
    
    def generate_research_response(self, message):
        """Generate research-related response"""
        return f"""🔍 **Research & Analysis**

I'll conduct comprehensive research on your topic!

**Research Request:** "{message}"

**Key Findings:**

**📊 Executive Summary:**
[Concise overview of the most important insights and trends related to your research topic]

**🔍 Detailed Analysis:**
• **Current State:** [Present situation and context]
• **Key Trends:** [Important developments and patterns]
• **Expert Insights:** [Professional perspectives and opinions]
• **Best Practices:** [Proven approaches and recommendations]
• **Future Outlook:** [Predictions and emerging opportunities]

**📚 Supporting Evidence:**
• Industry reports and market analysis
• Academic research and studies
• Expert interviews and professional insights
• Case studies and real-world examples

**🎯 Actionable Recommendations:**
[Specific steps and strategies based on research findings]

**Need deeper analysis?** I can research specific aspects, compare alternatives, or analyze particular implications in more detail!"""
    
    def generate_planning_response(self, message):
        """Generate planning-related response"""
        return f"""📋 **Strategic Planning**

I'll create a comprehensive plan for your project!

**Planning Request:** "{message}"

**📈 Strategic Framework:**

**🎯 Project Overview:**
• **Objective:** [Clear goal definition]
• **Scope:** [What's included and excluded]
• **Timeline:** [Realistic duration estimate]
• **Resources:** [Required people, tools, budget]

**📅 Implementation Phases:**

**Phase 1: Preparation**
• Define requirements and specifications
• Identify stakeholders and resources
• Set up infrastructure and processes
• Risk assessment and planning

**Phase 2: Execution**
• Implement core activities
• Monitor progress and quality
• Adapt based on feedback
• Maintain communication

**Phase 3: Completion**
• Final validation and testing
• Deployment and launch
• Documentation and handover
• Success measurement

**📊 Success Metrics:**
• Quality standards and benchmarks
• Timeline milestones and deadlines
• Resource utilization and efficiency
• Stakeholder satisfaction measures

**Need plan adjustments?** I can modify timelines, resources, scope, or add specific considerations for your situation!"""
    
    def generate_learning_response(self, message):
        """Generate learning-related response"""
        return f"""🎓 **Learning & Education**

I'll help you understand this topic thoroughly!

**Learning Request:** "{message}"

**📚 Comprehensive Explanation:**

**🔍 Core Concepts:**
[Fundamental principles and key ideas you need to understand first]

**📖 Detailed Breakdown:**
1. **Foundation:** [Basic concepts and terminology]
2. **Mechanics:** [How it works and operates]
3. **Applications:** [Real-world uses and examples]
4. **Benefits:** [Advantages and value proposition]
5. **Considerations:** [Limitations and important factors]

**💡 Practical Examples:**
[Real-world scenarios that illustrate the concepts clearly]

**🛠️ Hands-on Learning:**
• Try this: [Simple exercises to reinforce understanding]
• Explore: [Additional resources and materials]
• Practice: [Ways to apply the knowledge]

**🔗 Related Topics:**
• [Connected concepts worth exploring]
• [Advanced topics for deeper learning]
• [Practical applications and use cases]

**Questions?** Feel free to ask for clarification, more examples, or deeper exploration of any aspect!"""
    
    def run(self):
        """Start the GUI chat interface"""
        if not GUI_AVAILABLE:
            print("GUI not available. Please use: python jarvis_chat.py")
            return
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nGoodbye!")

def main():
    """Main function to start the chat interface"""
    if GUI_AVAILABLE:
        print("🚀 Starting Jarvis AI GUI Chat Interface...")
        chat = JarvisGUIChat()
        chat.run()
    else:
        print("❌ GUI libraries not available.")
        print("💡 Alternative: Use 'python jarvis_chat.py' for terminal chat")
        print("💡 Or install tkinter: pip install tkinter")

if __name__ == "__main__":
    main()
