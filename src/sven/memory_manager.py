from dataclasses import dataclass, field
from typing import List, Optional
import time
import uuid
import re
import json
import os

# Import storage manager to persist facts
from .storage_manager import load_session, save_session

@dataclass
class Fact:
    id: str
    content: str
    score: float = 0.0
    category: str = "general"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "category": self.category,
            "timestamp": self.timestamp
        }

class MemoryManager:
    def __init__(self):
        self.facts: List[Fact] = []
        # Keywords that indicate high importance
        self.high_priority_keywords = [
            "must", "should", "always", "never", "requirement", 
            "constraint", "important", "critical", "note:", "remember"
        ]
        self._load_from_storage()

    def _load_from_storage(self):
        """
        Load facts from the session storage.
        """
        state = load_session()
        saved_facts = state.get("facts", [])
        if isinstance(saved_facts, list):
            self.facts = [
                Fact(
                    id=f["id"],
                    content=f["content"],
                    score=float(f["score"]),
                    category=f["category"],
                    timestamp=float(f["timestamp"])
                )
                for f in saved_facts
            ]

    def save_to_storage(self):
        """
        Save current facts to the session storage.
        """
        state = {
            "facts": [f.to_dict() for f in self.facts]
        }
        save_session(state)

    def add_fact(self, content: str, category: str = "general") -> Fact:
        """
        Extracts facts from a string and adds them to the memory.
        In a real implementation, this would use an LLM or more complex NLP.
        For now, we'll do some basic heuristic-based extraction.
        """
        # Basic logic: if it contains certain keywords, it might be a fact.
        # We also check for specific entities like filenames or variable names.
        
        # Simple heuristic: split by sentences and evaluate each.
        sentences = re.split(r'[.!?\n]', content)
        new_facts = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:
                continue
            
            score = 10.0
            # Boost score if it contains high priority keywords
            if any(kw in sentence.lower() for kw in self.high_priority_keywords):
                score += 20.0
            
            # Boost score if it mentions files or specific technical terms (heuristic)
            if re.search(r'(\w+\.(py|json|md|txt))', sentence):
                score += 15.0
            
            if score > 10: # Only just keep things that meet a minimum threshold
                fact = Fact(
                    id=str(uuid.uuid4()),
                    content=sentence,
                    score=score,
                    category=category
                )
                new_facts.append(fact)
        
        self.facts.extend(new_facts)
        # Persist the new facts immediately
        self.save_to_storage()
        return new_facts

    def update_scores(self):
        """
        Update scores based on recency and frequency.
        Recency: Facts from the last 10 minutes get a boost.
        Frequency: If multiple facts have similar content, they are grouped (simplified here).
        """
        now = time.time()
        for fact in self.facts:
            # Recency boost
            if now - fact.timestamp < 600: # Last 10 minutes
                fact.score += 5.0
            
            # Decay score over time (simple linear decay)
            # This is a placeholder for more complex logic.
            pass
        
        # Save updated scores
        self.save_to_storage()

    def get_high_value_facts(self, limit: int = 20) -> List[Fact]:
        """
        Returns the top N facts based on their scores.
        """
        # Sort by score descending
        sorted_facts = sorted(self.facts, key=lambda x: x.score, reverse=True)
        return sorted_facts[:limit]

    def prune_low_value_facts(self, threshold: float = 10.0):
        """
        Remove facts that fall below a certain score threshold.
        """
        initial_count = len(self.facts)
        self.facts = [f for f in self.facts if f.score >= threshold]
        if len(self.facts) != initial_count:
            self.save_to_storage()
        return len(self.facts)
