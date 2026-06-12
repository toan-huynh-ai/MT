"""
Setup Configuration for Bahnar Translation
============================================
Configure environment variables and paths for translation experiments.
Run this once to verify your setup.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)


def check_environment():
    """Verify all required environment variables are set."""
    required_vars = [
        "AZURE_TENANT_ID",
        "APPLICATION_AI_VOS_USERS_ID",
        "APPLICATION_AI_VOS_USERS_SECRET",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_API_VERSION",
        "AZURE_CHAT_DEPLOYMENT",
    ]
    
    print("="*70)
    print("ENVIRONMENT VERIFICATION")
    print("="*70)
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive values
            display_value = value[:20] + "..." if len(str(value)) > 20 else value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"✗ {var}: NOT SET")
            missing.append(var)
    
    if missing:
        print(f"\n⚠ Missing environment variables: {', '.join(missing)}")
        print(f"   Please set them in: {dotenv_path}")
        return False
    
    print("\n✓ All environment variables are set!")
    return True


def check_data_files():
    """Verify data files exist."""
    print("\n" + "="*70)
    print("DATA FILES VERIFICATION")
    print("="*70)
    
    data_path = Path(r"C:\Users\HOY9HC\Desktop\Code\Learning\MT2\bahnar\data\vi_bahnar.jsonl")
    
    if data_path.exists():
        size_mb = data_path.stat().st_size / (1024 * 1024)
        print(f"✓ Data file found: {data_path}")
        print(f"  Size: {size_mb:.2f} MB")
        
        # Count lines
        with open(data_path, "r", encoding="utf-8") as f:
            count = sum(1 for _ in f)
        print(f"  Records: {count}")
        return True
    else:
        print(f"✗ Data file not found: {data_path}")
        return False


def check_output_directory():
    """Create output directory if needed."""
    print("\n" + "="*70)
    print("OUTPUT DIRECTORY SETUP")
    print("="*70)
    
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    print(f"✓ Output directory ready: {output_dir}")
    return True


def check_dependencies():
    """Verify required Python packages."""
    print("\n" + "="*70)
    print("DEPENDENCY CHECK")
    print("="*70)
    
    required_packages = [
        ("dotenv", "python-dotenv"),
        ("openai", "openai"),
        ("azure.identity", "azure-identity"),
        ("httpx", "httpx"),
        ("sacrebleu", "sacrebleu"),
    ]
    
    all_ok = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - NOT INSTALLED")
            print(f"   Install with: pip install {package_name}")
            all_ok = False
    
    return all_ok


def main():
    """Run all checks."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "BAHNAR TRANSLATION SETUP" + " "*29 + "║")
    print("╚" + "="*68 + "╝")
    
    checks = [
        ("Environment Variables", check_environment),
        ("Data Files", check_data_files),
        ("Output Directory", check_output_directory),
        ("Dependencies", check_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("SETUP SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "="*70)
    if all_pass:
        print("✓ Setup complete! You can now run the translation scripts:")
        print("  - python translate_vi_to_bahnar_zeroshot.py")
        print("  - python translate_bahnar_to_vi_zeroshot.py")
    else:
        print("✗ Setup incomplete. Please fix the issues above.")
        sys.exit(1)
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
