import sys
import os

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui import GUI

def main():
    """
    Main function to run the Rush Hour GUI.
    """
    boards_dir = 'test_map'
    gui = GUI(boards_dir)
    gui.run()

if __name__ == "__main__":
    main() 