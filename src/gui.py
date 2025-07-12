import pygame
import os
from board import Board
from state import State
from solver import BfsSolver, DfsSolver, UcsSolver, AStarSolver

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 1050  # Increased width to accommodate better spacing
SCREEN_HEIGHT = 800  # Increased height to accommodate moved elements
# Grid dimensions
GRID_WIDTH = 450
GRID_HEIGHT = 450
CELL_SIZE = GRID_WIDTH // 6
GRID_X = 380  # Moved further right to accommodate wider control panel
GRID_Y = 100
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GRID_COLOR = (128, 128, 128)
DARK_GRAY = (100, 100, 100)
BUTTON_COLOR = (220, 220, 220)
# Vehicle Colors - a map of vehicle ID to color
VEHICLE_COLORS = {
    'X': (255, 0, 0),     # Red car (special)
    'A': (0, 255, 0),     # Bright Green
    'B': (0, 0, 255),     # Blue
    'C': (255, 255, 0),   # Yellow
    'D': (255, 0, 255),   # Magenta
    'E': (0, 255, 255),   # Cyan
    'F': (128, 0, 128),   # Purple
    'G': (255, 165, 0),   # Orange
    'H': (0, 128, 0),     # Dark Green
    'I': (128, 128, 0),   # Olive
    'J': (0, 128, 128),   # Teal
    'K': (128, 0, 0),     # Maroon
    'L': (255, 192, 203), # Pink
    'M': (255, 20, 147),  # Deep Pink
    'N': (75, 0, 130),    # Indigo
    'O': (255, 69, 0),    # Red Orange
    'P': (50, 205, 50),   # Lime Green
    'Q': (30, 144, 255),  # Dodger Blue
    'R': (255, 215, 0),   # Gold
    'S': (220, 20, 60),   # Crimson
    'T': (0, 191, 255),   # Deep Sky Blue
    'U': (148, 0, 211),   # Dark Violet
    'V': (255, 140, 0),   # Dark Orange
    'W': (46, 139, 87),   # Sea Green
    'Y': (199, 21, 133),  # Medium Violet Red
    'Z': (72, 61, 139)    # Dark Slate Blue
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
        # Load grass background image once
        try:
            self.grass_background = pygame.image.load(r"C:\Users\PC\Documents\GitHub\QuaMon-AI\grass.jpg")
            self.grass_background = pygame.transform.scale(self.grass_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error as e:
            print(f"Failed to load grass background: {e}")
            self.grass_background = None
        
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
        
        self._load_board(self.board_files[self.current_board_idx])
        self._create_buttons()

    def _create_buttons(self):
        """Create button rectangles."""
        self.buttons = {
            'prev_board': pygame.Rect(40, 125, 50, 40),  # Moved down from 105 to 125
            'next_board': pygame.Rect(100, 125, 50, 40),  # Moved down from 105 to 125
            'prev_solver': pygame.Rect(40, 195, 50, 40),  # Moved down from 175 to 195
            'next_solver': pygame.Rect(100, 195, 50, 40),  # Moved down from 175 to 195
            'solve': pygame.Rect(40, 275, 170, 50),  # Moved down from 255 to 275
            'play_pause': pygame.Rect(40, 335, 170, 50),  # Moved down from 315 to 335
            'reset': pygame.Rect(40, 395, 170, 50)  # Moved down from 375 to 395
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
        # Draw grass background image first
        if self.grass_background:
            self.screen.blit(self.grass_background, (0, 0))
        else:
            # Fallback to green background if image failed to load
            self.screen.fill((144, 238, 144))
        
        # Draw a subtle background for the control panel with rounded corners and transparency
        control_panel = pygame.Rect(20, 40, 300, 750)  # Increased height to accommodate solution info
        # Create semi-transparent surface for modern look
        panel_surface = pygame.Surface((300, 750), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 200), (0, 0, 300, 750), border_radius=15)
        self.screen.blit(panel_surface, (20, 40))
        pygame.draw.rect(self.screen, (255, 255, 255, 100), control_panel, 2, border_radius=15)

    def draw_grid(self):
        # Draw a background for the grid with rounded corners and transparency
        grid_bg = pygame.Rect(GRID_X - 10, GRID_Y - 10, GRID_WIDTH + 20, GRID_HEIGHT + 20)
        # Create semi-transparent surface for modern look
        grid_bg_surface = pygame.Surface((GRID_WIDTH + 20, GRID_HEIGHT + 20), pygame.SRCALPHA)
        pygame.draw.rect(grid_bg_surface, (255, 255, 255, 180), (0, 0, GRID_WIDTH + 20, GRID_HEIGHT + 20), border_radius=15)
        self.screen.blit(grid_bg_surface, (GRID_X - 10, GRID_Y - 10))
        pygame.draw.rect(self.screen, (255, 255, 255, 120), grid_bg, 3, border_radius=15)
        
        # Draw the main grid area with rounded corners
        pygame.draw.rect(self.screen, WHITE, (GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT), border_radius=10)
        
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
        solver_name = self.solvers[self.current_solver_idx]
        solver_map = {
            'BFS': BfsSolver,
            'DFS': DfsSolver,
            'UCS': UcsSolver,
            'A*': AStarSolver
        }
        solver_class = solver_map[solver_name]
        solver = solver_class(self.current_board, State(self.current_board.vehicles))
        
        # Simply solve the puzzle
        self.solution_path = solver.solve()
        
        if self.solution_path:
            self.is_animating = True
            self.animation_step = 0
            self.message = f"Solution found in {len(self.solution_path) - 1} moves."
        else:
            self.message = "No solution found!"

    def _calculate_solution_cost(self):
        """Calculate the total cost of the solution based on current solver."""
        if not self.solution_path or len(self.solution_path) <= 1:
            return 0
        
        solver_name = self.solvers[self.current_solver_idx]
        
        # For BFS and DFS: cost = number of moves
        if solver_name in ['BFS', 'DFS']:
            return len(self.solution_path) - 1
        
        # For UCS and A*: cost = sum of vehicle lengths for each move
        elif solver_name in ['UCS', 'A*']:
            total_cost = 0
            for i in range(1, len(self.solution_path)):
                prev_state = self.solution_path[i-1]
                curr_state = self.solution_path[i]
                
                # Find which vehicle moved
                for vid, vehicle in curr_state.vehicles.items():
                    if vehicle != prev_state.vehicles[vid]:
                        total_cost += vehicle.length
                        break
            return total_cost
        
        return 0

    def _calculate_current_cost(self):
        """Calculate the cost up to the current step in animation."""
        if not self.solution_path or len(self.solution_path) <= 1 or self.animation_step == 0:
            return 0
        
        solver_name = self.solvers[self.current_solver_idx]
        
        # For BFS and DFS: cost = number of moves taken so far
        if solver_name in ['BFS', 'DFS']:
            return self.animation_step
        
        # For UCS and A*: cost = sum of vehicle lengths for moves taken so far
        elif solver_name in ['UCS', 'A*']:
            current_cost = 0
            for i in range(1, min(self.animation_step + 1, len(self.solution_path))):
                prev_state = self.solution_path[i-1]
                curr_state = self.solution_path[i]
                
                # Find which vehicle moved
                for vid, vehicle in curr_state.vehicles.items():
                    if vehicle != prev_state.vehicles[vid]:
                        current_cost += vehicle.length
                        break
            return current_cost
        
        return 0

    def draw_ui(self):
        """Draws the user interface elements."""
        # Title
        title_text = self.title_font.render("Rush Hour Solver", True, BLACK)
        self.screen.blit(title_text, (40, 50))  # Moved down from 15 to 50
        
        # Board selection
        board_label = self.font.render("Board:", True, BLACK)
        self.screen.blit(board_label, (40, 95))  # Moved down from 75 to 95
        # Truncate filename if too long
        board_name = self.board_files[self.current_board_idx]
        display_name = board_name
        if len(board_name) > 20:
            display_name = board_name[:17] + "..."
        board_text = self.font.render(f"{display_name}", True, BLACK)
        board_text_rect = pygame.Rect(160, 130, board_text.get_width(), board_text.get_height())
        self.screen.blit(board_text, (160, 130))
        
        # Show full filename on hover
        if board_text_rect.collidepoint(self.mouse_pos) and len(board_name) > 15:
            tooltip_surf = self.small_font.render(board_name, True, BLACK)
            tooltip_rect = pygame.Rect(self.mouse_pos[0] + 10, self.mouse_pos[1] - 30, 
                                     tooltip_surf.get_width() + 10, tooltip_surf.get_height() + 6)
            # Create semi-transparent tooltip
            tooltip_bg_surface = pygame.Surface((tooltip_surf.get_width() + 10, tooltip_surf.get_height() + 6), pygame.SRCALPHA)
            pygame.draw.rect(tooltip_bg_surface, (255, 255, 200, 220), (0, 0, tooltip_surf.get_width() + 10, tooltip_surf.get_height() + 6), border_radius=8)
            self.screen.blit(tooltip_bg_surface, (tooltip_rect.x, tooltip_rect.y))
            pygame.draw.rect(self.screen, BLACK, tooltip_rect, 1, border_radius=8)
            self.screen.blit(tooltip_surf, (tooltip_rect.x + 5, tooltip_rect.y + 3))
        self.draw_button("<", self.buttons['prev_board'], BUTTON_COLOR)
        self.draw_button(">", self.buttons['next_board'], BUTTON_COLOR)
        
        # Solver selection
        solver_label = self.font.render("Solver:", True, BLACK)
        self.screen.blit(solver_label, (40, 165))  # Moved down from 145 to 165
        solver_text = self.font.render(f"{self.solvers[self.current_solver_idx]}", True, BLACK)
        self.screen.blit(solver_text, (160, 200))
        self.draw_button("<", self.buttons['prev_solver'], BUTTON_COLOR)
        self.draw_button(">", self.buttons['next_solver'], BUTTON_COLOR)

        # Add separator line with gradient effect
        pygame.draw.line(self.screen, (150, 150, 150), (40, 255), (220, 255), 2)

        # Solve button
        self.draw_button("Solve", self.buttons['solve'])
        # Play/Pause button
        play_pause_text = "Pause" if self.is_animating else "Play"
        self.draw_button(play_pause_text, self.buttons['play_pause'])
        # Reset button
        self.draw_button("Reset", self.buttons['reset'], BUTTON_COLOR)
        
        # Solution info display in control panel
        if self.solution_path:
            # Calculate costs
            current_cost = self._calculate_current_cost()
            total_cost = self._calculate_solution_cost()
            solver_name = self.solvers[self.current_solver_idx]
            
            # Display solution information
            info_y = 465  # Position below reset button
            info_bg = pygame.Rect(35, info_y - 5, 240, 120)  # Increased height for cost info
            pygame.draw.rect(self.screen, WHITE, info_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, info_bg, 1, border_radius=8)
            
            # Solution info title
            info_title = self.font.render("Solution Info:", True, BLACK)
            self.screen.blit(info_title, (42, info_y))
            
            # Current step during animation
            current_step_text = f"Step: {self.animation_step + 1}/{len(self.solution_path)}"
            current_step_surf = self.small_font.render(current_step_text, True, DARK_GRAY)
            self.screen.blit(current_step_surf, (42, info_y + 25))
            
            # Current cost during animation
            current_cost_text = f"Current Cost: {current_cost}"
            current_cost_surf = self.small_font.render(current_cost_text, True, DARK_GRAY)
            self.screen.blit(current_cost_surf, (42, info_y + 45))
            
            # Total cost
            total_cost_text = f"Total Cost: {total_cost}"
            total_cost_surf = self.small_font.render(total_cost_text, True, DARK_GRAY)
            self.screen.blit(total_cost_surf, (42, info_y + 65))
            
            # Cost calculation method
            cost_method = "1 move = 1 cost" if solver_name in ['BFS', 'DFS'] else "cost = vehicle length"
            cost_method_surf = self.small_font.render(f"({cost_method})", True, DARK_GRAY)
            self.screen.blit(cost_method_surf, (42, info_y + 85))
        
        # Step count and cost display
        if self.solution_path:
            # Calculate costs
            current_cost = self._calculate_current_cost()
            total_cost = self._calculate_solution_cost()
            
            # Step count
            step_text = f"Step: {self.animation_step + 1}/{len(self.solution_path)}"
            step_surf = self.font.render(step_text, True, BLACK)
            
            # Cost display
            cost_text = f"Cost: {current_cost}/{total_cost}"
            cost_surf = self.font.render(cost_text, True, BLACK)
            
            # Calculate background size to fit both texts
            max_width = max(step_surf.get_width(), cost_surf.get_width())
            step_bg = pygame.Rect(GRID_X - 5, GRID_Y - 70, max_width + 10, 60)
            pygame.draw.rect(self.screen, WHITE, step_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, step_bg, 1, border_radius=8)
            
            # Display step count
            self.screen.blit(step_surf, (GRID_X, GRID_Y - 65))
            # Display cost
            self.screen.blit(cost_surf, (GRID_X, GRID_Y - 40))
        
        # Message display
        if self.message:
            # Position message better and add background
            msg_y = 600 if self.solution_path else 465  # Move down if solution info is shown
            msg_bg = pygame.Rect(35, msg_y, 240, 50)
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
                    self.screen.blit(msg_surf1, (42, msg_y + 5))
                    self.screen.blit(msg_surf2, (42, msg_y + 25))
                else:
                    msg_surf = self.small_font.render(msg_text, True, BLACK)
                    self.screen.blit(msg_surf, (42, msg_y + 15))
            else:
                msg_surf = self.small_font.render(msg_text, True, BLACK)
                self.screen.blit(msg_surf, (42, msg_y + 15))
        
        # Instructions - only show when no solution is loaded
        if not self.solution_path and not self.message:
            # Add some spacing before instructions
            instruction_y_start = 470  # Moved down slightly
            
            # Draw a subtle background for instructions
            inst_bg = pygame.Rect(35, 465, 240, 200)  # Adjusted position
            pygame.draw.rect(self.screen, WHITE, inst_bg, border_radius=8)
            pygame.draw.rect(self.screen, GRID_COLOR, inst_bg, 1, border_radius=8)
            
            instructions = [
                "1. Select a board and solver",
                "2. Click 'Solve' to find solution", 
                "3. Click 'Play' to animate solution",
                "",
                "Available algorithms:",
                "• BFS - Breadth-First Search",
                "• DFS - Depth-First Search", 
                "• UCS - Uniform Cost Search",
                "• A* - A-Star Search"
            ]
            for i, instruction in enumerate(instructions):
                if instruction:  # Only render non-empty lines
                    inst_surf = self.small_font.render(instruction, True, DARK_GRAY)
                    # Ensure instructions fit within the panel
                    y_pos = instruction_y_start + i * 20  # Slightly increased spacing
                    if y_pos + inst_surf.get_height() < 800:  # Check if it fits within panel (460+165=625)
                        self.screen.blit(inst_surf, (42, y_pos))  # Slight indent from box edge

    def draw_button(self, text, rect, color=GRAY):
        # Add a subtle shadow effect with rounded corners
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (0, 0, rect.width, rect.height), border_radius=8)
        self.screen.blit(shadow_surface, (rect.x + 2, rect.y + 2))
        
        # Draw the main button with rounded corners and transparency
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (*color, 200), (0, 0, rect.width, rect.height), border_radius=8)
        self.screen.blit(button_surface, (rect.x, rect.y))
        pygame.draw.rect(self.screen, (255, 255, 255, 150), rect, 2, border_radius=8)
        
        # Center the text
        text_surf = self.font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect) 