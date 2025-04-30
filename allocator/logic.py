from typing import List, Tuple, Dict, Union
import pandas as pd
import time

# Type alias for clarity
dBlock = Tuple[int, float]
ContainerMap = Dict[int, Dict[str, Union[List[int], float]]]


def load_blocks(path: str) -> List[dBlock]:
    """Load CSV and return list of (BlockNo, Weight).
    Ensures the required columns exist and handles potential errors."""
    try:
        df = pd.read_csv(path)
        
        # Verify required columns exist
        required_cols = ['BlockNo', 'Weight']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in CSV file")
        
        # Check for invalid values
        if df['BlockNo'].isna().any():
            raise ValueError("CSV contains empty BlockNo values")
        if df['Weight'].isna().any():
            raise ValueError("CSV contains empty Weight values")
        
        return list(df[['BlockNo', 'Weight']].itertuples(index=False, name=None))
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {str(e)}")


def find_best_subset_dp(blocks: List[dBlock], capacity: float, max_blocks: int = None) -> Tuple[List[dBlock], float]:
    """Find the best subset of blocks using dynamic programming.
    More efficient than recursion while still finding optimal solution."""
    n = len(blocks)
    
    # Handle edge cases
    if n == 0 or capacity <= 0:
        return [], 0.0
    
    # If max_blocks is None or greater than total blocks, use full capacity
    max_blocks_to_use = min(n, max_blocks) if max_blocks is not None else n
    
    # Create arrays for our dynamic programming approach
    # dp[i][j][k] = best weight for first i blocks, capacity j, using k blocks
    dp = {}
    chosen = {}
    
    # Initialize
    for i in range(n+1):
        dp[i] = {}
        chosen[i] = {}
        for j in range(int(capacity*100) + 1):  # Scale to handle floating point
            dp[i][j] = {}
            chosen[i][j] = {}
            for k in range(max_blocks_to_use + 1):
                dp[i][j][k] = 0.0
                chosen[i][j][k] = False
    
    # Fill the dp table
    for i in range(1, n+1):
        block_no, weight = blocks[i-1]
        weight_scaled = int(weight * 100)  # Scale to handle floating point
        
        for j in range(int(capacity*100) + 1):
            for k in range(1, max_blocks_to_use + 1):
                # Don't include this block
                dp[i][j][k] = dp[i-1][j][k]
                
                # Include this block if it fits
                if j >= weight_scaled:
                    with_block = dp[i-1][j-weight_scaled][k-1] + weight
                    if with_block > dp[i][j][k]:
                        dp[i][j][k] = with_block
                        chosen[i][j][k] = True
    
    # Reconstruct the solution
    result = []
    j = int(capacity * 100)
    k = max_blocks_to_use
    
    # Find the best k (number of blocks to use)
    best_k = 0
    best_value = 0.0
    for potential_k in range(max_blocks_to_use + 1):
        if dp[n][j][potential_k] > best_value:
            best_value = dp[n][j][potential_k]
            best_k = potential_k
    
    k = best_k
    
    for i in range(n, 0, -1):
        if chosen[i][j][k]:
            block_no, weight = blocks[i-1]
            result.append(blocks[i-1])
            j -= int(weight * 100)
            k -= 1
    
    total_weight = sum(block[1] for block in result)
    return result, total_weight


def find_best_subset_greedy(blocks: List[dBlock], capacity: float, max_blocks: int = None) -> Tuple[List[dBlock], float]:
    """Find a good subset of blocks using a greedy approach.
    This is more efficient but may not find the optimal solution."""
    # Sort blocks by weight/mass ratio in descending order for better greedy results
    sorted_blocks = sorted(blocks, key=lambda x: x[1], reverse=True)
    
    selected_blocks = []
    total_weight = 0.0
    
    # Try to find a good solution
    for block in sorted_blocks:
        # If adding this block doesn't exceed capacity
        if total_weight + block[1] <= capacity:
            # And doesn't exceed max_blocks (if specified)
            if max_blocks is None or len(selected_blocks) < max_blocks:
                selected_blocks.append(block)
                total_weight += block[1]
    
    return selected_blocks, total_weight


def find_best_subset(blocks: List[dBlock], capacity: float, max_blocks: int = None) -> Tuple[List[dBlock], float]:
    """Find the best subset of blocks that fits within capacity and max_blocks constraint.
    Selects the appropriate algorithm based on input size and constraints."""
    # Handle edge cases
    if not blocks or capacity <= 0:
        return [], 0.0
    
    # Set max_blocks to total blocks if not specified
    if max_blocks is None:
        max_blocks = len(blocks)
    
    # For small datasets, use dynamic programming for optimal solution
    if len(blocks) <= 20:
        start_time = time.time()
        result = find_best_subset_dp(blocks, capacity, max_blocks)
        elapsed = time.time() - start_time
        
        # If DP takes too long, fallback to greedy
        if elapsed > 1.0:  # More than 1 second
            return find_best_subset_greedy(blocks, capacity, max_blocks)
        return result
    
    # For larger datasets, use greedy approach
    return find_best_subset_greedy(blocks, capacity, max_blocks)


def assign_containers(blocks: List[dBlock], capacity: float, count: int, max_blocks: int = None) -> ContainerMap:
    """Pack blocks into `count` containers with optional max blocks per container limit."""
    # Input validation
    if capacity <= 0:
        raise ValueError("Container capacity must be greater than 0")
    if count <= 0:
        raise ValueError("Number of containers must be greater than 0")
    
    # Make a copy to avoid modifying the original
    remaining = blocks.copy()
    assignments: ContainerMap = {}
    
    # Track running time to prevent excessive computation
    start_time = time.time()
    timeout = 10.0  # 10 seconds max for the entire allocation
    
    for cid in range(1, count + 1):
        # Check timeout to prevent hanging
        if time.time() - start_time > timeout:
            # If we're timing out, process remaining containers with greedy approach
            while remaining and cid <= count:
                greedy_combo, greedy_total = find_best_subset_greedy(
                    remaining[:min(20, len(remaining))], capacity, max_blocks
                )
                if not greedy_combo:
                    break
                    
                assignments[cid] = {
                    'blocks': [b[0] for b in greedy_combo],
                    'total_weight': greedy_total
                }
                for b in greedy_combo:
                    remaining.remove(b)
                cid += 1
            break
            
        if not remaining:
            break
            
        combo, total = find_best_subset(remaining, capacity, max_blocks)
        
        assignments[cid] = {
            'blocks': [b[0] for b in combo],
            'total_weight': total
        }
        
        for b in combo:
            remaining.remove(b)
    
    return assignments