try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
import re

def parse_natural_language_to_actions(nl_command: str):
    """
    Parse a natural language command into browser actions.
    """
    actions = []
    # Example: "Go to google.com and search for cats"
    url_match = re.search(r"go to ([^ ]+)", nl_command.lower())
    if url_match:
        url = url_match.group(1)
        if not url.startswith("http"):
            url = "https://" + url
        actions.append({"type": "goto", "url": url})
    search_match = re.search(r"search for ([^\n]+)", nl_command.lower())
    if search_match:
        # Assume Google search page
        actions.append({"type": "type", "selector": "input[name='q']", "text": search_match.group(1)})
        actions.append({"type": "click", "selector": "input[type='submit']"})
    
    return actions

def trigger_browser_task(nl_command: str):
    """
    Triggers browser automation using a natural language command and returns the result summary.
    """
    try:
        results = automate_browser(nl_command)
        if isinstance(results, dict) and results.get("error"):
            return results["error"]
        elif isinstance(results, dict) and results.get("results"):
            return " | ".join(results["results"])
        else:
            return " | ".join(results) if isinstance(results, list) else str(results)
    except Exception as e:
        return f"Browser automation failed: {str(e)}"

def automate_browser(actions_or_nl):
    """
    Accepts either a list of actions or a natural language command.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright not available - please install with 'pip install playwright'", "success": False}
    
    if isinstance(actions_or_nl, str):
        actions = parse_natural_language_to_actions(actions_or_nl)
    else:
        actions = actions_or_nl
    
    try:
        results = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            for action in actions:
                try:
                    if action['type'] == 'goto':
                        page.goto(action['url'])
                        results.append(f"Went to {action['url']}")
                    elif action['type'] == 'click':
                        page.click(action['selector'])
                        results.append(f"Clicked {action['selector']}")
                    elif action['type'] == 'type':
                        page.fill(action['selector'], action['text'])
                        results.append(f"Typed in {action['selector']}")
                    else:
                        results.append(f"Unknown action: {action['type']}")
                except Exception as e:
                    results.append(f"Error with action {action}: {str(e)}")
            browser.close()
        return {"results": results, "success": True}
    except Exception as e:
        return {"error": f"Browser automation failed: {str(e)}", "success": False}