import re
import pandas as pd
import numpy as np
# from exporter import text_to_textline

"""
Generate a doccano import compatible file
that contains the reports split into one sentence per line
"""
input = "data/ProcessedData.csv"
output = "data/processed_data.text"
column = "statement"

try:
    reports = pd.read_csv(input)
    print(f"Converting '{input}' into '{output}'...")
    np.savetxt(output, reports[column].sample(n=9000,random_state=2).values, fmt='%s')
    print(f'Conversion completed.')
except FileNotFoundError:
    print(f"File '{input}' could not be found.")

