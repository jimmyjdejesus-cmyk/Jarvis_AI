"""
🧠 PHASE 5: KNOWLEDGE ENGINE

Continuous learning with knowledge graphs, cross-domain reasoning,
and intelligent knowledge synthesis.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import numpy as np
from collections import defaultdict, deque
import uuid
import re

logger = logging.getLogger(__name__)

class KnowledgeType(Enum):
    """Types of knowledge in the system"""
    FACTUAL = "factual"
    PROCEDURAL = "procedural"
    CONTEXTUAL = "contextual"
    EXPERIENTIAL = "experiential"
    RELATIONAL = "relational"
    TEMPORAL = "temporal"

class ConceptType(Enum):
    """Types of concepts in knowledge graph"""
    ENTITY = "entity"
    PROCESS = "process"
    PROPERTY = "property"
    RELATIONSHIP = "relationship"
    PATTERN = "pattern"
    RULE = "rule"

class ConfidenceLevel(Enum):
    """Confidence levels for knowledge"""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9
    CERTAIN = 1.0

@dataclass
class KnowledgeNode:
    """A node in the knowledge graph"""
    node_id: str
    concept_type: ConceptType
    name: str
    description: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    source: str = "unknown"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    relevance_score: float = 0.0
    
    def update_relevance(self, new_access: bool = True):
        """Update relevance score based on usage"""
        if new_access:
            self.access_count += 1
            self.updated_at = datetime.now()
        
        # Calculate relevance based on recency and frequency
        age_days = (datetime.now() - self.updated_at).days
        recency_factor = max(0.1, 1.0 - (age_days / 365))  # Decay over a year
        frequency_factor = min(1.0, self.access_count / 100)  # Cap at 100 accesses
        
        self.relevance_score = (recency_factor * 0.6) + (frequency_factor * 0.4)

@dataclass
class KnowledgeRelationship:
    """A relationship between knowledge nodes"""
    relationship_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    strength: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)
    bidirectional: bool = False
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_reverse_type(self) -> str:
        """Get reverse relationship type for bidirectional relationships"""
        reverse_mappings = {
            "is_part_of": "contains",
            "contains": "is_part_of",
            "causes": "is_caused_by",
            "is_caused_by": "causes",
            "similar_to": "similar_to",
            "related_to": "related_to",
            "depends_on": "is_dependency_of",
            "is_dependency_of": "depends_on"
        }
        
        return reverse_mappings.get(self.relationship_type, f"reverse_{self.relationship_type}")

@dataclass
class KnowledgeQuery:
    """A query for knowledge retrieval"""
    query_id: str
    query_text: str
    query_type: str  # "semantic", "structural", "temporal", "causal"
    context: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    max_results: int = 10
    min_confidence: float = 0.3
    include_related: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class KnowledgeInsight:
    """An insight generated from knowledge analysis"""
    insight_id: str
    insight_type: str  # "pattern", "correlation", "prediction", "anomaly"
    title: str
    description: str
    evidence: List[str]
    confidence: float
    related_nodes: List[str]
    actionable: bool = False
    created_at: datetime = field(default_factory=datetime.now)

class SemanticProcessor:
    """Processes semantic meaning from text and data"""
    
    def __init__(self):
        self.concept_patterns = {
            "entity": r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            "process": r'\b\w+ing\b|\b\w+tion\b|\b\w+ment\b',
            "property": r'\bis\s+\w+\b|\bhas\s+\w+\b|\b\w+\s+is\b',
            "temporal": r'\b(?:before|after|during|when|while|until)\b',
            "causal": r'\b(?:because|causes?|results?\s+in|leads?\s+to|due\s+to)\b'
        }
        
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'must', 'shall'
        }
    
    async def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract concepts from text"""
        concepts = []
        
        # Extract entities (proper nouns, technical terms)
        entity_matches = re.findall(self.concept_patterns["entity"], text)
        for entity in entity_matches:
            if entity.lower() not in self.stop_words:
                concepts.append({
                    "text": entity,
                    "type": ConceptType.ENTITY.value,
                    "confidence": 0.7,
                    "position": text.find(entity)
                })
        
        # Extract processes (actions, procedures)
        process_matches = re.findall(self.concept_patterns["process"], text, re.IGNORECASE)
        for process in process_matches:
            if process.lower() not in self.stop_words:
                concepts.append({
                    "text": process,
                    "type": ConceptType.PROCESS.value,
                    "confidence": 0.6,
                    "position": text.lower().find(process.lower())
                })
        
        # Extract properties
        property_matches = re.findall(self.concept_patterns["property"], text, re.IGNORECASE)
        for prop in property_matches:
            concepts.append({
                "text": prop,
                "type": ConceptType.PROPERTY.value,
                "confidence": 0.5,
                "position": text.lower().find(prop.lower())
            })
        
        return sorted(concepts, key=lambda x: x["position"])
    
    async def extract_relationships(self, text: str, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between concepts"""
        relationships = []
        
        # Simple pattern-based relationship extraction
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts[i+1:], i+1):
                # Check distance between concepts
                distance = abs(concept2["position"] - concept1["position"])
                
                if distance < 100:  # Within 100 characters
                    # Determine relationship type based on patterns
                    text_between = text[concept1["position"]:concept2["position"]]
                    
                    rel_type = "related_to"  # Default
                    strength = 0.3
                    
                    if re.search(self.concept_patterns["causal"], text_between, re.IGNORECASE):
                        rel_type = "causes"
                        strength = 0.7
                    elif re.search(self.concept_patterns["temporal"], text_between, re.IGNORECASE):
                        rel_type = "temporal_relation"
                        strength = 0.6
                    elif "is" in text_between.lower() or "are" in text_between.lower():
                        rel_type = "is_a"
                        strength = 0.8
                    elif "has" in text_between.lower() or "contains" in text_between.lower():
                        rel_type = "contains"
                        strength = 0.7
                    
                    relationships.append({
                        "source": concept1["text"],
                        "target": concept2["text"],
                        "type": rel_type,
                        "strength": strength,
                        "distance": distance
                    })
        
        return relationships
    
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between texts"""
        # Simple word overlap similarity (can be enhanced with embeddings)
        words1 = set(text1.lower().split()) - self.stop_words
        words2 = set(text2.lower().split()) - self.stop_words
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

class KnowledgeGraph:
    """Graph-based knowledge representation"""
    
    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relationships: Dict[str, KnowledgeRelationship] = {}
        self.node_index: Dict[str, Set[str]] = defaultdict(set)  # For fast lookup
        self.semantic_processor = SemanticProcessor()
        
        # Graph statistics
        self.node_count_by_type = defaultdict(int)
        self.relationship_count_by_type = defaultdict(int)
    
    async def add_node(self, 
                      name: str,
                      concept_type: ConceptType,
                      description: str = "",
                      properties: Dict[str, Any] = None,
                      confidence: float = 0.5,
                      source: str = "user") -> str:
        """Add a node to the knowledge graph"""
        
        node_id = f"{concept_type.value}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        # Check if node already exists
        if node_id in self.nodes:
            # Update existing node
            existing_node = self.nodes[node_id]
            existing_node.description = description or existing_node.description
            existing_node.properties.update(properties or {})
            existing_node.confidence = max(existing_node.confidence, confidence)
            existing_node.update_relevance(True)
            return node_id
        
        # Create new node
        node = KnowledgeNode(
            node_id=node_id,
            concept_type=concept_type,
            name=name,
            description=description,
            properties=properties or {},
            confidence=confidence,
            source=source
        )
        
        self.nodes[node_id] = node
        self.node_count_by_type[concept_type.value] += 1
        
        # Index for search
        words = name.lower().split()
        for word in words:
            self.node_index[word].add(node_id)
        
        logger.info(f"Added knowledge node: {name} ({concept_type.value})")
        return node_id
    
    async def add_relationship(self,
                             source_node_id: str,
                             target_node_id: str,
                             relationship_type: str,
                             strength: float = 0.5,
                             properties: Dict[str, Any] = None,
                             bidirectional: bool = False,
                             confidence: float = 0.5) -> str:
        """Add a relationship between nodes"""
        
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
        
        relationship_id = f"rel_{hashlib.md5(f'{source_node_id}_{target_node_id}_{relationship_type}'.encode()).hexdigest()[:8]}"
        
        relationship = KnowledgeRelationship(
            relationship_id=relationship_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            strength=strength,
            properties=properties or {},
            bidirectional=bidirectional,
            confidence=confidence
        )
        
        self.relationships[relationship_id] = relationship
        self.relationship_count_by_type[relationship_type] += 1
        
        # Add reverse relationship if bidirectional
        if bidirectional:
            reverse_id = f"rel_{hashlib.md5(f'{target_node_id}_{source_node_id}_{relationship.get_reverse_type()}'.encode()).hexdigest()[:8]}"
            reverse_relationship = KnowledgeRelationship(
                relationship_id=reverse_id,
                source_node_id=target_node_id,
                target_node_id=source_node_id,
                relationship_type=relationship.get_reverse_type(),
                strength=strength,
                properties=properties or {},
                bidirectional=False,  # Prevent infinite recursion
                confidence=confidence
            )
            self.relationships[reverse_id] = reverse_relationship
        
        logger.info(f"Added relationship: {relationship_type} between {source_node_id} and {target_node_id}")
        return relationship_id
    
    async def process_text_knowledge(self, text: str, source: str = "text_processing") -> Dict[str, Any]:
        """Process text to extract and add knowledge"""
        
        # Extract concepts
        concepts = await self.semantic_processor.extract_concepts(text)
        
        # Add concepts as nodes
        added_nodes = []
        for concept in concepts:
            node_id = await self.add_node(
                name=concept["text"],
                concept_type=ConceptType(concept["type"]),
                description=f"Extracted from: {text[:100]}...",
                confidence=concept["confidence"],
                source=source
            )
            added_nodes.append(node_id)
        
        # Extract and add relationships
        relationships = await self.semantic_processor.extract_relationships(text, concepts)
        added_relationships = []
        
        for rel in relationships:
            # Find node IDs for source and target
            source_node_id = None
            target_node_id = None
            
            for node_id, node in self.nodes.items():
                if node.name == rel["source"]:
                    source_node_id = node_id
                if node.name == rel["target"]:
                    target_node_id = node_id
            
            if source_node_id and target_node_id:
                rel_id = await self.add_relationship(
                    source_node_id=source_node_id,
                    target_node_id=target_node_id,
                    relationship_type=rel["type"],
                    strength=rel["strength"],
                    confidence=rel["strength"]
                )
                if rel_id:
                    added_relationships.append(rel_id)
        
        return {
            "processed_text": text,
            "concepts_extracted": len(concepts),
            "nodes_added": len(added_nodes),
            "relationships_added": len(added_relationships),
            "node_ids": added_nodes,
            "relationship_ids": added_relationships
        }
    
    async def find_nodes(self, 
                        query: str,
                        concept_type: Optional[ConceptType] = None,
                        min_confidence: float = 0.0,
                        max_results: int = 10) -> List[KnowledgeNode]:
        """Find nodes matching query"""
        
        # Simple search by name and description
        query_words = set(query.lower().split())
        
        # Find nodes by indexed words
        candidate_node_ids = set()
        for word in query_words:
            candidate_node_ids.update(self.node_index.get(word, set()))
        
        # Score and filter candidates
        scored_nodes = []
        for node_id in candidate_node_ids:
            node = self.nodes[node_id]
            
            # Filter by type and confidence
            if concept_type and node.concept_type != concept_type:
                continue
            if node.confidence < min_confidence:
                continue
            
            # Calculate relevance score
            name_similarity = await self.semantic_processor.calculate_semantic_similarity(
                query, node.name
            )
            desc_similarity = await self.semantic_processor.calculate_semantic_similarity(
                query, node.description
            )
            
            total_score = (
                name_similarity * 0.7 +
                desc_similarity * 0.2 +
                node.relevance_score * 0.1
            )
            
            scored_nodes.append((total_score, node))
        
        # Sort by score and return top results
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in scored_nodes[:max_results]]
    
    async def get_related_nodes(self, 
                              node_id: str,
                              relationship_types: Optional[List[str]] = None,
                              max_depth: int = 2,
                              max_results: int = 20) -> List[Tuple[KnowledgeNode, float, int]]:
        """Get nodes related to a given node"""
        
        if node_id not in self.nodes:
            return []
        
        visited = set()
        results = []
        queue = deque([(node_id, 1.0, 0)])  # (node_id, accumulated_strength, depth)
        
        while queue and len(results) < max_results:
            current_node_id, strength, depth = queue.popleft()
            
            if current_node_id in visited or depth > max_depth:
                continue
            
            visited.add(current_node_id)
            
            if current_node_id != node_id:  # Don't include the original node
                node = self.nodes[current_node_id]
                results.append((node, strength, depth))
            
            # Find connected nodes
            if depth < max_depth:
                for rel in self.relationships.values():
                    target_id = None
                    rel_strength = rel.strength
                    
                    if rel.source_node_id == current_node_id:
                        target_id = rel.target_node_id
                    elif rel.bidirectional and rel.target_node_id == current_node_id:
                        target_id = rel.source_node_id
                    
                    if target_id and target_id not in visited:
                        # Filter by relationship type if specified
                        if relationship_types and rel.relationship_type not in relationship_types:
                            continue
                        
                        new_strength = strength * rel_strength
                        queue.append((target_id, new_strength, depth + 1))
        
        # Sort by strength (relevance)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        
        # Calculate average confidence
        avg_confidence = sum(node.confidence for node in self.nodes.values()) / len(self.nodes) if self.nodes else 0
        
        # Find most connected nodes
        node_connections = defaultdict(int)
        for rel in self.relationships.values():
            node_connections[rel.source_node_id] += 1
            node_connections[rel.target_node_id] += 1
        
        most_connected = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "nodes_by_type": dict(self.node_count_by_type),
            "relationships_by_type": dict(self.relationship_count_by_type),
            "average_confidence": avg_confidence,
            "most_connected_nodes": [
                {
                    "node_id": node_id,
                    "name": self.nodes[node_id].name if node_id in self.nodes else "Unknown",
                    "connections": count
                }
                for node_id, count in most_connected
            ]
        }

