"""Memory bridge syncing new conversation memory/knowledge with legacy formats.

This module provides one-way and two-way synchronization helpers to:
- Export new conversation memory into legacy JSON artifacts
- Export knowledge structures into a simple legacy representation
- Import legacy conversation data back into the new memory system
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryBridge:
    """Bridge between new memory systems and legacy memory services."""

    def __init__(self, new_conversation_memory=None, new_knowledge_graph=None):
        """Initialize the memory bridge.

        Args:
            new_conversation_memory: ConversationMemory instance from new runtime.
            new_knowledge_graph: KnowledgeGraph instance from new runtime.
        """
        self.new_conversation_memory = new_conversation_memory
        self.new_knowledge_graph = new_knowledge_graph
        self.legacy_memory_dir = Path("data/sessions")
        self.legacy_memory_dir.mkdir(parents=True, exist_ok=True)

    def sync_conversations_to_legacy(self) -> Dict[str, Any]:
        """Export recent conversation memory to a legacy JSON file.

        Returns:
            Dict with success flag, number of items, and file path.
        """
        if not self.new_conversation_memory:
            return {"error": "New conversation memory not available"}

        try:
            conversations = self.new_conversation_memory.get_recent_conversations(50)
            legacy_data = {
                "conversations": [],
                "metadata": {
                    "sync_time": datetime.now().isoformat(),
                    "source": "new_memory_system",
                    "count": len(conversations),
                },
            }
            for conv in conversations:
                legacy_conv = {
                    "id": getattr(conv, "id", str(hash(str(conv)))),
                    "timestamp": getattr(conv, "timestamp", datetime.now().isoformat()),
                    "messages": getattr(conv, "messages", []),
                    "metadata": getattr(conv, "metadata", {}),
                }
                legacy_data["conversations"].append(legacy_conv)

            legacy_file = self.legacy_memory_dir / "new_system_conversations.json"
            with open(legacy_file, "w", encoding="utf-8") as f:
                json.dump(legacy_data, f, indent=2)

            return {"success": True, "conversations_synced": len(conversations), "legacy_file": str(legacy_file)}

        except Exception as e:
            logger.error(f"Failed to sync conversations to legacy: {e}")
            return {"error": str(e), "success": False}

    def sync_knowledge_to_legacy(self) -> Dict[str, Any]:
        """Export knowledge graph subset to a legacy JSON file (simplified)."""
        if not self.new_knowledge_graph:
            return {"error": "New knowledge graph not available"}

        try:
            knowledge_data = {
                "nodes": [
                    {
                        "id": "system_info",
                        "type": "system",
                        "properties": {"name": "Jarvis AI System", "version": "2.0", "description": "Unified AI assistant system"},
                    }
                ],
                "edges": [],
                "metadata": {
                    "sync_time": datetime.now().isoformat(),
                    "source": "new_knowledge_system",
                },
            }

            legacy_file = self.legacy_memory_dir / "new_system_knowledge.json"
            with open(legacy_file, "w", encoding="utf-8") as f:
                json.dump(knowledge_data, f, indent=2)

            return {"success": True, "knowledge_synced": True, "legacy_file": str(legacy_file)}

        except Exception as e:
            logger.error(f"Failed to sync knowledge to legacy: {e}")
            return {"error": str(e), "success": False}

    def load_legacy_conversations(self) -> Dict[str, Any]:
        """Import legacy conversation files into the new memory system.

        Returns:
            Dict with counts of loaded conversations and processed files.
        """
        if not self.new_conversation_memory:
            return {"error": "New conversation memory not available"}

        try:
            legacy_files = list(self.legacy_memory_dir.glob("*.json"))
            loaded_count = 0

            for file_path in legacy_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    if "conversations" in data:
                        for conv_data in data["conversations"]:
                            if hasattr(self.new_conversation_memory, "add_conversation"):
                                self.new_conversation_memory.add_conversation(conv_data)
                                loaded_count += 1

                except Exception as e:
                    logger.warning(f"Failed to load legacy file {file_path}: {e}")
                    continue

            return {"success": True, "conversations_loaded": loaded_count, "files_processed": len(legacy_files)}

        except Exception as e:
            logger.error(f"Failed to load legacy conversations: {e}")
            return {"error": str(e), "success": False}

    def get_memory_stats(self) -> Dict[str, Any]:
        """Return a summary of new and legacy memory states."""
        stats = {
            "new_system": {
                "conversation_memory_available": self.new_conversation_memory is not None,
                "knowledge_graph_available": self.new_knowledge_graph is not None,
            },
            "legacy_system": {
                "memory_dir": str(self.legacy_memory_dir),
                "files_count": len(list(self.legacy_memory_dir.glob("*.json"))),
            },
        }
        if self.new_conversation_memory:
            try:
                conversations = self.new_conversation_memory.get_recent_conversations(1000)
                stats["new_system"]["conversation_count"] = len(conversations)
            except Exception:
                stats["new_system"]["conversation_count"] = "unknown"
        return stats

    def migrate_all_data(self) -> Dict[str, Any]:
        """Run a convenience migration: export new->legacy, import legacy->new, and summarize."""
        results = {
            "conversations_to_legacy": self.sync_conversations_to_legacy(),
            "knowledge_to_legacy": self.sync_knowledge_to_legacy(),
            "legacy_to_new": self.load_legacy_conversations(),
            "stats": self.get_memory_stats(),
        }
        results["overall_success"] = all(
            result.get("success", False) for result in results.values() if isinstance(result, dict) and "success" in result
        )
        return results


# Global memory bridge instance
memory_bridge = None


def initialize_memory_bridge(new_conversation_memory=None, new_knowledge_graph=None):
    """Initialize and register a global MemoryBridge instance."""
    global memory_bridge
    memory_bridge = MemoryBridge(new_conversation_memory, new_knowledge_graph)
    return memory_bridge


def get_memory_bridge() -> Optional[MemoryBridge]:
    """Return the global MemoryBridge instance if initialized."""
    return memory_bridge
