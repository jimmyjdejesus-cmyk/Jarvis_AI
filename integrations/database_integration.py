#!/usr/bin/env python3
"""
Database Integration Examples
Connect your workflows to various databases for persistent data.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class DatabaseIntegration:
    """Handle database operations for workflows."""
    
    def __init__(self, db_path="jarvis_data.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Workflows table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_name TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                execution_time REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Custom data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_type TEXT NOT NULL,
                data_key TEXT NOT NULL,
                data_value TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                metric_unit TEXT,
                tags TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def save_workflow_result(self, workflow_name, input_data, output_data, execution_time, status="success"):
        """Save workflow execution results."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workflows (workflow_name, input_data, output_data, execution_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            workflow_name,
            json.dumps(input_data) if isinstance(input_data, dict) else str(input_data),
            json.dumps(output_data) if isinstance(output_data, dict) else str(output_data),
            execution_time,
            status
        ))
        
        workflow_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"📊 Workflow saved: ID {workflow_id}")
        return workflow_id
    
    def get_workflow_history(self, workflow_name=None, limit=10):
        """Get workflow execution history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if workflow_name:
            cursor.execute('''
                SELECT * FROM workflows 
                WHERE workflow_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (workflow_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM workflows 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def store_custom_data(self, data_type, data_key, data_value, metadata=None):
        """Store custom data for workflows."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute('''
            SELECT id FROM custom_data 
            WHERE data_type = ? AND data_key = ?
        ''', (data_type, data_key))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing data
            cursor.execute('''
                UPDATE custom_data 
                SET data_value = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE data_type = ? AND data_key = ?
            ''', (
                json.dumps(data_value) if isinstance(data_value, (dict, list)) else str(data_value),
                json.dumps(metadata) if metadata else None,
                data_type,
                data_key
            ))
            print(f"📝 Updated data: {data_type}.{data_key}")
        else:
            # Insert new data
            cursor.execute('''
                INSERT INTO custom_data (data_type, data_key, data_value, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                data_type,
                data_key,
                json.dumps(data_value) if isinstance(data_value, (dict, list)) else str(data_value),
                json.dumps(metadata) if metadata else None
            ))
            print(f"💾 Stored data: {data_type}.{data_key}")
        
        conn.commit()
        conn.close()
    
    def get_custom_data(self, data_type, data_key=None):
        """Retrieve custom data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if data_key:
            cursor.execute('''
                SELECT data_value, metadata FROM custom_data 
                WHERE data_type = ? AND data_key = ?
            ''', (data_type, data_key))
            result = cursor.fetchone()
            
            if result:
                try:
                    value = json.loads(result[0])
                except:
                    value = result[0]
                
                try:
                    metadata = json.loads(result[1]) if result[1] else None
                except:
                    metadata = result[1]
                
                conn.close()
                return {'value': value, 'metadata': metadata}
        else:
            cursor.execute('''
                SELECT data_key, data_value FROM custom_data 
                WHERE data_type = ?
            ''', (data_type,))
            results = cursor.fetchall()
            
            data = {}
            for key, value in results:
                try:
                    data[key] = json.loads(value)
                except:
                    data[key] = value
            
            conn.close()
            return data
        
        conn.close()
        return None
    
    def log_analytics(self, metric_name, metric_value, metric_unit="", tags=None):
        """Log analytics metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analytics (metric_name, metric_value, metric_unit, tags)
            VALUES (?, ?, ?, ?)
        ''', (
            metric_name,
            metric_value,
            metric_unit,
            json.dumps(tags) if tags else None
        ))
        
        conn.commit()
        conn.close()
        print(f"📈 Logged metric: {metric_name} = {metric_value} {metric_unit}")
    
    def get_analytics_summary(self, metric_name=None, hours=24):
        """Get analytics summary."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if metric_name:
            cursor.execute('''
                SELECT AVG(metric_value), MIN(metric_value), MAX(metric_value), COUNT(*)
                FROM analytics 
                WHERE metric_name = ? 
                AND timestamp > datetime('now', '-{} hours')
            '''.format(hours), (metric_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] is not None:
                return {
                    'metric': metric_name,
                    'average': result[0],
                    'minimum': result[1],
                    'maximum': result[2],
                    'count': result[3]
                }
        else:
            cursor.execute('''
                SELECT metric_name, AVG(metric_value), COUNT(*)
                FROM analytics 
                WHERE timestamp > datetime('now', '-{} hours')
                GROUP BY metric_name
            '''.format(hours))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {'metric': row[0], 'average': row[1], 'count': row[2]}
                for row in results
            ]
        
        return None

# Example: Database-integrated workflow
class DatabaseWorkflow:
    """Example workflow that uses database integration."""
    
    def __init__(self):
        self.db = DatabaseIntegration()
    
    def process_user_query(self, query, user_id="anonymous"):
        """Process a user query with database tracking."""
        import time
        
        start_time = time.time()
        
        try:
            # Log the query
            self.db.store_custom_data("user_queries", f"{user_id}_{int(time.time())}", {
                "query": query,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
            
            # Process the query (simulate processing)
            result = f"Processed query: {query}"
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Save workflow result
            workflow_id = self.db.save_workflow_result(
                workflow_name="user_query_processing",
                input_data={"query": query, "user_id": user_id},
                output_data={"result": result},
                execution_time=execution_time,
                status="success"
            )
            
            # Log analytics
            self.db.log_analytics("query_processing_time", execution_time, "seconds", 
                                {"user_id": user_id, "workflow_id": workflow_id})
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Save failed workflow
            self.db.save_workflow_result(
                workflow_name="user_query_processing",
                input_data={"query": query, "user_id": user_id},
                output_data={"error": str(e)},
                execution_time=execution_time,
                status="error"
            )
            
            raise e
    
    def get_user_query_history(self, user_id):
        """Get query history for a user."""
        all_queries = self.db.get_custom_data("user_queries")
        user_queries = []
        
        for key, value in all_queries.items():
            if value.get("user_id") == user_id:
                user_queries.append(value)
        
        return sorted(user_queries, key=lambda x: x["timestamp"], reverse=True)
    
    def get_performance_stats(self):
        """Get performance statistics."""
        return self.db.get_analytics_summary("query_processing_time")

def demo_database_integration():
    """Demonstrate database integration."""
    print("🗄️ Database Integration Demo")
    print("=" * 40)
    
    # Create workflow instance
    workflow = DatabaseWorkflow()
    
    # Process some queries
    queries = [
        "What is machine learning?",
        "How to deploy AI models?",
        "Best practices for LLM applications?"
    ]
    
    print("\n📝 Processing queries...")
    for i, query in enumerate(queries):
        result = workflow.process_user_query(query, f"user_{i+1}")
        print(f"   Query {i+1}: Processed successfully")
    
    # Show workflow history
    print("\n📊 Workflow History:")
    history = workflow.db.get_workflow_history(limit=5)
    for record in history:
        print(f"   ID: {record[0]}, Name: {record[1]}, Status: {record[5]}")
    
    # Show performance stats
    print("\n📈 Performance Statistics:")
    stats = workflow.get_performance_stats()
    if stats:
        print(f"   Average processing time: {stats['average']:.3f} seconds")
        print(f"   Total queries processed: {stats['count']}")
    
    # Show user query history
    print("\n👤 User Query History (user_1):")
    user_history = workflow.get_user_query_history("user_1")
    for query in user_history:
        print(f"   {query['timestamp']}: {query['query']}")

if __name__ == "__main__":
    demo_database_integration()
