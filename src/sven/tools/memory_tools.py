"""Tools for managing Sven's skill/knowledge base.

Skills are persistent pieces of knowledge that Sven has learned:
- Facts, preferences, patterns, or procedures
- Each has a name + description for discovery
- Optional content with the full details
- Tags for categorization and search

The LLM can list skills by description to decide what's relevant,
then retrieve full content when needed.
"""

from pathlib import Path
from sven.memory import get_store


def _get_memory_store() -> "MemoryStore":
    """Get the memory store from the config."""
    from sven.config import Config
    config = Config.load()
    return get_store(config.data_dir)


def add_skill(name: str, description: str, content: str = "", tags: list[str] | None = None) -> dict:
    """Store a new skill/fact/preference.

    Args:
        name: Short identifier (e.g., "python_style", "user_preference")
        description: Brief description for discovery by the LLM
        content: The actual learned information or pattern
        tags: Optional list of tags for categorization

    Returns:
        Success status and stored skill data
    """
    try:
        store = _get_memory_store()
        skill = store.add(name=name, description=description, content=content, tags=tags)
        return {
            "success": True,
            "message": f"Skill '{name}' stored successfully",
            "data": skill.to_dict()
        }
    except ValueError as e:
        return {"success": False, "message": str(e), "data": None}


def list_skills() -> dict:
    """List all available skills with their descriptions.

    Returns:
        List of skills (without full content) for the LLM to decide what's relevant
    """
    try:
        store = _get_memory_store()
        skills = store.list_all()
        return {
            "success": True,
            "message": f"Found {len(skills)} skill(s)",
            "data": skills
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}


def get_skill(identifier: str) -> dict:
    """Retrieve a skill by name or ID.

    Args:
        identifier: Skill name or ID to retrieve

    Returns:
        Full skill data including content
    """
    try:
        store = _get_memory_store()
        skill = store.get(identifier)
        if skill is None:
            return {"success": False, "message": f"Skill '{identifier}' not found", "data": None}
        return {
            "success": True,
            "message": f"Retrieved skill '{skill.name}'",
            "data": skill.to_dict()
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def update_skill(identifier: str, **fields) -> dict:
    """Update fields of an existing skill.

    Args:
        identifier: Skill name or ID to update
        **fields: Fields to update (name, description, content, tags)

    Returns:
        Updated skill data
    """
    try:
        store = _get_memory_store()
        skill = store.update(identifier, **fields)
        if skill is None:
            return {"success": False, "message": f"Skill '{identifier}' not found", "data": None}
        return {
            "success": True,
            "message": f"Updated skill '{skill.name}'",
            "data": skill.to_dict()
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def delete_skill(identifier: str) -> dict:
    """Delete a skill by name or ID.

    Args:
        identifier: Skill name or ID to delete

    Returns:
        Success status
    """
    try:
        store = _get_memory_store()
        deleted = store.delete(identifier)
        if not deleted:
            return {"success": False, "message": f"Skill '{identifier}' not found", "data": None}
        return {
            "success": True,
            "message": f"Deleted skill '{identifier}'",
            "data": True
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": None}


def search_skills(query: str) -> dict:
    """Search skills by description or tags.

    Args:
        query: Search string to match against descriptions and tags

    Returns:
        List of matching skills (without full content)
    """
    try:
        store = _get_memory_store()
        all_skills = store.list_all()
        
        # Simple case-insensitive search in description and tags
        query_lower = query.lower()
        matches = []
        for skill in all_skills:
            desc_match = query_lower in skill["description"].lower()
            tag_match = any(query_lower in tag.lower() for tag in skill.get("tags", []))
            if desc_match or tag_match:
                matches.append(skill)
        
        return {
            "success": True,
            "message": f"Found {len(matches)} matching skill(s)",
            "data": matches
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}