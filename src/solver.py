from collections import deque
from node import Node
from state import State
import heapq
import time
import tracemalloc
import gc
import psutil
import os

class Solver:
    def __init__(self, board, initial_state):
        self.board = board
        self.initial_state = initial_state
        self.nodes_explored = 0
        self.total_nodes = 0

    def solve(self):
        raise NotImplementedError

    def solve_with_metrics(self):
        """Solve with performance metrics tracking"""
        # Force garbage collection before measurement
        gc.collect()
        
        # Get initial memory baseline
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Start memory tracking
        tracemalloc.start()
        
        # Reset counters
        self.nodes_explored = 0
        self.total_nodes = 0
        
        # Start timing (use time.perf_counter for higher precision)
        start_time = time.perf_counter()
        
        # Solve the puzzle
        solution = self.solve()
        
        # Stop timing immediately
        end_time = time.perf_counter()
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = max(peak / 1024 / 1024, final_memory - initial_memory)
        
        # Calculate metrics
        solve_time = end_time - start_time
        
        # Calculate total cost based on algorithm type
        total_cost = self._calculate_total_cost(solution) if solution else 0
        
        # Prepare results
        metrics = {
            'time': solve_time,
            'memory_mb': memory_used,
            'nodes_explored': self.nodes_explored,
            'total_nodes': self.total_nodes,
            'solution_length': len(solution) if solution else 0,
            'total_cost': total_cost
        }
        
        return solution, metrics

    def _calculate_total_cost(self, solution):
        """Calculate total cost based on algorithm type"""
        if not solution or len(solution) <= 1:
            return 0
        
        # Default implementation for BFS/DFS: 1 move = 1 cost
        return len(solution) - 1

    def _reconstruct_path(self, node):
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return path[::-1]

    def solve_with_multiple_runs(self, num_runs=3):
        """Run solver multiple times and return average metrics"""
        results = []
        best_solution = None
        
        for run in range(num_runs):
            solution, metrics = self.solve_with_metrics()
            if solution:
                results.append(metrics)
                if best_solution is None:
                    best_solution = solution
            
            # Clean up between runs
            gc.collect()
        
        if not results:
            return None, None
        
        # Calculate average metrics
        avg_time = sum(r['time'] for r in results) / len(results)
        avg_memory = sum(r['memory_mb'] for r in results) / len(results)
        
        # Calculate standard deviations
        time_std = 0
        memory_std = 0
        if len(results) > 1:
            time_std = (sum((r['time'] - avg_time)**2 for r in results) / len(results))**0.5
            memory_std = (sum((r['memory_mb'] - avg_memory)**2 for r in results) / len(results))**0.5
        
        avg_metrics = {
            'time': avg_time,
            'memory_mb': avg_memory,
            'nodes_explored': results[0]['nodes_explored'],  # Should be consistent
            'total_nodes': results[0]['total_nodes'],        # Should be consistent
            'solution_length': results[0]['solution_length'], # Should be consistent
            'total_cost': results[0]['total_cost'],          # Should be consistent
            'runs': len(results),
            'time_std': time_std,
            'memory_std': memory_std
        }
        
        return best_solution, avg_metrics

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
        self.total_nodes = 1

        while frontier:
            current_node = frontier.popleft()
            self.nodes_explored += 1

            for successor_state in current_node.state.get_successors(self.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    self.total_nodes += 1
                    
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
        self.total_nodes = 1

        while frontier:
            current_node = frontier.pop() # LIFO
            self.nodes_explored += 1

            for successor_state in current_node.state.get_successors(self.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    self.total_nodes += 1
                    
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
        self.total_nodes = 1

        while frontier:
            current_node = heapq.heappop(frontier)
            self.nodes_explored += 1

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
                    self.total_nodes += 1
                    heapq.heappush(frontier, successor_node)
        
        return None # No solution found

    def _calculate_total_cost(self, solution):
        """Calculate total cost for UCS: sum of vehicle lengths for each move"""
        if not solution or len(solution) <= 1:
            return 0
        
        total_cost = 0
        for i in range(1, len(solution)):
            prev_state = solution[i-1]
            curr_state = solution[i]
            
            # Find which vehicle moved
            for vid, vehicle in curr_state.vehicles.items():
                if vehicle != prev_state.vehicles[vid]:
                    total_cost += vehicle.length
                    break
        
        return total_cost

class AStarSolver(Solver):
    def solve(self):
        """
        Solves the Rush Hour puzzle using A* Search.
        """
        initial_node = Node(self.initial_state, path_cost=0)
        
        # The frontier stores tuples of (priority, node)
        frontier = [(self._blocking_heuristic(initial_node.state), initial_node)]
        explored = {initial_node.state: 0}
        self.total_nodes = 1

        while frontier:
            _, current_node = heapq.heappop(frontier)
            self.nodes_explored += 1

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
                    self.total_nodes += 1
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

    def _calculate_total_cost(self, solution):
        """Calculate total cost for A*: sum of vehicle lengths for each move"""
        if not solution or len(solution) <= 1:
            return 0
        
        total_cost = 0
        for i in range(1, len(solution)):
            prev_state = solution[i-1]
            curr_state = solution[i]
            
            # Find which vehicle moved
            for vid, vehicle in curr_state.vehicles.items():
                if vehicle != prev_state.vehicles[vid]:
                    total_cost += vehicle.length
                    break
        
        return total_cost