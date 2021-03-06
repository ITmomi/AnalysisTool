from concurrent.futures import ThreadPoolExecutor
import threading
import random

values = [2,3,4,5,6,7,8]

def multiplyByTwo(n):
    return 2 * n

def main():
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(multiplyByTwo, values)
        for result in results:
            print(result)



if __name__ == '__main__':
    main()
    results = list(map(multiplyByTwo, values))
    print(results)