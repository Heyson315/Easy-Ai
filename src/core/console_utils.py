"""
Console utilities for M365 Security Toolkit.

Provides consistent console output formatting for scripts and demos.
"""


def print_header(title: str, width: int = 80, char: str = "=") -> None:
    """
    Print a formatted section header to console.
    
    Args:
        title: The title text to display
        width: Total width of the header line (default: 80)
        char: Character to use for the border (default: "=")
        
    Example:
        print_header("Demo 1: Simple Chat")
        # Outputs:
        # ================================================================================
        #   Demo 1: Simple Chat
        # ================================================================================
    """
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")
