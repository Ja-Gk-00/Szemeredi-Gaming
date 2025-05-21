import random


def has_arithmetic_progression(k: int, numbers: list[int]) -> bool:
    if k <= 1:
        return True
    s = set(numbers)
    sorted_nums = sorted(s)
    n = len(sorted_nums)
    for i in range(n):
        for j in range(i + 1, n):
            d = sorted_nums[j] - sorted_nums[i]
            count = 2
            next_val = sorted_nums[j] + d
            while next_val in s:
                count += 1
                if count >= k:
                    return True
                next_val += d
    return False


def find_winning_progression(k: int, numbers: list[int]) -> list[int]:
    s = set(numbers)
    sorted_nums = sorted(s)
    n = len(sorted_nums)
    for i in range(n):
        for j in range(i + 1, n):
            d = sorted_nums[j] - sorted_nums[i]
            prog = []
            for m in range(k):
                candidate = sorted_nums[i] + m * d
                if candidate in s:
                    prog.append(candidate)
                else:
                    break
            if len(prog) == k:
                return prog
    return []


def find_all_arithmetic_progressions(k: int, numbers: list[int]) -> list[list[int]]:
    s = set(numbers)
    sorted_nums = sorted(s)
    n = len(sorted_nums)
    progs = []
    for i in range(n):
        for j in range(i + 1, n):
            d = sorted_nums[j] - sorted_nums[i]
            prog = []
            for m in range(k):
                candidate = sorted_nums[i] + m * d
                if candidate in s:
                    prog.append(candidate)
                else:
                    break
            if len(prog) == k:
                progs.append(prog)
    return sorted(progs)


def generate_random_subset_with_progression(k, subset_size, lower, bound):
    if subset_size < k or subset_size > (bound - lower + 1):
        raise ValueError("Invalid subset size")
    max_d = (bound - lower) // (k - 1)
    if max_d < 1:
        raise ValueError("Bound too small")
    d = random.randint(1, max_d)
    a_max = bound - (k - 1) * d
    a = random.randint(lower, a_max)
    progression = {a + i * d for i in range(k)}
    available = list(set(range(lower, bound + 1)) - progression)
    additional = random.sample(available, subset_size - k)
    X = list(progression) + additional
    random.shuffle(X)
    return X, sorted(list(progression))
