"""
__init__.py
─────────────────────────────────────────────────────────────
PURPOSE:
    This file makes the 'modules' folder a Python PACKAGE.

WHY IS IT NEEDED?
    Without this file, Python won't recognize the 'modules'
    folder as something you can import from.
    
    With this file:
        from modules.constants import CELL_SIZE   ← Works!
    
    Without this file:
        from modules.constants import CELL_SIZE   ← ImportError!

THE FILE CAN BE EMPTY — its mere existence is what matters.
We just added this explanation so you understand its role.
─────────────────────────────────────────────────────────────
"""
