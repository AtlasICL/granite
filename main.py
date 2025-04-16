from typing import List, Tuple, Dict, Union
import pandas as pd
import json

CONTAINER_INFO_FILENAME: str = "container_info.json"
BLOCKS_INFO_FILENAME: str = "blocks.csv"

def load_container_info(path: str) -> Tuple[float, int]:
    """
    Loads container capacity and container count from JSON file.
    """
    with open(path, "r") as f:
        data: dict = json.load(f)
    capacity: float = float(data["Container payload"])
    count: int = int(data["Number of containers"])
    return capacity, count


def load_blocks(path: str) -> List[Tuple[int, float]]:
    """
    Loads blocks from CSV file and returns a list of (BlockNo, Weight) tuples.
    """
    df = pd.read_csv(path)
    blocks: List[Tuple[int, float]] = list(df[['BlockNo', 'Weight']].itertuples(index=False, name=None))
    return blocks


def find_best_subset(blocks: List[Tuple[int, float]], capacity: float) -> Tuple[List[Tuple[int, float]], float]:
    """
    Finds the subset of blocks with maximum total weight without exceeding capacity.
    Returns (best_subset, best_weight).
    """
    best_subset: List[Tuple[int, float]] = []
    best_weight: float = 0.0

    def search(start: int, current_subset: List[Tuple[int, float]], current_weight: float) -> None:
        nonlocal best_subset, best_weight

        if current_weight > capacity:
            return

        if current_weight > best_weight:
            best_weight = current_weight
            best_subset = current_subset.copy()

        for i in range(start, len(blocks)):
            block = blocks[i]
            current_subset.append(block)
            search(i + 1, current_subset, current_weight + block[1])
            current_subset.pop()

    search(0, [], 0.0)
    return best_subset, best_weight


def assign_containers(blocks: List[Tuple[int, float]], capacity: float, count: int) -> Dict[int, Dict[str, Union[List[int], float]]]:
    """
    Assigns blocks to a given number of containers in sequence, each up to the specified capacity.
    Returns a mapping: container_id -> {blocks: [...], total_weight: ...}.
    """
    remaining: List[Tuple[int, float]] = blocks.copy()
    assignments: Dict[int, Dict[str, Union[List[int], float]]] = {}

    for container_id in range(1, count + 1):
        if not remaining:
            break

        best_combo, total_wt = find_best_subset(remaining, capacity)
        assignments[container_id] = {"blocks": [b[0] for b in best_combo], "total_weight": total_wt}
        for b in best_combo:
            remaining.remove(b)

    return assignments


def print_assignments(assignments: Dict[int, Dict[str, Union[List[int], float]]]) -> None:
    """
    Prints out container assignments and their weights.
    """
    for cid, info in assignments.items():
        blocks_list: List[int] = info["blocks"]  # type: ignore
        total_wt: float = info["total_weight"]  # type: ignore
        blocks_str: str = ", ".join(str(b) for b in blocks_list)
        print(
            f"Container {cid}: blocks {blocks_str} "
            f"(Total Weight of container: {total_wt})"
        )


def main() -> None:
    container_capacity, container_count = load_container_info(CONTAINER_INFO_FILENAME)
    blocks = load_blocks("blocks.csv")
    assignments = assign_containers(blocks, container_capacity, container_count)
    print_assignments(assignments)


if __name__ == "__main__":
    main()
