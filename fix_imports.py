#!/usr/bin/env python3
"""
Script to fix all import paths in backend Python files to use absolute imports.
"""
import os
import re

def fix_imports_in_file(filepath):
    """Fix imports in a single file to use absolute backend imports."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Patterns to fix: from ai.*, from models.*, from utils.*, etc.
        patterns = [
            (r'from\s+(ai|models|routes|utils|config|middleware)\b', r'from backend.\1'),
            (r'import\s+(ai|models|routes|utils|config|middleware)\b', r'import backend.\1'),
        ]

        original_content = content
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Fixed imports in {filepath}")
        else:
            print(f"⏭️  No changes needed in {filepath}")

    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def fix_all_imports():
    """Fix imports in all Python files in backend directory."""
    backend_dir = "backend"
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                fix_imports_in_file(filepath)

if __name__ == "__main__":
    fix_all_imports()
    print("🎉 Import fixing complete!")