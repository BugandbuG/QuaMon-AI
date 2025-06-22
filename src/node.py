class Node:
    """
    A node in the search tree.
    """
    def __init__(self, state, parent=None, action=None, path_cost=0):
        """
        Initializes a Node object.

        Args:
            state (State): The state represented by this node.
            parent (Node): The parent node.
            action (tuple): The action that led to this state.
            path_cost (int): The cost of the path to this node.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    def __repr__(self):
        return f"<Node {self.state}>"

    def __lt__(self, other):
        # For priority queue in UCS and A*
        return self.path_cost < other.path_cost 