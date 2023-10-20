"""
Load PD codes for thetas from data_topoly_pd.py and save it to a .csv file.
"""

import csv

from data_topoly_pd import PD

csv_output_file = 'theta-pd-non-ccw.csv'

count = 0
with open(csv_output_file, 'w') as file:

    csv_writer = csv.writer(file)
    csv_writer.writerow(["Name", "PD"])
    for name, pd_code in PD.items():
        csv_writer.writerow([name, pd_code.replace(";",",")])
        count += 1

print(f'Written {count} codes to {csv_output_file}.')
