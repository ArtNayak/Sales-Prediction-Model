"""Extract the sales table from the PDF report into backend/data/sales_raw.csv.

Needs `pip install tabula-py` (and Java) and a "Sales Report.pdf" in the working directory.
"""
import os
import sys

import tabula

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from paths import RAW_CSV  # noqa: E402

tabula.convert_into("Sales Report.pdf", RAW_CSV, output_format="csv", pages="all")
