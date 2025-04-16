import pandas as pd
import json

with open("container_info.json", "r") as file:
    container_info = json.load(file)

CONTAINER_CAPACITY: float = container_info["Container payload"]
CONTAINER_COUNT: int = container_info["Number of containers"]

df = pd.read_csv("blocks.csv")

# Create a list of tuples: (BlockNo, Weight)
blocks = list(df[['BlockNo', 'Weight']].itertuples(index=False, name=None))

def find_best_subset(blocks, capacity):
    """
    Given a list of blocks (as tuples: (BlockNo, Weight)) and a capacity,
    find the subset of blocks that gives the maximum total weight without exceeding capacity.
    Returns (best_subset, best_weight).
    """
    best_subset = []
    best_weight = 0.0

    def search(start, current_subset, current_weight):
        nonlocal best_subset, best_weight
        # If current weight is over capacity, prune
        if current_weight > capacity:
            return
        # Check if the current combination is better than what we had
        if current_weight > best_weight:
            best_weight = current_weight
            best_subset = current_subset.copy()
        # Explore the remaining blocks
        for i in range(start, len(blocks)):
            block = blocks[i]
            current_subset.append(block)
            search(i + 1, current_subset, current_weight + block[1])
            current_subset.pop()

    search(0, [], 0)
    return best_subset, best_weight

# List to hold container assignments:
container_assignments = {}

# Work on a copy of the blocks list
remaining_blocks = blocks.copy()

for container in range(1, CONTAINER_COUNT + 1):
    # break early if no blocks remaining
    if not remaining_blocks:
        break

    best_combo, total_weight = find_best_subset(remaining_blocks, CONTAINER_CAPACITY)
    
    # Save the container assignment using block numbers.
    container_assignments[container] = {
        "blocks": [block[0] for block in best_combo],
        "total_weight": total_weight,
    }
    
    # Remove the selected blocks from the pool of remaining blocks.
    for block in best_combo:
        remaining_blocks.remove(block)

# Print out the container assignments
for container, assignment in container_assignments.items():
    blocks_str = ", ".join(str(b) for b in assignment["blocks"])
    print(f"Container {container}: blocks {blocks_str} (Total Weight of container: {assignment['total_weight']})")


