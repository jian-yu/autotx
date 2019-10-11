import random


def Select(arr):
    normalizeArr = []
    sum = 0.0
    for a in arr:
        sum += a[1]
    for index in range(len(arr)):
        if sum == 0:
            continue
        normalizeArr.append(1 - (arr[index])[1] / sum)
    sum = 0.0
    for b in normalizeArr:
        sum += b
    for index in range(len(normalizeArr)):
        if sum == 0:
            continue
        normalizeArr[index] = normalizeArr[index] / sum
    sum = 0.0
    seed = random.random()
    for index in range(len(normalizeArr)):
        sum += normalizeArr[index]
        if sum > seed:
            return index
    return len(arr) - 1
