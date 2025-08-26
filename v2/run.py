import asyncio
from v2.agent.core.agent import JarvisAgentV2
from jarvis.logging import configure

async def main():
    # Initialize logging
    configure()

    # Create the v2 agent, which will in turn create the orchestrator
    agent = JarvisAgentV2()

    # Simple interactive loop
    while True:
        request = input("Enter your request: ")
        if request.lower() == "exit":
            break
        result = await agent.handle_request(request)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
