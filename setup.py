import os
import sys

def setup_environment():
    # Ensure uploads directory exists
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✓ Created uploads directory")
      # Ensure Exam_GRP_SMUAPP directory exists
    if not os.path.exists('C:\\Exam_GRP_SMUAPP'):
        os.makedirs('C:\\Exam_GRP_SMUAPP')
        print("✓ Created C:\\Exam_GRP_SMUAPP directory")
    
    # Ensure Exam_DAY_Smart directory exists
    if not os.path.exists('C:\\Exam_DAY_Smart'):
        os.makedirs('C:\\Exam_DAY_Smart')
        print("✓ Created C:\\Exam_DAY_Smart directory")
    
    # Set UTF-8 as default encoding
    if sys.stdout.encoding != 'utf-8':
        print("⚠ Warning: Terminal encoding is not UTF-8")
        print(f"Current encoding: {sys.stdout.encoding}")
        print("Please run the server with PYTHONIOENCODING=utf-8")
    
    print("\nSetup completed successfully!")
    print("\nTo start the server:")
    print("1. Run: python server.py")
    print("2. In another terminal, run: npm start")

if __name__ == '__main__':
    setup_environment()
