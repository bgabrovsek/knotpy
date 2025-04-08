import codecs


def read_file_with_encodings(file_path, encodings):
    """
    Attempts to read a text file with different specified encodings and print its contents.

    :param file_path: Path to the text file.
    :type file_path: str
    :param encodings: List of encodings to try.
    :type encodings: list
    """
    for encoding in encodings:
        try:
            print(f"Trying encoding: {encoding}")
            with codecs.open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                print("Successfully read with encoding:", encoding)
                print(content)
                print("\n---\n")
                return  # Stop after the first successful read
        except Exception as e:
            print(f"Failed to read with encoding {encoding}: {e}")
            print("\n---\n")


# List of encodings to try
encodings_to_try = ['utf-8', 'iso-8859-1', 'utf-16', 'utf-16le', 'utf-16be', 'utf-32']

# Specify the path to your file
file_path = 'file.txt'

# Call the function with the path and list of encodings
read_file_with_encodings(file_path, encodings_to_try)