#!/usr/bin/env python3
"""
API Integration Examples
Connect your workflows to external APIs and services.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class APIIntegrationManager:
    """Manage API integrations for workflows."""
    
    def __init__(self):
        self.api_configs = {}
        self.rate_limits = {}
        self.cache = {}
        self.cache_duration = 300  # 5 minutes default
    
    def add_api_config(self, name: str, base_url: str, headers: Dict = None, 
                      rate_limit: int = 60, auth_type: str = None):
        """Add API configuration."""
        self.api_configs[name] = {
            'base_url': base_url.rstrip('/'),
            'headers': headers or {},
            'auth_type': auth_type,
            'rate_limit': rate_limit,  # requests per minute
            'last_request': 0
        }
        print(f"✅ Added API config: {name}")
    
    def make_request(self, api_name: str, endpoint: str, method: str = 'GET', 
                    data: Dict = None, params: Dict = None, use_cache: bool = True):
        """Make API request with rate limiting and caching."""
        
        if api_name not in self.api_configs:
            raise ValueError(f"API config '{api_name}' not found")
        
        config = self.api_configs[api_name]
        
        # Check rate limiting
        self._check_rate_limit(api_name)
        
        # Check cache
        cache_key = f"{api_name}_{endpoint}_{json.dumps(params, sort_keys=True)}"
        if use_cache and cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if time.time() - cache_data['timestamp'] < self.cache_duration:
                print(f"📋 Using cached response for {api_name}")
                return cache_data['response']
        
        # Build URL
        url = f"{config['base_url']}/{endpoint.lstrip('/')}"
        
        # Prepare headers
        headers = config['headers'].copy()
        if config.get('auth_type') == 'bearer' and 'BEARER_TOKEN' in os.environ:
            headers['Authorization'] = f"Bearer {os.environ['BEARER_TOKEN']}"
        
        try:
            print(f"🌐 Making {method} request to {api_name}: {endpoint}")
            
            # Make request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method != 'GET' else None,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json() if response.content else {}
            
            # Update rate limit tracking
            self.api_configs[api_name]['last_request'] = time.time()
            
            # Cache response
            if use_cache:
                self.cache[cache_key] = {
                    'response': result,
                    'timestamp': time.time()
                }
            
            print(f"✅ API request successful: {response.status_code}")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {str(e)}")
            raise
    
    def _check_rate_limit(self, api_name: str):
        """Check and enforce rate limiting."""
        config = self.api_configs[api_name]
        
        if config['last_request'] > 0:
            time_since_last = time.time() - config['last_request']
            min_interval = 60.0 / config['rate_limit']  # seconds between requests
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                print(f"⏳ Rate limiting: waiting {sleep_time:.1f} seconds")
                time.sleep(sleep_time)

# Example API Integrations
class WeatherAPIIntegration:
    """Weather API integration example."""
    
    def __init__(self, api_manager: APIIntegrationManager):
        self.api_manager = api_manager
        self.setup_api()
    
    def setup_api(self):
        """Setup weather API configuration."""
        # Using OpenWeatherMap as example (free tier)
        api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        
        self.api_manager.add_api_config(
            name='weather',
            base_url='https://api.openweathermap.org/data/2.5',
            headers={'Content-Type': 'application/json'},
            rate_limit=60  # 60 requests per minute
        )
    
    def get_current_weather(self, city: str, country: str = None):
        """Get current weather for a city."""
        params = {
            'q': f"{city},{country}" if country else city,
            'appid': os.getenv('OPENWEATHER_API_KEY', 'demo_key'),
            'units': 'metric'
        }
        
        try:
            result = self.api_manager.make_request('weather', 'weather', params=params)
            
            return {
                'city': result.get('name', city),
                'temperature': result['main']['temp'],
                'description': result['weather'][0]['description'],
                'humidity': result['main']['humidity'],
                'pressure': result['main']['pressure']
            }
        except Exception as e:
            print(f"❌ Weather API error: {e}")
            return None
    
    def get_forecast(self, city: str, days: int = 5):
        """Get weather forecast."""
        params = {
            'q': city,
            'appid': os.getenv('OPENWEATHER_API_KEY', 'demo_key'),
            'units': 'metric',
            'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        try:
            result = self.api_manager.make_request('weather', 'forecast', params=params)
            
            forecasts = []
            for item in result.get('list', []):
                forecasts.append({
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description']
                })
            
            return forecasts
        except Exception as e:
            print(f"❌ Forecast API error: {e}")
            return []

class NewsAPIIntegration:
    """News API integration example."""
    
    def __init__(self, api_manager: APIIntegrationManager):
        self.api_manager = api_manager
        self.setup_api()
    
    def setup_api(self):
        """Setup news API configuration."""
        self.api_manager.add_api_config(
            name='news',
            base_url='https://newsapi.org/v2',
            headers={
                'X-API-Key': os.getenv('NEWS_API_KEY', 'demo_key'),
                'Content-Type': 'application/json'
            },
            rate_limit=100  # 100 requests per minute
        )
    
    def get_top_headlines(self, country: str = 'us', category: str = None, sources: str = None):
        """Get top news headlines."""
        params = {
            'country': country,
            'pageSize': 20
        }
        
        if category:
            params['category'] = category
        if sources:
            params['sources'] = sources
            params.pop('country')  # Can't use country with sources
        
        try:
            result = self.api_manager.make_request('news', 'top-headlines', params=params)
            
            articles = []
            for article in result.get('articles', []):
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'published_at': article['publishedAt']
                })
            
            return articles
        except Exception as e:
            print(f"❌ News API error: {e}")
            return []
    
    def search_news(self, query: str, language: str = 'en', sort_by: str = 'publishedAt'):
        """Search for news articles."""
        params = {
            'q': query,
            'language': language,
            'sortBy': sort_by,
            'pageSize': 20
        }
        
        try:
            result = self.api_manager.make_request('news', 'everything', params=params)
            
            articles = []
            for article in result.get('articles', []):
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'published_at': article['publishedAt']
                })
            
            return articles
        except Exception as e:
            print(f"❌ News search error: {e}")
            return []

class SlackIntegration:
    """Slack API integration for notifications."""
    
    def __init__(self, api_manager: APIIntegrationManager):
        self.api_manager = api_manager
        self.setup_api()
    
    def setup_api(self):
        """Setup Slack API configuration."""
        self.api_manager.add_api_config(
            name='slack',
            base_url='https://slack.com/api',
            headers={
                'Authorization': f"Bearer {os.getenv('SLACK_BOT_TOKEN', 'demo_token')}",
                'Content-Type': 'application/json'
            },
            rate_limit=120  # Slack allows more requests
        )
    
    def send_message(self, channel: str, text: str, blocks: List = None):
        """Send message to Slack channel."""
        data = {
            'channel': channel,
            'text': text
        }
        
        if blocks:
            data['blocks'] = blocks
        
        try:
            result = self.api_manager.make_request('slack', 'chat.postMessage', 
                                                 method='POST', data=data, use_cache=False)
            
            if result.get('ok'):
                print(f"✅ Slack message sent to {channel}")
                return True
            else:
                print(f"❌ Slack error: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Slack API error: {e}")
            return False
    
    def create_workflow_notification(self, workflow_name: str, status: str, details: str = None):
        """Create a workflow status notification."""
        emoji = "✅" if status == "success" else "❌" if status == "error" else "⏳"
        
        message = f"{emoji} *{workflow_name}* - {status.title()}"
        if details:
            message += f"\n{details}"
        
        return self.send_message('#workflows', message)

# Integration Workflow Example
class APIIntegratedWorkflow:
    """Example workflow that uses multiple API integrations."""
    
    def __init__(self):
        self.api_manager = APIIntegrationManager()
        self.weather = WeatherAPIIntegration(self.api_manager)
        self.news = NewsAPIIntegration(self.api_manager)
        self.slack = SlackIntegration(self.api_manager)
    
    def create_daily_briefing(self, city: str = "New York", topics: List[str] = None):
        """Create a daily briefing with weather and news."""
        print("📰 Creating Daily Briefing")
        print("=" * 30)
        
        briefing = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'city': city,
            'weather': None,
            'news': [],
            'summary': ""
        }
        
        # Get weather
        print("🌤️ Fetching weather...")
        weather = self.weather.get_current_weather(city)
        if weather:
            briefing['weather'] = weather
            print(f"   {weather['city']}: {weather['temperature']}°C, {weather['description']}")
        
        # Get news
        topics = topics or ['technology', 'business', 'science']
        print(f"📰 Fetching news for topics: {', '.join(topics)}")
        
        for topic in topics:
            if topic in ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']:
                # Use category for top headlines
                articles = self.news.get_top_headlines(category=topic)
            else:
                # Use search for custom topics
                articles = self.news.search_news(topic)
            
            if articles:
                briefing['news'].extend(articles[:3])  # Top 3 articles per topic
                print(f"   Found {len(articles)} articles for {topic}")
        
        # Create summary
        weather_summary = ""
        if briefing['weather']:
            w = briefing['weather']
            weather_summary = f"Weather in {w['city']}: {w['temperature']}°C, {w['description']}"
        
        news_summary = f"Found {len(briefing['news'])} relevant news articles"
        
        briefing['summary'] = f"{weather_summary}. {news_summary}."
        
        # Send to Slack (optional)
        if os.getenv('SLACK_BOT_TOKEN'):
            self.slack.create_workflow_notification(
                "Daily Briefing", 
                "success", 
                briefing['summary']
            )
        
        return briefing
    
    def monitor_keyword_mentions(self, keywords: List[str], notification_channel: str = None):
        """Monitor news for specific keyword mentions."""
        print(f"🔍 Monitoring keywords: {', '.join(keywords)}")
        
        results = {}
        for keyword in keywords:
            articles = self.news.search_news(keyword)
            results[keyword] = {
                'count': len(articles),
                'articles': articles[:5]  # Top 5
            }
            
            print(f"   {keyword}: {len(articles)} mentions")
            
            # Send alert if many mentions
            if len(articles) > 10 and notification_channel:
                self.slack.send_message(
                    notification_channel,
                    f"🚨 High activity for '{keyword}': {len(articles)} new articles"
                )
        
        return results

def demo_api_integrations():
    """Demonstrate API integrations."""
    print("🔌 API Integration Demo")
    print("=" * 30)
    
    # Note about API keys
    print("💡 Note: This demo uses placeholder API keys.")
    print("   Set environment variables for real APIs:")
    print("   - OPENWEATHER_API_KEY")
    print("   - NEWS_API_KEY") 
    print("   - SLACK_BOT_TOKEN")
    print()
    
    # Create workflow
    workflow = APIIntegratedWorkflow()
    
    # Demo 1: Daily briefing
    print("📰 Demo 1: Daily Briefing")
    try:
        briefing = workflow.create_daily_briefing("London", ["technology", "ai"])
        print(f"   Summary: {briefing['summary']}")
    except Exception as e:
        print(f"   Demo failed (expected with demo keys): {e}")
    
    print("\n" + "-" * 30)
    
    # Demo 2: Keyword monitoring
    print("🔍 Demo 2: Keyword Monitoring")
    try:
        results = workflow.monitor_keyword_mentions(["artificial intelligence", "machine learning"])
        for keyword, data in results.items():
            print(f"   {keyword}: {data['count']} articles")
    except Exception as e:
        print(f"   Demo failed (expected with demo keys): {e}")

if __name__ == "__main__":
    demo_api_integrations()
