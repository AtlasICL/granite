from typing import List, Tuple, Dict, Union
import pandas as pd

# Type alias for clarity
dBlock = Tuple[int, float]
ContainerMap = Dict[int, Dict[str, Union[List[int], float]]]


def load_blocks(path: str) -> List[dBlock]:
    """Load CSV and return list of (BlockNo, Weight)."""
    df = pd.read_csv(path)
    return list(df[['BlockNo', 'Weight']].itertuples(index=False, name=None))


def find_best_subset(
    blocks: List[dBlock], capacity: float
) -> Tuple[List[dBlock], float]:
    best_subset: List[dBlock] = []
    best_weight: float = 0.0

    def search(start: int, curr: List[dBlock], weight: float) -> None:
        nonlocal best_subset, best_weight
        if weight > capacity:
            return
        if weight > best_weight:
            best_weight, best_subset = weight, curr.copy()
        for i in range(start, len(blocks)):
            blk = blocks[i]
            curr.append(blk)
            search(i + 1, curr, weight + blk[1])
            curr.pop()

    search(0, [], 0.0)
    return best_subset, best_weight


def assign_containers(
    blocks: List[dBlock], capacity: float, count: int
) -> ContainerMap:
    """Pack blocks into `count` containers."""
    remaining = blocks.copy()
    assignments: ContainerMap = {}
    for cid in range(1, count + 1):
        if not remaining:
            break
        combo, total = find_best_subset(remaining, capacity)
        assignments[cid] = {
            'blocks': [b[0] for b in combo],
            'total_weight': total
        }
        for b in combo:
            remaining.remove(b)
    return assignments