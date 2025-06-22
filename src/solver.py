from collections import deque
from node import Node
from state import State
import heapq

class Solver:
    def __init__(self, board, initial_state):
        self.board = board
        self.initial_state = initial_state

    def solve(self):
        raise NotImplementedError

    def _reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return path[::-1]

class BfsSolver(Solver):
    def solve(self):
        """
        Solves the Rush Hour puzzle using Breadth-First Search.
        """
        initial_node = Node(self.initial_state)
        
        if initial_node.state.is_goal_state(self.board):
            return self._reconstruct_path(initial_node)

        frontier = deque([initial_node])
        explored = {initial_node.state}

        while frontier:
            current_node = frontier.popleft()

            for successor_state in current_node.state.get_successors(self.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    
                    if successor_node.state.is_goal_state(self.board):
                        return self._reconstruct_path(successor_node)
                    
                    frontier.append(successor_node)
                    explored.add(successor_state)
        
        return None # No solution found

class DfsSolver(Solver):
    def solve(self):
        """
        Solves the Rush Hour puzzle using Depth-First Search.
        """
        initial_node = Node(self.initial_state)
        
        if initial_node.state.is_goal_state(self.board):
            return self._reconstruct_path(initial_node)

        frontier = [initial_node] # Stack for DFS
        explored = {initial_node.state}

        while frontier:
            current_node = frontier.pop() # LIFO

            for successor_state in current_node.state.get_successors(self.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    
                    if successor_node.state.is_goal_state(self.board):
                        return self._reconstruct_path(successor_node)
                    
                    frontier.append(successor_node)
                    explored.add(successor_state)
        
        return None # No solution found

class UcsSolver(Solver):
    def solve(self):
        """
        Solves the Rush Hour puzzle using Uniform-Cost Search.
        """
        initial_node = Node(self.initial_state, path_cost=0)
        
        frontier = [initial_node] # Priority queue for UCS
        explored = {initial_node.state: 0}

        while frontier:
            current_node = heapq.heappop(frontier)

            if current_node.state.is_goal_state(self.board):
                return self._reconstruct_path(current_node)

            for successor_state in current_node.state.get_successors(self.board):
                moved_vehicle_id = None
                for vid, v in current_node.state.vehicles.items():
                    if v != successor_state.vehicles[vid]:
                        moved_vehicle_id = vid
                        break
                
                move_cost = successor_state.vehicles[moved_vehicle_id].length
                new_cost = current_node.path_cost + move_cost

                if successor_state not in explored or new_cost < explored[successor_state]:
                    explored[successor_state] = new_cost
                    successor_node = Node(state=successor_state, parent=current_node, path_cost=new_cost)
                    heapq.heappush(frontier, successor_node)
        
        return None # No solution found

class AStarSolver(Solver):
    def solve(self):
        """
        Solves the Rush Hour puzzle using A* Search.
        """
        initial_node = Node(self.initial_state, path_cost=0)
        
        # The frontier stores tuples of (priority, node)
        frontier = [(self._blocking_heuristic(initial_node.state), initial_node)]
        explored = {initial_node.state: 0}

        while frontier:
            _, current_node = heapq.heappop(frontier)

            if current_node.state.is_goal_state(self.board):
                return self._reconstruct_path(current_node)

            for successor_state in current_node.state.get_successors(self.board):
                moved_vehicle_id = None
                for vid, v in current_node.state.vehicles.items():
                    if v != successor_state.vehicles[vid]:
                        moved_vehicle_id = vid
                        break
                
                move_cost = successor_state.vehicles[moved_vehicle_id].length
                new_cost = current_node.path_cost + move_cost

                if successor_state not in explored or new_cost < explored[successor_state]:
                    explored[successor_state] = new_cost
                    heuristic_cost = self._blocking_heuristic(successor_state)
                    priority = new_cost + heuristic_cost
                    successor_node = Node(state=successor_state, parent=current_node, path_cost=new_cost)
                    heapq.heappush(frontier, (priority, successor_node))
        
        return None # No solution found

    def _blocking_heuristic(self, state):
        """
        Calculates the blocking heuristic for a given state.
        The heuristic is the number of cars directly between the red car and the exit.
        """
        red_car = state.vehicles['X']
        grid = state._create_grid(self.board)
        blocking_cars = set()

        for i in range(red_car.x + red_car.length, self.board.width):
            if grid[red_car.y][i] != '.':
                blocking_cars.add(grid[red_car.y][i])
        
        return len(blocking_cars) 