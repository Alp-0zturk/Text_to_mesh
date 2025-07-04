#!/usr/bin/env python3
"""
Installation script for mesh analysis and coloring system dependencies.
Run this script to install all required packages for the intelligent mesh coloring features.
"""

import subprocess
import sys
import importlib.util

def check_package(package_name):
    """Check if a package is already installed."""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🎨 Installing Mesh Analysis and Coloring System Dependencies")
    print("=" * 65)
    
    # Required packages for the mesh coloring system
    required_packages = [
        # Core scientific computing
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        
        # Machine learning and clustering
        ("sklearn", "scikit-learn"),
        
        # Graph analysis
        ("networkx", "networkx"),
        
        # Computer vision and image processing
        ("cv2", "opencv-python"),
        ("PIL", "Pillow"),
        
        # Mesh processing (may already be installed)
        ("trimesh", "trimesh"),
        
        # Deep learning (may already be installed)
        ("torch", "torch"),
        ("transformers", "transformers"),
    ]
    
    print("Checking existing packages...")
    
    to_install = []
    already_installed = []
    
    for import_name, package_name in required_packages:
        if check_package(import_name):
            already_installed.append(package_name)
            print(f"✅ {package_name} - already installed")
        else:
            to_install.append(package_name)
            print(f"❌ {package_name} - needs installation")
    
    print(f"\nStatus: {len(already_installed)} already installed, {len(to_install)} need installation")
    
    if not to_install:
        print("\n🎉 All required packages are already installed!")
        print("You're ready to use the mesh coloring system.")
        return
    
    print(f"\n📦 Installing {len(to_install)} packages...")
    
    success_count = 0
    failed_packages = []
    
    for package in to_install:
        print(f"\nInstalling {package}...")
        if install_package(package):
            print(f"✅ Successfully installed {package}")
            success_count += 1
        else:
            print(f"❌ Failed to install {package}")
            failed_packages.append(package)
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(to_install)} packages")
    
    if failed_packages:
        print(f"❌ Failed installations: {', '.join(failed_packages)}")
        print("\n🔧 Troubleshooting tips for failed packages:")
        for package in failed_packages:
            if package == "opencv-python":
                print(f"  - {package}: Try 'pip install opencv-python-headless' instead")
            elif package == "torch":
                print(f"  - {package}: Visit https://pytorch.org for platform-specific installation")
            else:
                print(f"  - {package}: Try 'pip install --upgrade {package}'")
    else:
        print("\n🎉 All packages installed successfully!")
    
    print("\n🚀 Next Steps:")
    print("1. Run 'python main.py' for the basic interface")
    print("2. Run 'python demo_colored_meshes.py' for the full demo")
    print("3. Check 'MESH_COLORING_README.md' for detailed documentation")
    
    # Test import of key modules
    print("\n🧪 Testing key imports...")
    test_imports = [
        ("numpy", "np"),
        ("scipy", None),
        ("sklearn", None),
        ("networkx", "nx"),
        ("matplotlib.pyplot", "plt"),
    ]
    
    all_imports_successful = True
    for module, alias in test_imports:
        try:
            if alias:
                exec(f"import {module} as {alias}")
            else:
                exec(f"import {module}")
            print(f"✅ {module} import successful")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            all_imports_successful = False
    
    if all_imports_successful:
        print("\n✅ All key imports successful! The system is ready to use.")
    else:
        print("\n⚠️  Some imports failed. Please resolve the issues above.")
    
    print("\n" + "=" * 65)
    print("Installation complete! 🎨")

if __name__ == "__main__":
    main() 