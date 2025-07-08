import sys
import os
import time
import tracemalloc
from pathlib import Path
import psutil
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from board import Board
from state import State
from solver import BfsSolver, DfsSolver, UcsSolver, AStarSolver
from node import Node

class PerformanceMetrics:
    def __init__(self):
        self.search_time = 0.0
        self.memory_usage = 0.0      # in MB
        self.memory_peak = 0.0       # in MB (if available)
        self.nodes_expanded = 0
        self.solution_length = 0
        self.solution_found = False

    def __str__(self):
        return (f"Time: {self.search_time:.4f}s, "
                f"Memory: {self.memory_usage:.2f}MB, "
                f"Peak Memory: {self.memory_peak:.2f}MB, "
                f"Nodes Expanded: {self.nodes_expanded}, "
                f"Solution Length: {self.solution_length}, "
                f"Solution Found: {self.solution_found}")


class InstrumentedSolver:
    def __init__(self, solver_class):
        self.solver_class = solver_class
        self.metrics = PerformanceMetrics()

    def solve_with_metrics(self, board, initial_state):
        self.metrics = PerformanceMetrics()

        if tracemalloc.is_tracing():
            tracemalloc.stop()
        tracemalloc.start()

        solver = self.solver_class(board, initial_state)

        self._patch_solver_for_counting(solver)

        start_time = time.perf_counter()

        try:
            solution = solver.solve()
        except Exception as e:
            solution = None
            print(f"Error during search: {e}")
        finally:
            end_time = time.perf_counter()
            self.metrics.search_time = end_time - start_time
            self._record_memory_metrics()
            self.metrics.nodes_expanded = getattr(solver, '_nodes_expanded', 0)
            self.metrics.solution_found = solution is not None

            if solution and hasattr(solution, '__len__'):
                self.metrics.solution_length = len(solution) - 1 

        return solution

    def _record_memory_metrics(self):
        if tracemalloc.is_tracing():
            current, peak = tracemalloc.get_traced_memory()
            self.metrics.memory_usage = current / 1024 / 1024
            self.metrics.memory_peak = peak / 1024 / 1024
            tracemalloc.stop()

        process = psutil.Process(os.getpid())
        self.metrics.memory_usage = max(self.metrics.memory_usage, process.memory_info().rss / 1024 / 1024)
    
    def _patch_solver_for_counting(self, solver):
        solver._nodes_expanded = 0
        original_solve = solver.solve
        
        def counting_solve():
            if isinstance(solver, BfsSolver):
                return self._count_bfs_nodes(solver)
            elif isinstance(solver, DfsSolver):
                return self._count_dfs_nodes(solver)
            elif isinstance(solver, UcsSolver):
                return self._count_ucs_nodes(solver)
            elif isinstance(solver, AStarSolver):
                return self._count_astar_nodes(solver)
            else:
                return original_solve()
        
        solver.solve = counting_solve
    
    def _count_bfs_nodes(self, solver):
        from collections import deque
        
        initial_node = Node(solver.initial_state)
        
        if initial_node.state.is_goal_state(solver.board):
            return solver._reconstruct_path(initial_node)

        frontier = deque([initial_node])
        explored = {initial_node.state}

        while frontier:
            current_node = frontier.popleft()
            solver._nodes_expanded += 1  

            for successor_state in current_node.state.get_successors(solver.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    
                    if successor_node.state.is_goal_state(solver.board):
                        return solver._reconstruct_path(successor_node)
                    
                    frontier.append(successor_node)
                    explored.add(successor_state)
        
        return None
    
    def _count_dfs_nodes(self, solver):
        initial_node = Node(solver.initial_state)
        
        if initial_node.state.is_goal_state(solver.board):
            return solver._reconstruct_path(initial_node)

        frontier = [initial_node] 
        explored = {initial_node.state}

        while frontier:
            current_node = frontier.pop()  
            solver._nodes_expanded += 1 

            for successor_state in current_node.state.get_successors(solver.board):
                if successor_state not in explored:
                    successor_node = Node(state=successor_state, parent=current_node)
                    
                    if successor_node.state.is_goal_state(solver.board):
                        return solver._reconstruct_path(successor_node)
                    
                    frontier.append(successor_node)
                    explored.add(successor_state)
        
        return None
    
    def _count_ucs_nodes(self, solver):
        import heapq
        
        initial_node = Node(solver.initial_state, path_cost=0)
        
        frontier = [initial_node]
        explored = {initial_node.state: 0}

        while frontier:
            current_node = heapq.heappop(frontier)
            solver._nodes_expanded += 1

            if current_node.state.is_goal_state(solver.board):
                return solver._reconstruct_path(current_node)

            for successor_state in current_node.state.get_successors(solver.board):
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
        
        return None
    
    def _count_astar_nodes(self, solver):
        import heapq
        
        initial_node = Node(solver.initial_state, path_cost=0)
        
        frontier = [(solver._blocking_heuristic(initial_node.state), initial_node)]
        explored = {initial_node.state: 0}

        while frontier:
            _, current_node = heapq.heappop(frontier)
            solver._nodes_expanded += 1

            if current_node.state.is_goal_state(solver.board):
                return solver._reconstruct_path(current_node)

            for successor_state in current_node.state.get_successors(solver.board):
                moved_vehicle_id = None
                for vid, v in current_node.state.vehicles.items():
                    if v != successor_state.vehicles[vid]:
                        moved_vehicle_id = vid
                        break
                
                move_cost = successor_state.vehicles[moved_vehicle_id].length
                new_cost = current_node.path_cost + move_cost

                if successor_state not in explored or new_cost < explored[successor_state]:
                    explored[successor_state] = new_cost
                    heuristic_cost = solver._blocking_heuristic(successor_state)
                    priority = new_cost + heuristic_cost
                    successor_node = Node(state=successor_state, parent=current_node, path_cost=new_cost)
                    heapq.heappush(frontier, (priority, successor_node))
        
        return None

def evaluate_board(board_file, algorithms, timeout=60, num_runs=100):
    print(f"\n{'='*60}")
    print(f"Evaluating: {os.path.basename(board_file)} (Running {num_runs} times)")
    print(f"{'='*60}")
    
    try:
        board = Board(board_file)
        initial_state = State(board.vehicles)
        
        results = {}
        
        for name, solver_class in algorithms.items():
            print(f"\n{name}:")
            print("-" * 40)
            
            # Lists to store metrics from all runs
            all_times = []
            all_memories = []
            all_nodes = []
            all_solution_lengths = []
            solutions_found = 0
            
            # Run multiple times
            for run in range(num_runs):
                if run % 10 == 0:  # Progress indicator
                    print(f"  Run {run+1}/{num_runs}...")
                
                instrumented = InstrumentedSolver(solver_class)
                
                try:
                    solution = instrumented.solve_with_metrics(board, initial_state)
                    
                    # Collect metrics
                    all_times.append(instrumented.metrics.search_time)
                    all_memories.append(instrumented.metrics.memory_usage)
                    all_nodes.append(instrumented.metrics.nodes_expanded)
                    
                    if solution:
                        solutions_found += 1
                        all_solution_lengths.append(len(solution) - 1)
                    else:
                        all_solution_lengths.append(0)
                        
                except KeyboardInterrupt:
                    print(f"  Timeout exceeded ({timeout}s)")
                    break
                except Exception as e:
                    print(f"  Error in run {run+1}: {e}")
                    continue
            
            # Calculate averages
            if all_times:
                avg_metrics = PerformanceMetrics()
                avg_metrics.search_time = sum(all_times) / len(all_times)
                avg_metrics.memory_usage = sum(all_memories) / len(all_memories)
                avg_metrics.nodes_expanded = int(sum(all_nodes) / len(all_nodes))
                avg_metrics.solution_length = int(sum(all_solution_lengths) / len(all_solution_lengths))
                avg_metrics.solution_found = solutions_found > 0
                
                results[name] = avg_metrics
                print(f"  Average over {len(all_times)} runs: {avg_metrics}")
                print(f"  Success rate: {solutions_found}/{len(all_times)} ({100*solutions_found/len(all_times):.1f}%)")
            else:
                results[name] = PerformanceMetrics()
                results[name].search_time = timeout
                
        return results
        
    except Exception as e:
        print(f"Error loading board {board_file}: {e}")
        return {}

def create_summary_table(all_results):
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    
    header = f"{'Board':<15} {'Algorithm':<10} {'Time(s)':<8} {'Memory(MB)':<12} {'Nodes':<8} {'Sol.Len':<8} {'Found':<6}"
    print(header)
    print("-" * 80)
    
    for board_name, board_results in all_results.items():
        for i, (algorithm, metrics) in enumerate(board_results.items()):
            board_display = board_name if i == 0 else ""
            found_display = "Yes" if metrics.solution_found else "No"
            
            row = f"{board_display:<15} {algorithm:<10} {metrics.search_time:<8.3f} {metrics.memory_usage:<12.2f} {metrics.nodes_expanded:<8} {metrics.solution_length:<8} {found_display:<6}"
            print(row)
        
        if board_results: 
            print()

def save_results_to_csv(all_results, num_runs=100):
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    csv_filename = results_dir / f"evaluation_results.csv"
    
    csv_data = []
    
    headers = [
        'Board', 'Algorithm', 'Avg_Time_s', 'Avg_Memory_MB', 'Avg_Nodes_Expanded', 
        'Avg_Solution_Length', 'Solution_Found', 'Num_Runs'
    ]
    
    for board_name, board_results in all_results.items():
        for algorithm, metrics in board_results.items():
            row = [
                board_name,
                algorithm,
                f"{metrics.search_time:.6f}",
                f"{metrics.memory_usage:.2f}",
                metrics.nodes_expanded,
                metrics.solution_length,
                "Yes" if metrics.solution_found else "No",
                num_runs
            ]
            csv_data.append(row)
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(csv_data)
        
        print(f"\nResults saved to: {csv_filename}")
        
    except Exception as e:
        print(f"Error saving results to CSV: {e}")

def main():
    print("Rush Hour Search Algorithm Performance Evaluation")
    print("=" * 60)
    
    algorithms = {
        'BFS': BfsSolver,
        'DFS': DfsSolver,
        'UCS': UcsSolver,
        'A*': AStarSolver
    }
    
    boards_dir = Path("test_map")
    if not boards_dir.exists():
        print(f"Error: Boards directory '{boards_dir}' not found!")
        return
    
    board_files = list(boards_dir.glob("*.txt"))
    if not board_files:
        print(f"Error: No board files found in '{boards_dir}'!")
        return
    
    board_files.sort()
    
    print(f"Found {len(board_files)} board files to evaluate")
    print(f"Testing algorithms: {', '.join(algorithms.keys())}")
    print("Each algorithm will be run 100 times per board for average metrics")
    
    all_results = {}
    
    for board_file in board_files:
        board_name = board_file.stem
        results = evaluate_board(str(board_file), algorithms, num_runs=100)
        if results:
            all_results[board_name] = results
    
    if all_results:
        create_summary_table(all_results)
        save_results_to_csv(all_results, num_runs=100)
    else:
        print("No results to display.")

if __name__ == "__main__":
    main()
