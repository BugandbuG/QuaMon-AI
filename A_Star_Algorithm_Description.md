# A* Algorithm in Rush Hour Solver

## Detailed Description of A* Algorithm

| **Information** | **Details** |
|-----------------|-------------|
| **Algorithm Name** | A* Search (A-Star Search) |
| **Algorithm Type** | Informed Search Algorithm |
| **Time Complexity** | O(b^d) in worst case, but usually much more efficient |
| **Space Complexity** | O(b^d) |

## 1. Input

| **Parameter** | **Data Type** | **Description** |
|---------------|---------------|-----------------|
| `board` | `Board` object | Rush Hour game board containing grid size and goal position information |
| `initial_state` | `State` object | Initial state of the puzzle, containing positions of all vehicles |

### Input Details:
- **Board**: Contains information about:
  - Grid dimensions (width x height)
  - Goal position (goal_pos) that the red car needs to reach
  - Movement space constraints

- **Initial State**: Contains:
  - Dictionary of all vehicles with IDs and position information
  - Red car (ID = 'X') is the target vehicle to reach the goal

## 2. Output

| **Result** | **Data Type** | **Description** |
|------------|---------------|-----------------|
| **Success** | `List[State]` | List of states from initial state to goal state |
| **Failure** | `None` | No solution found |

### Output Details:
- **List[State]**: Each State in the list represents one move step
  - State[0]: Initial state
  - State[1], State[2], ...: Intermediate move steps
  - State[n-1]: Goal state (red car has escaped)

## 3. Detailed Algorithm Operation

### 3.1 Initialization

```python
initial_node = Node(self.initial_state, path_cost=0)
frontier = [(self._blocking_heuristic(initial_node.state), initial_node)]
explored = {initial_node.state: 0}
```

| **Component** | **Description** |
|---------------|-----------------|
| `initial_node` | First node with initial state and cost = 0 |
| `frontier` | Priority queue containing unexplored nodes, sorted by f(n) = g(n) + h(n) |
| `explored` | Dictionary storing explored states and their best costs |

### 3.2 Main Loop

| **Step** | **Action** | **Details** |
|----------|------------|-------------|
| **1** | Get node with lowest priority | `current_node = heapq.heappop(frontier)` |
| **2** | Check termination condition | If red car reached goal position → return path |
| **3** | Generate successor states | All valid moves from current state |
| **4** | Calculate cost | `g(n) = path_cost + move_cost` |
| **5** | Calculate heuristic | `h(n) = blocking_heuristic(state)` |
| **6** | Calculate priority | `f(n) = g(n) + h(n)` |
| **7** | Update frontier and explored | Add new node if unexplored or has better cost |

### 3.3 Heuristic Function (Blocking Heuristic)

```python
def _blocking_heuristic(self, state):
    red_car = state.vehicles['X']
    grid = state._create_grid(self.board)
    blocking_cars = set()
    
    for i in range(red_car.x + red_car.length, self.board.width):
        if grid[red_car.y][i] != '.':
            blocking_cars.add(grid[red_car.y][i])
    
    return len(blocking_cars)
```

| **Component** | **Description** |
|---------------|-----------------|
| **Purpose** | Estimate minimum steps needed for red car to escape |
| **Calculation** | Count distinct vehicles blocking red car's path to exit |
| **Properties** | Admissible (never overestimates) and Consistent |
| **Range** | From 0 (no blocking cars) to n (n blocking cars) |

### 3.4 Cost Calculation

| **Cost Type** | **Formula** | **Meaning** |
|---------------|-------------|-------------|
| **g(n)** | `current_cost + vehicle.length` | Actual cost from initial state |
| **h(n)** | `blocking_heuristic(state)` | Estimated cost to goal |
| **f(n)** | `g(n) + h(n)` | Total estimated cost |

### 3.5 Termination Conditions

| **Condition** | **Action** |
|---------------|------------|
| **Goal found** | `return self._reconstruct_path(current_node)` |
| **Empty frontier** | `return None` (no solution exists) |

### 3.6 Path Reconstruction

```python
def _reconstruct_path(self, node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return path[::-1]
```

| **Step** | **Description** |
|----------|-----------------|
| **1** | Start from goal node |
| **2** | Follow parent pointers back to root node |
| **3** | Reverse list to get path from start to goal |

## 4. Operation Example

### Initial State:
```
+---+---+---+---+---+---+
| A | A |   |   |   |   |
+---+---+---+---+---+---+
| X | X | B | B |   |   |
+---+---+---+---+---+---+
|   |   | C |   |   |   |
+---+---+---+---+---+---+
```

### Calculation Steps:
1. **h(initial) = 2** (cars B and C block car X)
2. **g(initial) = 0** (initial cost)
3. **f(initial) = 0 + 2 = 2**

### After moving car A down:
```
+---+---+---+---+---+---+
|   |   |   |   |   |   |
+---+---+---+---+---+---+
| X | X | B | B |   |   |
+---+---+---+---+---+---+
| A | A | C |   |   |   |
+---+---+---+---+---+---+
```
- **h(new) = 2** (cars B and C still blocking)
- **g(new) = 2** (cost of moving car A with length 2)
- **f(new) = 2 + 2 = 4**

## 5. Advantages of A* in Rush Hour

| **Advantage** | **Description** |
|---------------|-----------------|
| **Optimal** | Always finds optimal solution if heuristic is admissible |
| **Efficient** | Good heuristic reduces number of nodes to explore |
| **Complete** | Always finds solution if one exists |
| **Intelligent** | Prioritizes exploring most promising paths |

## 6. Comparison with Other Algorithms

| **Algorithm** | **Optimal** | **Complete** | **Efficient** | **Memory** |
|---------------|-------------|--------------|---------------|------------|
| **BFS** | ✅ | ✅ | ❌ | High |
| **DFS** | ❌ | ❌ | ❌ | Low |
| **UCS** | ✅ | ✅ | ⚠️ | High |
| **A*** | ✅ | ✅ | ✅ | High |
