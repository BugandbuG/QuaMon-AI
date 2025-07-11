import pygame
import os
from board import Board
from state import State
from solver import BfsSolver, DfsSolver, UcsSolver, AStarSolver

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 1050  # Increased width to accommodate better spacing
SCREEN_HEIGHT = 780  # Increased height for performance metrics with cost
# Grid dimensions
GRID_WIDTH = 450
GRID_HEIGHT = 450
CELL_SIZE = GRID_WIDTH // 6
GRID_X = 330  # Moved slightly further right to ensure no overlap
GRID_Y = 100
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
GRID_COLOR = (128, 128, 128)
BUTTON_COLOR = (220, 220, 220)
HOVER_COLOR = (180, 180, 180)
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
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 32, bold=True)
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
        self.mouse_pos = (0, 0)
        self.performance_metrics = None  # Add performance metrics storage
        
        self._load_board(self.board_files[self.current_board_idx])
        self._create_buttons()

    def _create_buttons(self):
        """Create button rectangles."""
        self.buttons = {
            'prev_board': pygame.Rect(40, 105, 50, 40),  # Adjusted to new control panel position
            'next_board': pygame.Rect(100, 105, 50, 40),
            'prev_solver': pygame.Rect(40, 175, 50, 40),
            'next_solver': pygame.Rect(100, 175, 50, 40),
            'solve': pygame.Rect(40, 255, 170, 50),  # Made slightly wider
            'play_pause': pygame.Rect(40, 315, 170, 50),
            'reset': pygame.Rect(40, 375, 170, 50)
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
        self.performance_metrics = None  # Clear performance metrics

    def run(self):
        """Main loop for the GUI."""
        running = True
        while running:
            time_delta = self.clock.tick(30) / 1000.0
            self.mouse_pos = pygame.mouse.get_pos()
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
        
        # Draw a subtle background for the control panel with rounded corners
        control_panel = pygame.Rect(20, 40, 270, 690)  # Slightly adjusted position and size
        pygame.draw.rect(self.screen, LIGHT_GRAY, control_panel, border_radius=15)
        pygame.draw.rect(self.screen, DARK_GRAY, control_panel, 2, border_radius=15)

    def draw_grid(self):
        # Draw a background for the grid with rounded corners
        grid_bg = pygame.Rect(GRID_X - 10, GRID_Y - 10, GRID_WIDTH + 20, GRID_HEIGHT + 20)
        pygame.draw.rect(self.screen, LIGHT_GRAY, grid_bg, border_radius=15)
        pygame.draw.rect(self.screen, DARK_GRAY, grid_bg, 3, border_radius=15)
        
        # Draw the main grid area with rounded corners
        pygame.draw.rect(self.screen, WHITE, (GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT), border_radius=10)
        
        # Draw grid lines
        for i in range(1, 6):
            # Vertical lines
            pygame.draw.line(self.screen, GRID_COLOR, (GRID_X + i * CELL_SIZE, GRID_Y), (GRID_X + i * CELL_SIZE, GRID_Y + GRID_HEIGHT), 1)
            # Horizontal lines
            pygame.draw.line(self.screen, GRID_COLOR, (GRID_X, GRID_Y + i * CELL_SIZE), (GRID_X + GRID_WIDTH, GRID_Y + i * CELL_SIZE), 1)

        # Draw the exit based on the actual goal position with rounded corners
        if self.current_board:
            exit_y = GRID_Y + self.current_board.goal_pos[1] * CELL_SIZE
            exit_rect = pygame.Rect(GRID_X + GRID_WIDTH - 10, exit_y + 5, 20, CELL_SIZE - 10)
            pygame.draw.rect(self.screen, (255, 200, 200), exit_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 0, 0), exit_rect, 2, border_radius=8)

    def draw_vehicles(self, state):
        """Draws all vehicles from a given state."""
        for vehicle in state.vehicles.values():
            color = VEHICLE_COLORS.get(vehicle.id, GRAY)
            if vehicle.orientation == 'h':
                rect = pygame.Rect(GRID_X + vehicle.x * CELL_SIZE + 2, GRID_Y + vehicle.y * CELL_SIZE + 2, 
                                 vehicle.length * CELL_SIZE - 4, CELL_SIZE - 4)
            else: # 'v'
                rect = pygame.Rect(GRID_X + vehicle.x * CELL_SIZE + 2, GRID_Y + vehicle.y * CELL_SIZE + 2, 
                                 CELL_SIZE - 4, vehicle.length * CELL_SIZE - 4)
            
            # Draw vehicle with rounded corners
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            # Add a border to the vehicle with rounded corners
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
            
            # Draw vehicle ID on the vehicle
            if rect.width > 30 and rect.height > 30:  # Only if vehicle is big enough
                text_surf = self.small_font.render(vehicle.id, True, BLACK)
                text_rect = text_surf.get_rect(center=rect.center)
                self.screen.blit(text_surf, text_rect)

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
        self.performance_metrics = None  # Reset metrics
        solver_name = self.solvers[self.current_solver_idx]
        solver_map = {
            'BFS': BfsSolver,
            'DFS': DfsSolver,
            'UCS': UcsSolver,
            'A*': AStarSolver
        }
        solver_class = solver_map[solver_name]
        solver = solver_class(self.current_board, State(self.current_board.vehicles))
        
        # Use multiple runs for more accurate measurements
        self.solution_path, self.performance_metrics = solver.solve_with_multiple_runs(num_runs=3)
        
        if self.solution_path:
            self.is_animating = True
            self.animation_step = 0
            self.animation_timer = 0
            self.current_state = self.solution_path[0]
            self.message = f"Solution found! ({len(self.solution_path)} steps)"
        else:
            self.message = "No solution found!"
            self.performance_metrics = None

    def draw_ui(self):
        """Draws the user interface elements."""
        # Title
        title_text = self.title_font.render("Rush Hour Solver", True, BLACK)
        self.screen.blit(title_text, (40, 15))  # Adjusted to match new control panel position
        
        # Board selection
        board_label = self.font.render("Board:", True, BLACK)
        self.screen.blit(board_label, (40, 75))  # Adjusted position
        # Truncate filename if too long
        board_name = self.board_files[self.current_board_idx]
        display_name = board_name
        if len(board_name) > 15:
            display_name = board_name[:12] + "..."
        board_text = self.font.render(f"{display_name}", True, BLACK)
        board_text_rect = pygame.Rect(160, 110, board_text.get_width(), board_text.get_height())
        self.screen.blit(board_text, (160, 110))
        
        # Show full filename on hover
        if board_text_rect.collidepoint(self.mouse_pos) and len(board_name) > 15:
            tooltip_surf = self.small_font.render(board_name, True, BLACK)
            tooltip_rect = pygame.Rect(self.mouse_pos[0] + 10, self.mouse_pos[1] - 30, 
                                     tooltip_surf.get_width() + 10, tooltip_surf.get_height() + 6)
            pygame.draw.rect(self.screen, (255, 255, 200), tooltip_rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, tooltip_rect, 1, border_radius=8)
            self.screen.blit(tooltip_surf, (tooltip_rect.x + 5, tooltip_rect.y + 3))
        self.draw_button("<", self.buttons['prev_board'], BUTTON_COLOR)
        self.draw_button(">", self.buttons['next_board'], BUTTON_COLOR)
        
        # Solver selection
        solver_label = self.font.render("Solver:", True, BLACK)
        self.screen.blit(solver_label, (40, 145))  # Adjusted position
        solver_text = self.font.render(f"{self.solvers[self.current_solver_idx]}", True, BLACK)
        self.screen.blit(solver_text, (160, 180))
        self.draw_button("<", self.buttons['prev_solver'], BUTTON_COLOR)
        self.draw_button(">", self.buttons['next_solver'], BUTTON_COLOR)

        # Add separator line
        pygame.draw.line(self.screen, DARK_GRAY, (40, 235), (220, 235), 2)

        # Solve button
        solve_enabled = not self.solution_path and not self.is_animating
        solve_color = BUTTON_COLOR if solve_enabled else HOVER_COLOR
        self.draw_button("Solve", self.buttons['solve'], solve_color)
        
        # Play/Pause button
        play_pause_text = "Pause" if self.is_animating else "Play"
        play_enabled = bool(self.solution_path)
        play_color = BUTTON_COLOR if play_enabled else HOVER_COLOR
        self.draw_button(play_pause_text, self.buttons['play_pause'], play_color)
        
        # Reset button
        self.draw_button("Reset", self.buttons['reset'], BUTTON_COLOR)
        
        # Step count
        if self.solution_path:
            step_text = f"Step: {self.animation_step + 1}/{len(self.solution_path)}"
            step_surf = self.font.render(step_text, True, BLACK)
            # Add background for step counter
            step_bg = pygame.Rect(GRID_X - 5, GRID_Y - 50, step_surf.get_width() + 10, 35)
            pygame.draw.rect(self.screen, WHITE, step_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, step_bg, 1, border_radius=8)
            self.screen.blit(step_surf, (GRID_X, GRID_Y - 40))
        
        # Message display
        if self.message:
            # Position message better and add background
            msg_bg = pygame.Rect(35, 435, 210, 50)  # Adjusted to new control panel
            pygame.draw.rect(self.screen, WHITE, msg_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, msg_bg, 1, border_radius=8)
            
            # Check if message is too long and wrap if needed
            msg_text = self.message
            if len(msg_text) > 25:
                # Split long messages into two lines
                words = msg_text.split()
                if len(words) > 3:
                    mid = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                    msg_surf1 = self.small_font.render(line1, True, BLACK)
                    msg_surf2 = self.small_font.render(line2, True, BLACK)
                    self.screen.blit(msg_surf1, (42, 440))
                    self.screen.blit(msg_surf2, (42, 460))
                else:
                    msg_surf = self.small_font.render(msg_text, True, BLACK)
                    self.screen.blit(msg_surf, (42, 450))
            else:
                msg_surf = self.small_font.render(msg_text, True, BLACK)
                self.screen.blit(msg_surf, (42, 450))
        
        # Performance metrics display
        if self.performance_metrics:
            metrics_y = 495  # Adjusted position
            metrics_bg = pygame.Rect(35, metrics_y - 5, 250, 165)  # Wider to accommodate new panel
            pygame.draw.rect(self.screen, WHITE, metrics_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, metrics_bg, 1, border_radius=8)
            
            # Title with number of runs
            runs_info = f" (avg of {self.performance_metrics.get('runs', 1)} runs)" if 'runs' in self.performance_metrics else ""
            title_surf = self.small_font.render(f"Performance Metrics{runs_info}:", True, BLACK)
            self.screen.blit(title_surf, (42, metrics_y))
            
            # Time with standard deviation
            time_val = self.performance_metrics['time']
            time_str = f"{time_val:.3f}s" if time_val >= 1 else f"{time_val*1000:.1f}ms"
            if 'time_std' in self.performance_metrics and self.performance_metrics['time_std'] > 0:
                std_str = f" (±{self.performance_metrics['time_std']*1000:.1f}ms)" if time_val < 1 else f" (±{self.performance_metrics['time_std']:.3f}s)"
                time_str += std_str
            time_surf = self.small_font.render(f"Time: {time_str}", True, BLACK)
            self.screen.blit(time_surf, (42, metrics_y + 20))
            
            # Memory with standard deviation
            mem_str = f"{self.performance_metrics['memory_mb']:.2f} MB"
            if 'memory_std' in self.performance_metrics and self.performance_metrics['memory_std'] > 0:
                mem_str += f" (±{self.performance_metrics['memory_std']:.2f})"
            mem_surf = self.small_font.render(f"Memory: {mem_str}", True, BLACK)
            self.screen.blit(mem_surf, (42, metrics_y + 40))
            
            # Total cost
            cost_surf = self.small_font.render(f"Total Cost: {self.performance_metrics['total_cost']}", True, BLACK)
            self.screen.blit(cost_surf, (42, metrics_y + 60))
            
            # Nodes explored
            nodes_surf = self.small_font.render(f"Nodes Explored: {self.performance_metrics['nodes_explored']}", True, BLACK)
            self.screen.blit(nodes_surf, (42, metrics_y + 80))
            
            # Total nodes
            total_surf = self.small_font.render(f"Total Nodes: {self.performance_metrics['total_nodes']}", True, BLACK)
            self.screen.blit(total_surf, (42, metrics_y + 100))
            
            # Solution length
            if self.performance_metrics['solution_length'] > 0:
                sol_surf = self.small_font.render(f"Solution: {self.performance_metrics['solution_length']} steps", True, BLACK)
                self.screen.blit(sol_surf, (42, metrics_y + 120))
            
        # Instructions - only show when no solution is loaded and no metrics
        if not self.solution_path and not self.message and not self.performance_metrics:
            # Add some spacing before instructions
            instruction_y_start = 445  # Adjusted position
            
            # Draw a subtle background for instructions
            inst_bg = pygame.Rect(35, 440, 210, 165)  # Adjusted to new panel size
            pygame.draw.rect(self.screen, WHITE, inst_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, inst_bg, 1, border_radius=8)
            
            instructions = [
                "1. Select a board and solver",
                "2. Click 'Solve' to find solution", 
                "3. Click 'Play' to animate solution",
                "",
                "Cost calculation:",
                "BFS/DFS: 1 move = 1 cost",
                "UCS/A*: cost = vehicle length"
            ]
            for i, instruction in enumerate(instructions):
                if instruction:  # Only render non-empty lines
                    inst_surf = self.small_font.render(instruction, True, DARK_GRAY)
                    # Ensure instructions fit within the panel
                    y_pos = instruction_y_start + i * 20  # Slightly increased spacing
                    if y_pos + inst_surf.get_height() < 600:  # Check if it fits within panel
                        self.screen.blit(inst_surf, (42, y_pos))  # Slight indent from box edge

    def draw_button(self, text, rect, color=GRAY):
        # Add a slight shadow effect with rounded corners
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        pygame.draw.rect(self.screen, (150, 150, 150), shadow_rect, border_radius=8)
        
        # Draw the main button with rounded corners
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)
        
        # Center the text
        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)