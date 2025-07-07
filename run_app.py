#!/usr/bin/env python3
"""
Startup script for the Data Analysis Application
This script handles environment setup and starts the Flask application.
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    # Package names as they appear in imports vs pip install names
    package_mapping = {
        'flask': 'flask',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'plotly': 'plotly',
        'sklearn': 'scikit-learn',  # sklearn is the import name for scikit-learn
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'scipy': 'scipy'
    }
    
    missing_packages = []
    for import_name, pip_name in package_mapping.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ['uploads', 'uploads/models', 'instance']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created/verified directory: {directory}")

def setup_environment():
    """Set up environment variables"""
    if not os.getenv('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        print("🔑 Set default SECRET_KEY (change for production!)")
    
    if not os.getenv('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///eda_app.db'
        print("🗄️  Using SQLite database")

def initialize_database():
    """Initialize the database"""
    try:
        from app import app, db
        with app.app_context():
            # Import models to ensure tables are created
            import models
            db.create_all()
            print("✅ Database initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def start_application():
    """Start the Flask application"""
    try:
        from app import app
        print("\n🚀 Starting Data Analysis Application...")
        print("📊 Application will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the application\n")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🔧 Setting up Data Analysis Application...\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup directories
    print("\n📁 Setting up directories...")
    setup_directories()
    
    # Setup environment
    print("\n⚙️  Setting up environment...")
    setup_environment()
    
    # Initialize database
    print("\n🗄️  Initializing database...")
    if not initialize_database():
        sys.exit(1)
    
    # Start application
    start_application()

if __name__ == '__main__':
    main()