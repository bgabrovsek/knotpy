import itertools


def print_bar_chart(data: dict):
    if not data:
        print("No data to display.")
        return

    # ANSI color codes for cycling colors
    COLORS = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
    color_cycle = itertools.cycle(COLORS)
    RESET = "\033[0m"

    # Sort dictionary by keys
    sorted_items = sorted(data.items())
    keys, values = zip(*sorted_items)

    # Normalize values so the largest is 20
    max_value = max(values)
    scale = 100 / max_value if max_value > 0 else 1

    # Determine column widths for alignment
    max_key_length = max(len(str(k)) for k in keys)
    max_value_length = max(len(str(v)) for v in values)

    # Print the bar chart
    for key, value in sorted_items:
        bar_length = int(value * scale)
        bar_color = next(color_cycle)
        bar = bar_color + "█" * bar_length + RESET
        print(f"{key:<{max_key_length}} ({value:>{max_value_length}}) {bar}")



# Example usage
if __name__ == "__main__":
    data = {"apple": 50, "banana": 30, "cherry": 80, "date": 20}
    print_bar_chart(data)
