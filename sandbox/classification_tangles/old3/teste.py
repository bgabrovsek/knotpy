import random


def generate_random_booleans(n):
    # Generate a list of n random booleans (True or False)
    return "".join(random.choices("TF", weights=[0.8,0.2], k=n))


def count_max_consecutive_trues(boolean_list):
    max_consecutive_trues = 0
    current_count = 0

    # Loop through the list and count consecutive True values
    for value in boolean_list:
        if value:
            current_count += 1
            max_consecutive_trues = max(max_consecutive_trues, current_count)
        else:
            current_count = 0

    return max_consecutive_trues


if __name__ == '__main__':
    # Generate 5000 random booleans
    count = 0
    s = "T"*46

    for i in range(10000):
        random_booleans = generate_random_booleans(20000)
        if s in random_booleans:
            count += 1
    print(count/10000*100)