from vehicle import Vehicle

class Board:
    """
    A class to represent the Rush Hour board.
    """
    def __init__(self, board_file):
        """
        Initializes a Board object from a file.

        Args:
            board_file (str): The path to the board file.
        """
        self.width = 6
        self.height = 6
        self.vehicles = {}
        self.load_from_file(board_file)
        
        # Set goal position based on red car's row
        if 'X' in self.vehicles:
            red_car_y = self.vehicles['X'].y
            self.goal_pos = (self.width - 1, red_car_y)
        else:
            # Default or error
            self.goal_pos = (5, 2)

    def load_from_file(self, board_file):
        """
        Loads a board configuration from a file.
        """
        grid = []
        with open(board_file, 'r') as f:
            for line in f:
                line = line.rstrip('\n')
                padded_line = (line + '.' * self.width)[:self.width]
                grid.append(list(padded_line))

        vehicle_coords = {}
        for r, row in enumerate(grid):
            for c, char in enumerate(row):
                if char != '.':
                    if char not in vehicle_coords:
                        vehicle_coords[char] = []
                    vehicle_coords[char].append((c, r))

        for id, coords in vehicle_coords.items():
            coords.sort()
            x, y = coords[0]
            length = len(coords)
            orientation = 'h' if coords[0][1] == coords[-1][1] else 'v'
            self.vehicles[id] = Vehicle(id, orientation, x, y, length) 