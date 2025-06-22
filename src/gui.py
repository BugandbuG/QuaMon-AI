import pygame
import os
from board import Board
from state import State
from solver import BfsSolver, DfsSolver, UcsSolver, AStarSolver

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Grid dimensions
GRID_WIDTH = 450
GRID_HEIGHT = 450
CELL_SIZE = GRID_WIDTH // 6
GRID_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
GRID_Y = (SCREEN_HEIGHT - GRID_HEIGHT) // 2
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GRID_COLOR = (128, 128, 128)
# Vehicle Colors - a map of vehicle ID to color
VEHICLE_COLORS = {
    'X': (255, 0, 0),   # Red car
    'A': (0, 255, 0),
    'B': (0, 0, 255),
    'C': (255, 255, 0),
    'D': (255, 0, 255),
    'E': (0, 255, 255),
    'F': (128, 0, 128),
    'G': (255, 165, 0),
    'H': (0, 128, 0),
    'O': (128, 128, 0),
    'P': (0, 128, 128),
    'Q': (128, 0, 0),
    'R': (255, 192, 203)
}
# UI Element dimensions
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20

class GUI:
    def __init__(self, board_files_dir):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rush Hour Solver")
        self.font = pygame.font.SysFont(None, 36)
        self.board_files = sorted([f for f in os.listdir(board_files_dir) if f.endswith('.txt')])
        self.solvers = ['BFS', 'DFS', 'UCS', 'A*']
        self.board_dir = board_files_dir
        self.clock = pygame.time.Clock()
        
        # State variables
        self.current_board_idx = 0
        self.current_solver_idx = 0
        self.current_board = None
        self.current_state = None
        self.solution_path = []
        self.is_animating = False
        self.animation_step = 0
        self.animation_timer = 0
        self.message = ""
        
        self._load_board(self.board_files[self.current_board_idx])
        self._create_buttons()

    def _create_buttons(self):
        """Create button rectangles."""
        self.buttons = {
            'prev_board': pygame.Rect(BUTTON_MARGIN, 50, 50, 50),
            'next_board': pygame.Rect(BUTTON_MARGIN + 60, 50, 50, 50),
            'prev_solver': pygame.Rect(BUTTON_MARGIN, 120, 50, 50),
            'next_solver': pygame.Rect(BUTTON_MARGIN + 60, 120, 50, 50),
            'solve': pygame.Rect(BUTTON_MARGIN, 200, BUTTON_WIDTH, BUTTON_HEIGHT),
            'play_pause': pygame.Rect(BUTTON_MARGIN, 270, BUTTON_WIDTH, BUTTON_HEIGHT),
            'reset': pygame.Rect(BUTTON_MARGIN, 340, BUTTON_WIDTH, BUTTON_HEIGHT)
        }

    def _load_board(self, board_file):
        """Loads a board and sets the initial state."""
        board_path = os.path.join(self.board_dir, board_file)
        self.current_board = Board(board_path)
        self.current_state = State(self.current_board.vehicles)
        self.solution_path = []
        self.is_animating = False
        self.animation_step = 0
        self.message = ""

    def run(self):
        """Main loop for the GUI."""
        running = True
        while running:
            time_delta = self.clock.tick(30) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event.pos)
            
            self._update_animation(time_delta)

            self.draw_background()
            self.draw_grid()
            if self.current_state:
                self.draw_vehicles(self.current_state)
            self.draw_ui()
            
            pygame.display.flip()

        pygame.quit()

    def _update_animation(self, time_delta):
        if self.is_animating:
            self.animation_timer += time_delta
            if self.animation_timer > 0.5: # Half a second per step
                self.animation_timer = 0
                if self.animation_step < len(self.solution_path) - 1:
                    self.animation_step += 1
                    self.current_state = self.solution_path[self.animation_step]
                else:
                    self.is_animating = False

    def draw_background(self):
        self.screen.fill(WHITE)

    def draw_grid(self):
        # Draw the border of the grid
        pygame.draw.rect(self.screen, GRID_COLOR, (GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT), 3)
        # Draw grid lines
        for i in range(1, 6):
            # Vertical lines
            pygame.draw.line(self.screen, GRID_COLOR, (GRID_X + i * CELL_SIZE, GRID_Y), (GRID_X + i * CELL_SIZE, GRID_Y + GRID_HEIGHT))
            # Horizontal lines
            pygame.draw.line(self.screen, GRID_COLOR, (GRID_X, GRID_Y + i * CELL_SIZE), (GRID_X + GRID_WIDTH, GRID_Y + i * CELL_SIZE))

        # Draw the exit based on the actual goal position
        if self.current_board:
            exit_y = GRID_Y + self.current_board.goal_pos[1] * CELL_SIZE
            pygame.draw.rect(self.screen, WHITE, (GRID_X + GRID_WIDTH - 3, exit_y, 6, CELL_SIZE))

    def draw_vehicles(self, state):
        """Draws all vehicles from a given state."""
        for vehicle in state.vehicles.values():
            color = VEHICLE_COLORS.get(vehicle.id, GRAY)
            if vehicle.orientation == 'h':
                rect = pygame.Rect(GRID_X + vehicle.x * CELL_SIZE, GRID_Y + vehicle.y * CELL_SIZE, vehicle.length * CELL_SIZE, CELL_SIZE)
            else: # 'v'
                rect = pygame.Rect(GRID_X + vehicle.x * CELL_SIZE, GRID_Y + vehicle.y * CELL_SIZE, CELL_SIZE, vehicle.length * CELL_SIZE)
            
            pygame.draw.rect(self.screen, color, rect)
            # Add a border to the vehicle
            pygame.draw.rect(self.screen, BLACK, rect, 2)

    def _handle_click(self, pos):
        if self.buttons['solve'].collidepoint(pos) and not self.solution_path:
            self._solve_puzzle()
        elif self.buttons['play_pause'].collidepoint(pos) and self.solution_path:
            self.is_animating = not self.is_animating
        elif self.buttons['reset'].collidepoint(pos):
            self._load_board(self.board_files[self.current_board_idx])
        elif self.buttons['prev_board'].collidepoint(pos):
            self.current_board_idx = (self.current_board_idx - 1) % len(self.board_files)
            self._load_board(self.board_files[self.current_board_idx])
        elif self.buttons['next_board'].collidepoint(pos):
            self.current_board_idx = (self.current_board_idx + 1) % len(self.board_files)
            self._load_board(self.board_files[self.current_board_idx])
        elif self.buttons['prev_solver'].collidepoint(pos):
            self.current_solver_idx = (self.current_solver_idx - 1) % len(self.solvers)
        elif self.buttons['next_solver'].collidepoint(pos):
            self.current_solver_idx = (self.current_solver_idx + 1) % len(self.solvers)
    
    def _solve_puzzle(self):
        self.message = "Solving..."
        solver_name = self.solvers[self.current_solver_idx]
        solver_map = {
            'BFS': BfsSolver,
            'DFS': DfsSolver,
            'UCS': UcsSolver,
            'A*': AStarSolver
        }
        solver_class = solver_map[solver_name]
        solver = solver_class(self.current_board, State(self.current_board.vehicles))
        
        self.solution_path = solver.solve()
        
        if self.solution_path:
            self.is_animating = True
            self.animation_step = 0
            self.message = f"Solution found in {len(self.solution_path) - 1} moves."
        else:
            self.message = "No solution found."

    def draw_ui(self):
        """Draws the user interface elements."""
        # Board selection
        board_text = self.font.render(f"Board: {self.board_files[self.current_board_idx]}", True, BLACK)
        self.screen.blit(board_text, (self.buttons['prev_board'].right + 30, 60))
        self.draw_button("<", self.buttons['prev_board'])
        self.draw_button(">", self.buttons['next_board'])
        
        # Solver selection
        solver_text = self.font.render(f"Solver: {self.solvers[self.current_solver_idx]}", True, BLACK)
        self.screen.blit(solver_text, (self.buttons['prev_solver'].right + 30, 130))
        self.draw_button("<", self.buttons['prev_solver'])
        self.draw_button(">", self.buttons['next_solver'])

        # Solve button
        self.draw_button("Solve", self.buttons['solve'])
        # Play/Pause button
        play_pause_text = "Pause" if self.is_animating else "Play"
        self.draw_button(play_pause_text, self.buttons['play_pause'])
        # Reset button
        self.draw_button("Reset", self.buttons['reset'])
        # Message display
        if self.message:
            msg_surf = self.font.render(self.message, True, BLACK)
            self.screen.blit(msg_surf, (self.buttons['reset'].left, self.buttons['reset'].bottom + 20))
        # Step count
        if self.solution_path:
            step_text = f"Step: {self.animation_step + 1}/{len(self.solution_path)}"
            step_surf = self.font.render(step_text, True, BLACK)
            self.screen.blit(step_surf, (GRID_X, GRID_Y - 40))

    def draw_button(self, text, rect, color=GRAY):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect) 