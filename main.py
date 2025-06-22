import sys
import os

# Add src to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from board import Board
from state import State
from solver import BfsSolver, DfsSolver, UcsSolver, AStarSolver

def main():
    """
    Main function to run the Rush Hour solver.
    """
    if len(sys.argv) != 2 or sys.argv[1] not in ['bfs', 'dfs', 'ucs', 'astar']:
        print("Usage: python main.py <bfs|dfs|ucs|astar>")
        sys.exit(1)

    solver_type = sys.argv[1]
    board_file = 'boards/actually_hard.txt'
    board = Board(board_file)
    initial_state = State(board.vehicles)
    
    if solver_type == 'bfs':
        solver = BfsSolver(board, initial_state)
    elif solver_type == 'dfs':
        solver = DfsSolver(board, initial_state)
    elif solver_type == 'ucs':
        solver = UcsSolver(board, initial_state)
    else: # astar
        solver = AStarSolver(board, initial_state)
    
    path = solver.solve()

    if path:
        print(f"Solution found in {len(path) - 1} moves using {solver_type.upper()}.")
        for i, state in enumerate(path):
            print(f"Move {i}:")
            grid = state._create_grid(board)
            for row in grid:
                print("".join(row))
            print()
    else:
        print("No solution found.")

if __name__ == "__main__":
    main() 