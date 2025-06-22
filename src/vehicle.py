class Vehicle:
    """
    A class to represent a vehicle on the Rush Hour board.
    """
    def __init__(self, id, orientation, x, y, length):
        """
        Initializes a Vehicle object.

        Args:
            id (str): The character representing the vehicle on the board.
            orientation (str): 'h' for horizontal, 'v' for vertical.
            x (int): The column of the vehicle's top-left corner.
            y (int): The row of the vehicle's top-left corner.
            length (int): The length of the vehicle.
        """
        self.id = id
        self.orientation = orientation
        self.x = x
        self.y = y
        self.length = length

    def __repr__(self):
        return f"Vehicle({self.id}, {self.orientation}, ({self.x}, {self.y}), {self.length})"

    def __eq__(self, other):
        return self.id == other.id and self.orientation == other.orientation and \
               self.x == other.x and self.y == other.y and self.length == other.length

    def __hash__(self):
        return hash((self.id, self.orientation, self.x, self.y, self.length))

    def occupies(self, x, y):
        """
        Checks if the vehicle occupies a given coordinate.
        """
        if self.orientation == 'h':
            return self.y == y and self.x <= x < self.x + self.length
        else: # 'v'
            return self.x == x and self.y <= y < self.y + self.length 