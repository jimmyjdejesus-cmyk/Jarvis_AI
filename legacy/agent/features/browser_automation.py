from playwright.sync_api import sync_playwright
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

    def trigger_browser_task(nl_command: str):
        """
        Triggers browser automation using a natural language command and returns the result summary.
        """
        try:
            results = automate_browser(nl_command)
            return " | ".join(results)
        except Exception as e:
            return f"Browser automation failed: {str(e)}"
    
        # Add more natural language mappings as needed
        return actions

def automate_browser(actions_or_nl):
    """
    Accepts either a list of actions or a natural language command.
    """
    if isinstance(actions_or_nl, str):
        actions = parse_natural_language_to_actions(actions_or_nl)
    else:
        actions = actions_or_nl
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        for action in actions:
            if action['type'] == 'goto':
                page.goto(action['url'])
                results.append(f"Went to {action['url']}")
            elif action['type'] == 'click':
                page.click(action['selector'])
                results.append(f"Clicked {action['selector']}")
            elif action['type'] == 'type':
                page.fill(action['selector'], action['text'])
                results.append(f"Typed in {action['selector']}")
        browser.close()
    return results