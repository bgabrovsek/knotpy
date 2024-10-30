def split_file(input_file, output_file_prefix, lines_per_file=1000):
    # Open the input file
    with open(input_file, 'r') as infile:
        file_count = 0
        lines = []

        # Loop through each line in the input file
        for line_number, line in enumerate(infile, start=1):
            lines.append(line)

            # Once we have `lines_per_file` lines, write them to a new file
            if line_number % lines_per_file == 0:
                output_file = f"{output_file_prefix}_{file_count}.txt"
                with open(output_file, 'w') as outfile:
                    outfile.writelines(lines)

                # Clear the lines buffer and increment file count
                lines = []
                file_count += 1

        # Write any remaining lines to a final file if needed
        if lines:
            output_file = f"{output_file_prefix}_{file_count}.txt"
            with open(output_file, 'w') as outfile:
                outfile.writelines(lines)

    print(f"File split into {file_count + 1} files.")


input_file = 'data/old3/canonical_knots.txt'
output_file_prefix = 'data/tangles/canonical_knots'
split_file(input_file, output_file_prefix, lines_per_file=1024)