class ReasoningEngine:
    """Advanced reasoning capabilities"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.knowledge_graph = knowledge_graph
        self.reasoning_rules = []
        self._initialize_reasoning_rules()
    
    def _initialize_reasoning_rules(self):
        """Initialize basic reasoning rules"""
        self.reasoning_rules = [
            {
                "name": "transitivity",
                "pattern": ["A", "is_a", "B", "is_a", "C"],
                "conclusion": ["A", "is_a", "C"],
                "confidence_factor": 0.8
            },
            {
                "name": "causality_chain",
                "pattern": ["A", "causes", "B", "causes", "C"],
                "conclusion": ["A", "indirectly_causes", "C"],
                "confidence_factor": 0.6
            },
            {
                "name": "part_whole",
                "pattern": ["A", "is_part_of", "B", "is_part_of", "C"],
                "conclusion": ["A", "is_part_of", "C"],
                "confidence_factor": 0.9
            }
        ]
    
    async def infer_new_relationships(self) -> List[Dict[str, Any]]:
        """Infer new relationships using reasoning rules"""
        
        inferred_relationships = []
        
        for rule in self.reasoning_rules:
            # Apply each rule to find new relationships
            new_rels = await self._apply_reasoning_rule(rule)
            inferred_relationships.extend(new_rels)
        
        return inferred_relationships
    
    async def _apply_reasoning_rule(self, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply a specific reasoning rule"""
        
        pattern = rule["pattern"]
        conclusion = rule["conclusion"]
        confidence_factor = rule["confidence_factor"]
        
        inferences = []
        
        # Find relationship chains matching the pattern
        if len(pattern) == 5:  # A-rel1-B-rel2-C pattern
            rel1_type = pattern[1]
            rel2_type = pattern[3]
            conclusion_type = conclusion[1]
            
            # Find chains of relationships
            for rel1 in self.knowledge_graph.relationships.values():
                if rel1.relationship_type == rel1_type:
                    # Find second relationship starting from rel1's target
                    for rel2 in self.knowledge_graph.relationships.values():
                        if (rel2.relationship_type == rel2_type and 
                            rel2.source_node_id == rel1.target_node_id):
                            
                            # Check if conclusion already exists
                            conclusion_exists = False
                            for existing_rel in self.knowledge_graph.relationships.values():
                                if (existing_rel.source_node_id == rel1.source_node_id and
                                    existing_rel.target_node_id == rel2.target_node_id and
                                    existing_rel.relationship_type == conclusion_type):
                                    conclusion_exists = True
                                    break
                            
                            if not conclusion_exists:
                                # Calculate confidence
                                inference_confidence = min(
                                    rel1.confidence,
                                    rel2.confidence
                                ) * confidence_factor
                                
                                inferences.append({
                                    "rule": rule["name"],
                                    "source_node_id": rel1.source_node_id,
                                    "target_node_id": rel2.target_node_id,
                                    "relationship_type": conclusion_type,
                                    "confidence": inference_confidence,
                                    "evidence": [rel1.relationship_id, rel2.relationship_id]
                                })
        
        return inferences
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer questions using knowledge reasoning"""
        
        # Simple question processing
        question_lower = question.lower()
        
        # Extract question type and entities
        question_patterns = {
            "what_is": r"what is (\w+(?:\s+\w+)*)",
            "how_does": r"how does (\w+(?:\s+\w+)*) (\w+)",
            "why_does": r"why does (\w+(?:\s+\w+)*) (\w+)",
            "when_does": r"when does (\w+(?:\s+\w+)*) (\w+)",
            "where_is": r"where is (\w+(?:\s+\w+)*)",
            "who_is": r"who is (\w+(?:\s+\w+)*)"
        }
        
        question_type = "general"
        entities = []
        
        for q_type, pattern in question_patterns.items():
            match = re.search(pattern, question_lower)
            if match:
                question_type = q_type
                entities = [match.group(1)]
                if match.lastindex > 1:
                    entities.append(match.group(2))
                break
        
        # Find relevant nodes
        relevant_nodes = []
        for entity in entities:
            nodes = await self.knowledge_graph.find_nodes(entity, max_results=5)
            relevant_nodes.extend(nodes)
        
        if not relevant_nodes:
            return {
                "question": question,
                "answer": "I don't have enough knowledge to answer this question.",
                "confidence": 0.0,
                "entities_found": [],
                "reasoning_path": []
            }
        
        # Generate answer based on question type and found nodes
        answer = await self._generate_answer(question_type, entities, relevant_nodes)
        
        return answer
    
    async def _generate_answer(self, 
                             question_type: str,
                             entities: List[str],
                             nodes: List[KnowledgeNode]) -> Dict[str, Any]:
        """Generate answer from knowledge nodes"""
        
        if question_type == "what_is":
            # Find definition or description
            primary_node = nodes[0] if nodes else None
            if primary_node:
                answer_text = primary_node.description or f"{primary_node.name} is a {primary_node.concept_type.value}."
                
                # Get related information
                related = await self.knowledge_graph.get_related_nodes(
                    primary_node.node_id, max_depth=1, max_results=3
                )
                
                if related:
                    additional_info = []
                    for related_node, strength, depth in related:
                        additional_info.append(f"It is related to {related_node.name}")
                    
                    if additional_info:
                        answer_text += " " + ". ".join(additional_info[:2]) + "."
                
                return {
                    "question": f"What is {entities[0]}?",
                    "answer": answer_text,
                    "confidence": primary_node.confidence,
                    "entities_found": [primary_node.name],
                    "reasoning_path": [f"Found definition for {primary_node.name}"]
                }
        
        elif question_type == "how_does":
            # Find procedural knowledge or causal relationships
            if len(entities) >= 2:
                entity1, entity2 = entities[0], entities[1]
                
                # Look for causal or procedural relationships
                relevant_rels = []
                for rel in self.knowledge_graph.relationships.values():
                    source_node = self.knowledge_graph.nodes.get(rel.source_node_id)
                    target_node = self.knowledge_graph.nodes.get(rel.target_node_id)
                    
                    if (source_node and target_node and
                        entity1 in source_node.name.lower() and
                        entity2 in target_node.name.lower() and
                        rel.relationship_type in ["causes", "enables", "leads_to"]):
                        relevant_rels.append(rel)
                
                if relevant_rels:
                    rel = relevant_rels[0]
                    source_node = self.knowledge_graph.nodes[rel.source_node_id]
                    target_node = self.knowledge_graph.nodes[rel.target_node_id]
                    
                    return {
                        "question": f"How does {entity1} {entity2}?",
                        "answer": f"{source_node.name} {rel.relationship_type} {target_node.name}.",
                        "confidence": rel.confidence,
                        "entities_found": [source_node.name, target_node.name],
                        "reasoning_path": [f"Found {rel.relationship_type} relationship"]
                    }
        
        # Default response
        primary_node = nodes[0] if nodes else None
        return {
            "question": " ".join(entities) if entities else "Unknown question",
            "answer": f"I found information about {primary_node.name}: {primary_node.description}" if primary_node else "No relevant information found.",
            "confidence": primary_node.confidence if primary_node else 0.0,
            "entities_found": [node.name for node in nodes[:3]],
            "reasoning_path": ["Simple knowledge lookup"]
        }

class KnowledgeEngine:
    """Main knowledge engine orchestrator"""
    
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.reasoning_engine = ReasoningEngine(self.knowledge_graph)
        self.learning_history: List[Dict[str, Any]] = []
        self.insights: List[KnowledgeInsight] = []
        
        # Initialize with basic knowledge
        # asyncio.create_task(self._initialize_base_knowledge())
    
    async def _initialize_base_knowledge(self):
        """Initialize the engine with basic knowledge"""
        
        # Add fundamental concepts
        basic_concepts = [
            ("System", ConceptType.ENTITY, "A collection of interacting components"),
            ("Process", ConceptType.PROCESS, "A series of actions or steps"),
            ("Data", ConceptType.ENTITY, "Information stored and processed"),
            ("Algorithm", ConceptType.PROCESS, "A step-by-step procedure for solving problems"),
            ("Intelligence", ConceptType.PROPERTY, "The ability to learn and understand"),
            ("Learning", ConceptType.PROCESS, "The acquisition of knowledge or skills"),
            ("Pattern", ConceptType.PATTERN, "A repeated or regular form or sequence"),
            ("Optimization", ConceptType.PROCESS, "The process of making something as effective as possible")
        ]
        
        for name, concept_type, description in basic_concepts:
            await self.knowledge_graph.add_node(
                name=name,
                concept_type=concept_type,
                description=description,
                confidence=0.9,
                source="base_knowledge"
            )
        
        # Add basic relationships
        basic_relationships = [
            ("Algorithm", "Process", "is_a", 0.9),
            ("Learning", "Process", "is_a", 0.9),
            ("Intelligence", "Learning", "enables", 0.8),
            ("Data", "Algorithm", "input_to", 0.7),
            ("Pattern", "Learning", "enables", 0.7),
            ("Optimization", "Algorithm", "improves", 0.8)
        ]
        
        # Find node IDs and add relationships
        for source_name, target_name, rel_type, strength in basic_relationships:
            source_nodes = await self.knowledge_graph.find_nodes(source_name, max_results=1)
            target_nodes = await self.knowledge_graph.find_nodes(target_name, max_results=1)
            
            if source_nodes and target_nodes:
                await self.knowledge_graph.add_relationship(
                    source_node_id=source_nodes[0].node_id,
                    target_node_id=target_nodes[0].node_id,
                    relationship_type=rel_type,
                    strength=strength,
                    confidence=0.9
                )
    
    async def learn_from_text(self, text: str, source: str = "text_input") -> Dict[str, Any]:
        """Learn knowledge from text input"""
        
        result = await self.knowledge_graph.process_text_knowledge(text, source)
        
        # Record learning event
        learning_event = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "input_text": text,
            "nodes_learned": result["nodes_added"],
            "relationships_learned": result["relationships_added"],
            "concepts_extracted": result["concepts_extracted"]
        }
        
        self.learning_history.append(learning_event)
        
        # Generate insights from new knowledge
        await self._generate_insights_from_learning(result)
        
        return result
    
    async def learn_from_interaction(self, 
                                   interaction_type: str,
                                   context: Dict[str, Any],
                                   outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Learn from system interactions"""
        
        # Extract knowledge from interaction
        knowledge_text = f"""
        Interaction: {interaction_type}
        Context: {json.dumps(context, indent=2)}
        Outcome: {json.dumps(outcome, indent=2)}
        """
        
        return await self.learn_from_text(knowledge_text, f"interaction_{interaction_type}")
    
    async def query_knowledge(self, query: KnowledgeQuery) -> Dict[str, Any]:
        """Query the knowledge base"""
        
        if query.query_type == "semantic":
            # Semantic search
            nodes = await self.knowledge_graph.find_nodes(
                query.query_text,
                min_confidence=query.min_confidence,
                max_results=query.max_results
            )
            
            results = []
            for node in nodes:
                node_data = {
                    "node_id": node.node_id,
                    "name": node.name,
                    "type": node.concept_type.value,
                    "description": node.description,
                    "confidence": node.confidence,
                    "relevance": node.relevance_score
                }
                
                if query.include_related:
                    related = await self.knowledge_graph.get_related_nodes(
                        node.node_id, max_depth=1, max_results=3
                    )
                    node_data["related"] = [
                        {
                            "name": rel_node.name,
                            "type": rel_node.concept_type.value,
                            "strength": strength
                        }
                        for rel_node, strength, depth in related
                    ]
                
                results.append(node_data)
        
        else:
            # Other query types (to be implemented)
            results = []
        
        return {
            "query_id": query.query_id,
            "query_text": query.query_text,
            "query_type": query.query_type,
            "results": results,
            "result_count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    
    async def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a natural language question"""
        return await self.reasoning_engine.answer_question(question)
    
    async def generate_insights(self) -> List[KnowledgeInsight]:
        """Generate insights from knowledge analysis"""
        
        new_insights = []
        
        # Pattern detection insights
        pattern_insights = await self._detect_knowledge_patterns()
        new_insights.extend(pattern_insights)
        
        # Relationship strength insights
        relationship_insights = await self._analyze_relationship_strengths()
        new_insights.extend(relationship_insights)
        
        # Knowledge gap insights
        gap_insights = await self._identify_knowledge_gaps()
        new_insights.extend(gap_insights)
        
        self.insights.extend(new_insights)
        return new_insights
    
    async def _detect_knowledge_patterns(self) -> List[KnowledgeInsight]:
        """Detect patterns in the knowledge graph"""
        
        insights = []
        
        # Find highly connected concepts
        node_connections = defaultdict(int)
        for rel in self.knowledge_graph.relationships.values():
            node_connections[rel.source_node_id] += 1
            node_connections[rel.target_node_id] += 1
        
        # Identify central concepts
        central_nodes = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if central_nodes:
            central_node_id, connection_count = central_nodes[0]
            central_node = self.knowledge_graph.nodes.get(central_node_id)
            
            if central_node and connection_count > 5:
                insight = KnowledgeInsight(
                    insight_id=str(uuid.uuid4()),
                    insight_type="pattern",
                    title=f"Central Knowledge Concept: {central_node.name}",
                    description=f"{central_node.name} is highly connected with {connection_count} relationships, making it a central concept in the knowledge base.",
                    evidence=[f"Node {central_node_id} has {connection_count} connections"],
                    confidence=0.8,
                    related_nodes=[central_node_id],
                    actionable=True
                )
                insights.append(insight)
        
        return insights
    
    async def _analyze_relationship_strengths(self) -> List[KnowledgeInsight]:
        """Analyze relationship patterns"""
        
        insights = []
        
        # Find strongest relationships
        strong_relationships = [
            rel for rel in self.knowledge_graph.relationships.values()
            if rel.strength > 0.8
        ]
        
        if len(strong_relationships) > 10:
            insight = KnowledgeInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="correlation",
                title="Strong Knowledge Connections",
                description=f"Found {len(strong_relationships)} strong relationships (>0.8 strength), indicating well-established knowledge patterns.",
                evidence=[f"{len(strong_relationships)} relationships with strength > 0.8"],
                confidence=0.7,
                related_nodes=[],
                actionable=False
            )
            insights.append(insight)
        
        return insights
    
    async def _identify_knowledge_gaps(self) -> List[KnowledgeInsight]:
        """Identify gaps in knowledge"""
        
        insights = []
        
        # Find isolated nodes (few connections)
        isolated_nodes = []
        for node_id, node in self.knowledge_graph.nodes.items():
            connections = sum(
                1 for rel in self.knowledge_graph.relationships.values()
                if rel.source_node_id == node_id or rel.target_node_id == node_id
            )
            
            if connections < 2:
                isolated_nodes.append((node_id, node))
        
        if len(isolated_nodes) > len(self.knowledge_graph.nodes) * 0.2:  # >20% isolated
            insight = KnowledgeInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="anomaly",
                title="Knowledge Fragmentation",
                description=f"Found {len(isolated_nodes)} isolated concepts with few connections, suggesting knowledge gaps or fragmentation.",
                evidence=[f"{len(isolated_nodes)} nodes with <2 connections"],
                confidence=0.6,
                related_nodes=[node_id for node_id, _ in isolated_nodes[:5]],
                actionable=True
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_insights_from_learning(self, learning_result: Dict[str, Any]):
        """Generate insights from recent learning"""
        
        if learning_result["nodes_added"] > 5:
            insight = KnowledgeInsight(
                insight_id=str(uuid.uuid4()),
                insight_type="pattern",
                title="Significant Learning Event",
                description=f"Added {learning_result['nodes_added']} new concepts and {learning_result['relationships_added']} relationships from recent learning.",
                evidence=[f"Learning session added {learning_result['nodes_added']} nodes"],
                confidence=0.9,
                related_nodes=learning_result.get("node_ids", [])[:5],
                actionable=False
            )
            self.insights.append(insight)
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge engine statistics"""
        
        graph_stats = self.knowledge_graph.get_graph_statistics()
        
        return {
            "knowledge_graph": graph_stats,
            "learning_events": len(self.learning_history),
            "insights_generated": len(self.insights),
            "recent_learning": self.learning_history[-5:] if self.learning_history else [],
            "recent_insights": [
                {
                    "title": insight.title,
                    "type": insight.insight_type,
                    "confidence": insight.confidence,
                    "actionable": insight.actionable
                }
                for insight in self.insights[-5:]
            ],
            "knowledge_quality": {
                "average_confidence": graph_stats.get("average_confidence", 0),
                "connectivity": len(graph_stats.get("most_connected_nodes", [])),
                "diversity": len(graph_stats.get("nodes_by_type", {}))
            }
        }

# Global knowledge engine
knowledge_engine = KnowledgeEngine()

# Convenience functions
async def learn_knowledge(text: str, source: str = "user_input") -> Dict[str, Any]:
    """Learn knowledge from text"""
    return await knowledge_engine.learn_from_text(text, source)

async def ask_question(question: str) -> Dict[str, Any]:
    """Ask a question to the knowledge engine"""
    return await knowledge_engine.answer_question(question)

async def search_knowledge(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search the knowledge base"""
    knowledge_query = KnowledgeQuery(
        query_id=str(uuid.uuid4()),
        query_text=query,
        query_type="semantic",
        max_results=max_results
    )
    return await knowledge_engine.query_knowledge(knowledge_query)

def get_knowledge_stats() -> Dict[str, Any]:
    """Get knowledge engine statistics"""
    return knowledge_engine.get_knowledge_statistics()
