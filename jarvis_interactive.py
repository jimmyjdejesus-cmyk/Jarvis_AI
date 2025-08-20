"""
🎮 JARVIS AI PHASE 5 - INTERACTIVE INTERFACE

Simple interface to interact with the Jarvis AI Superintelligence Ecosystem
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class JarvisInterface:
    """Interactive interface for Jarvis AI"""
    
    def __init__(self):
        self.running = True
        print("🌟 Jarvis AI Phase 5 - Superintelligence Interface")
        print("=" * 60)
    
    async def start(self):
        """Start the interactive interface"""
        
        try:
            # Initialize basic functionality
            print("🚀 Initializing Jarvis AI...")
            
            # Try to import ecosystem components
            try:
                from jarvis.ecosystem.knowledge_engine import learn_knowledge, ask_question, search_knowledge
                from jarvis.ecosystem.superintelligence import process_complex_task, get_superintelligence_status
                print("✅ Core systems loaded successfully")
                
                self.has_ecosystem = True
                self.learn_knowledge = learn_knowledge
                self.ask_question = ask_question
                self.search_knowledge = search_knowledge
                self.process_complex_task = process_complex_task
                self.get_status = get_superintelligence_status
                
            except ImportError as e:
                print(f"⚠️ Ecosystem not fully available: {e}")
                print("📝 Running in basic mode...")
                self.has_ecosystem = False
            
            # Show menu
            await self.show_menu()
            
        except Exception as e:
            print(f"❌ Error initializing Jarvis: {e}")
            return
    
    async def show_menu(self):
        """Show the main menu"""
        
        while self.running:
            print("\n" + "=" * 40)
            print("🧠 JARVIS AI - MAIN MENU")
            print("=" * 40)
            
            if self.has_ecosystem:
                print("1. 🤔 Ask Jarvis a question")
                print("2. 📚 Teach Jarvis something new")
                print("3. 🔍 Search knowledge base")
                print("4. 🎯 Process complex task")
                print("5. 📊 Check system status")
                print("6. 🎮 Run mini demonstration")
                print("0. 👋 Exit")
            else:
                print("1. 💬 Basic chat mode")
                print("2. 📋 Show system info")
                print("0. 👋 Exit")
            
            try:
                choice = input("\n🎯 Choose an option: ").strip()
                
                if choice == "0":
                    print("👋 Goodbye! Jarvis AI shutting down...")
                    self.running = False
                    break
                
                await self.handle_choice(choice)
                
            except KeyboardInterrupt:
                print("\n⏸️ Interrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def handle_choice(self, choice: str):
        """Handle menu choice"""
        
        if not self.has_ecosystem:
            if choice == "1":
                await self.basic_chat()
            elif choice == "2":
                self.show_system_info()
            return
        
        if choice == "1":
            await self.ask_jarvis()
        elif choice == "2":
            await self.teach_jarvis()
        elif choice == "3":
            await self.search_knowledge()
        elif choice == "4":
            await self.process_task()
        elif choice == "5":
            await self.show_status()
        elif choice == "6":
            await self.mini_demo()
        else:
            print("❓ Invalid choice. Please try again.")
    
    async def ask_jarvis(self):
        """Ask Jarvis a question"""
        print("\n🤔 ASK JARVIS")
        print("-" * 20)
        
        question = input("❓ Your question: ").strip()
        if not question:
            print("⚠️ Please enter a question.")
            return
        
        print("🧠 Jarvis is thinking...")
        try:
            answer = await self.ask_question(question)
            
            print(f"\n💭 Jarvis says:")
            print(f"📝 {answer.get('answer', 'I need more information to answer that.')}")
            
            confidence = answer.get('confidence', 0)
            if confidence > 0:
                print(f"🎯 Confidence: {confidence:.1%}")
            
            entities = answer.get('entities_found', [])
            if entities:
                print(f"🔍 Related concepts: {', '.join(entities[:3])}")
                
        except Exception as e:
            print(f"❌ Error asking question: {e}")
    
    async def teach_jarvis(self):
        """Teach Jarvis something new"""
        print("\n📚 TEACH JARVIS")
        print("-" * 20)
        
        knowledge = input("📖 What would you like to teach Jarvis: ").strip()
        if not knowledge:
            print("⚠️ Please enter some knowledge to teach.")
            return
        
        print("🧠 Jarvis is learning...")
        try:
            result = await self.learn_knowledge(knowledge, "user_teaching")
            
            concepts = result.get('nodes_added', 0)
            relationships = result.get('relationships_added', 0)
            
            print(f"\n✅ Knowledge learned successfully!")
            print(f"📝 New concepts: {concepts}")
            print(f"🔗 New relationships: {relationships}")
            
            if concepts > 0:
                print("🎉 Jarvis is now smarter!")
                
        except Exception as e:
            print(f"❌ Error learning knowledge: {e}")
    
    async def search_knowledge(self):
        """Search the knowledge base"""
        print("\n🔍 SEARCH KNOWLEDGE")
        print("-" * 20)
        
        query = input("🔎 Search for: ").strip()
        if not query:
            print("⚠️ Please enter a search query.")
            return
        
        print("🔍 Searching...")
        try:
            results = await self.search_knowledge(query, max_results=5)
            
            found = results.get('results', [])
            if found:
                print(f"\n📚 Found {len(found)} results:")
                for i, result in enumerate(found[:3], 1):
                    print(f"\n{i}. 📌 {result.get('name', 'Unknown')}")
                    print(f"   📝 {result.get('description', 'No description')[:100]}...")
                    print(f"   🎯 Relevance: {result.get('relevance', 0):.2f}")
            else:
                print("❌ No results found. Try teaching Jarvis about this topic first!")
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
    
    async def process_task(self):
        """Process a complex task"""
        print("\n🎯 COMPLEX TASK PROCESSING")
        print("-" * 30)
        
        task = input("🚀 Describe the task: ").strip()
        if not task:
            print("⚠️ Please describe a task.")
            return
        
        print("📊 Choose complexity level:")
        print("1. Simple (1-3)")
        print("2. Medium (4-6)")
        print("3. Complex (7-10)")
        
        complexity_choice = input("🎯 Choice: ").strip()
        complexity_map = {"1": 3, "2": 5, "3": 8}
        complexity = complexity_map.get(complexity_choice, 5)
        
        print(f"\n🧠 Processing task (complexity {complexity})...")
        try:
            result = await self.process_complex_task(
                description=task,
                complexity=complexity,
                required_capabilities=["reasoning", "analysis"],
                context={"user_request": True}
            )
            
            status = result.get('status', 'unknown')
            print(f"\n📋 Task Status: {status}")
            
            if status == "completed":
                print("✅ Task completed successfully!")
                quality = result.get('quality_score', 0)
                if quality > 0:
                    print(f"🎯 Quality Score: {quality:.1%}")
            else:
                print("⚠️ Task processing encountered issues.")
                
        except Exception as e:
            print(f"❌ Error processing task: {e}")
    
    async def show_status(self):
        """Show system status"""
        print("\n📊 SYSTEM STATUS")
        print("-" * 20)
        
        try:
            status = self.get_status()
            
            print(f"🧠 Intelligence Level: {status.get('superintelligence_level', 'unknown')}")
            print(f"🎯 Overall Intelligence: {status.get('overall_intelligence', 0):.3f}")
            print(f"🔬 Consciousness Level: {status.get('consciousness_level', 0):.3f}")
            
            capabilities = status.get('capabilities', {})
            if capabilities:
                print(f"\n⚡ Top Capabilities:")
                sorted_caps = sorted(capabilities.items(), key=lambda x: x[1], reverse=True)
                for cap, level in sorted_caps[:5]:
                    bar = "█" * int(level * 10) + "░" * (10 - int(level * 10))
                    print(f"   {cap:15s} |{bar}| {level:.2f}")
            
            operations = status.get('active_operations', {})
            if operations:
                print(f"\n🔄 Active Operations:")
                print(f"   📋 Active Tasks: {operations.get('active_tasks', 0)}")
                print(f"   ✅ Completed: {operations.get('completed_tasks', 0)}")
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")
    
    async def mini_demo(self):
        """Run a mini demonstration"""
        print("\n🎮 MINI DEMONSTRATION")
        print("-" * 25)
        
        print("🚀 Running quick capability demo...")
        
        # 1. Teach something
        print("\n1️⃣ Teaching Jarvis about AI...")
        try:
            await self.learn_knowledge(
                "Artificial Intelligence is the simulation of human intelligence in machines",
                "demo"
            )
            print("   ✅ Knowledge learned")
        except:
            print("   ⚠️ Learning unavailable")
        
        # 2. Ask a question
        print("\n2️⃣ Asking about AI...")
        try:
            answer = await self.ask_question("What is artificial intelligence?")
            print(f"   💭 {answer.get('answer', 'Processing...')[:60]}...")
        except:
            print("   ⚠️ Question answering unavailable")
        
        # 3. Process a simple task
        print("\n3️⃣ Processing a simple task...")
        try:
            result = await self.process_complex_task(
                "Analyze the benefits of AI",
                complexity=3,
                required_capabilities=["reasoning"]
            )
            print(f"   🎯 Task {result.get('status', 'processed')}")
        except:
            print("   ⚠️ Task processing unavailable")
        
        print("\n🎉 Mini demo complete!")
    
    async def basic_chat(self):
        """Basic chat mode when ecosystem is not available"""
        print("\n💬 BASIC CHAT MODE")
        print("-" * 20)
        print("(Ecosystem not fully loaded - basic responses only)")
        
        message = input("💬 You: ").strip()
        if not message:
            return
        
        # Simple responses
        responses = {
            "hello": "Hello! I'm Jarvis AI. My full ecosystem isn't loaded yet, but I'm here!",
            "hi": "Hi there! I'm in basic mode right now.",
            "how are you": "I'm running in basic mode. My superintelligence features are loading!",
            "what can you do": "I'm Jarvis AI with superintelligence capabilities, but currently in basic mode.",
            "help": "I can chat basically right now. Try running the full ecosystem for more features!"
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                print(f"🤖 Jarvis: {response}")
                return
        
        print(f"🤖 Jarvis: I heard you say '{message}'. My full capabilities are still loading!")
    
    def show_system_info(self):
        """Show basic system information"""
        print("\n📋 SYSTEM INFORMATION")
        print("-" * 25)
        print("🤖 System: Jarvis AI Phase 5")
        print("🧠 Mode: Basic (Ecosystem Loading)")
        print("📅 Version: 5.0.0")
        print("🔧 Status: Operational")

async def main():
    """Main function"""
    interface = JarvisInterface()
    await interface.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Jarvis AI shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
