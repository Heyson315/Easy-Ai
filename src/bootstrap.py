"""
Bootstrap utilities for setting up Python import paths.

This module has NO dependencies on other src modules to avoid circular imports.
It must be imported first before any other src modules.
"""

import sys
from pathlib import Path


def setup_project_path(script_file: str) -> Path:
    """
    Setup Python path for scripts in the scripts/ directory to import from src/.
    
    This is a common pattern needed by standalone scripts that need to import
    from the src/ package.
    
    Args:
        script_file: The __file__ variable from the calling script
        
    Returns:
        The project root path
        
    Example:
        # At the top of a script in scripts/ directory (BEFORE other src imports):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Now you can import from src:
        from src.core.cost_tracker import GPT5CostTracker
        
    Note:
        This function is here for documentation purposes. Due to Python's import
        system, you must set up the path BEFORE importing this function. Therefore,
        you should use the inline pattern shown in the example above.
    """
    project_root = Path(script_file).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root
