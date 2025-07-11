import copy

class State:
    """
    Represents a state of the Rush Hour puzzle.
    """
    def __init__(self, vehicles):
        """
        Initializes a State object.
        Args:
            vehicles (dict): A dictionary of Vehicle objects, with vehicle ID as key.
        """
        self.vehicles = vehicles
        # Using a frozenset of items makes the state hashable
        self.hash = hash(frozenset(self.vehicles.items()))

    def __eq__(self, other):
        return self.hash == other.hash

    def __hash__(self):
        return self.hash

    def is_goal_state(self, board):
        """
        Checks if the current state is the goal state.
        The goal is reached if the red car 'X' is at the exit.
        """
        red_car = self.vehicles['X']
        # The goal is on the right edge, so red_car.x should be board.width - red_car.length
        # But let's check against the goal_pos in board
        return (red_car.x + red_car.length - 1) == board.goal_pos[0] and red_car.y == board.goal_pos[1]

    def get_successors(self, board):
        """
        Generates all possible successor states from the current state.
        """
        successors = []
        grid = self._create_grid(board)

        for vid, vehicle in self.vehicles.items():
            if vehicle.orientation == 'h':
                # Move right
                for i in range(1, board.width):
                    if vehicle.x + vehicle.length - 1 + i < board.width and grid[vehicle.y][vehicle.x + vehicle.length -1 + i] == '.':
                        new_vehicles = copy.deepcopy(self.vehicles)
                        new_vehicles[vid].x += 1
                        successors.append(State(new_vehicles))
                    else:
                        break
                # Move left
                for i in range(1, board.width):
                    if vehicle.x - i >= 0 and grid[vehicle.y][vehicle.x - i] == '.':
                        new_vehicles = copy.deepcopy(self.vehicles)
                        new_vehicles[vid].x -= 1
                        successors.append(State(new_vehicles))
                    else:
                        break
            else:  # 'v'
                # Move down
                for i in range(1, board.height):
                    if vehicle.y + vehicle.length - 1 + i < board.height and grid[vehicle.y + vehicle.length - 1 + i][vehicle.x] == '.':
                        new_vehicles = copy.deepcopy(self.vehicles)
                        new_vehicles[vid].y += 1
                        successors.append(State(new_vehicles))
                    else:
                        break
                # Move up
                for i in range(1, board.height):
                    if vehicle.y - i >= 0 and grid[vehicle.y - i][vehicle.x] == '.':
                        new_vehicles = copy.deepcopy(self.vehicles)
                        new_vehicles[vid].y -= 1
                        successors.append(State(new_vehicles))
                    else:
                        break
        return successors

    def _create_grid(self, board):
        grid = [['.' for _ in range(board.width)] for _ in range(board.height)]
        for vehicle in self.vehicles.values():
            for i in range(vehicle.length):
                if vehicle.orientation == 'h':
                    grid[vehicle.y][vehicle.x + i] = vehicle.id
                else:
                    grid[vehicle.y + i][vehicle.x] = vehicle.id
        return grid 