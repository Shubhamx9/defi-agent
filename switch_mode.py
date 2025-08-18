#!/usr/bin/env python3
"""
Simple script to switch between Demo and Production modes
"""
import os
import sys

def update_env_file(demo_mode: bool):
    """Update the .env file with the new mode setting"""
    env_path = "backend/.env"
    
    if not os.path.exists(env_path):
        print(f"❌ .env file not found at {env_path}")
        print("💡 Copy backend/.env.example to backend/.env first")
        return False
    
    # Read current .env file
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update USE_DEMO_MODE setting
    updated_lines = []
    mode_found = False
    
    for line in lines:
        if line.startswith('USE_DEMO_MODE='):
            updated_lines.append(f'USE_DEMO_MODE={str(demo_mode).lower()}\n')
            mode_found = True
        else:
            updated_lines.append(line)
    
    # Add the setting if it doesn't exist
    if not mode_found:
        updated_lines.append(f'\n# System Mode\nUSE_DEMO_MODE={str(demo_mode).lower()}\n')
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(updated_lines)
    
    return True

def main():
    """Main function to handle mode switching"""
    if len(sys.argv) != 2:
        print("🔄 DeFi AI Assistant Mode Switcher")
        print("=" * 40)
        print("Usage:")
        print("  python switch_mode.py demo       # Switch to Demo Mode")
        print("  python switch_mode.py production # Switch to Production Mode")
        print()
        print("Current mode check:")
        print("  curl http://localhost:8000/health/mode")
        return
    
    mode = sys.argv[1].lower()
    
    if mode in ['demo', 'd', 'mock', 'test']:
        demo_mode = True
        mode_name = "Demo Mode"
        description = "Mock responses, no external APIs, 100% reliable"
    elif mode in ['production', 'prod', 'p', 'real']:
        demo_mode = False
        mode_name = "Production Mode"
        description = "Real AI APIs, external services, variable reliability"
    else:
        print(f"❌ Invalid mode: {mode}")
        print("Valid options: demo, production")
        return
    
    print(f"🔄 Switching to {mode_name}...")
    
    if update_env_file(demo_mode):
        print(f"✅ Successfully switched to {mode_name}")
        print(f"📝 Description: {description}")
        print()
        print("🔄 Next steps:")
        print("1. Restart your backend server:")
        print("   cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print()
        print("2. Verify the mode switch:")
        print("   curl http://localhost:8000/health/mode")
        print()
        
        if demo_mode:
            print("🎯 Demo Mode Benefits:")
            print("   ✅ No API keys required")
            print("   ✅ Lightning fast responses")
            print("   ✅ 100% reliable for demos")
            print("   ✅ No external dependencies")
        else:
            print("⚠️  Production Mode Requirements:")
            print("   🔑 Valid API keys needed")
            print("   🌐 External services must be running")
            print("   💰 API usage costs apply")
            print("   📊 Real AI responses")
    else:
        print("❌ Failed to update .env file")

if __name__ == "__main__":
    main()