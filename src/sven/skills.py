from typing import Dict, Any, List, Optional
import json

class Skill:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, args: Dict[str, Any]) -> str:
        raise NotImplementedError("Each skill must implement its own execute method.")

class SkillRegistry:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def get_tools_for_llm(self) -> list:
        """Returns a list of tool definitions for the Ollama API."""
        return [
            {
                "type": "function",
                "function": {
                    "name": s.name,
                    "description": s.description,
                    "parameters": {
                        "type": "object",
                        "properties": {}, # This can be expanded with dynamic schema generation
                        "required": []
                    }
                }
            }
            for s in self.skills.values()
        ]

    def execute_skill(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.skills:
            return f"Error: Skill '{name}' not found."
        try:
            return self.skills[name].execute(args)
        except Exception as e:
            return f"Error executing skill '{name}': {str(e)}"
