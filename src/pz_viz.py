import os

import camelot
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

file_name = "Redrex - Fatura (1)"
path = os.path.abspath(f"Project_pdf_csv/src/files/redrex/{file_name}.pdf")

print()
print(f"Caminho absoluto: {path}")

tables = camelot.read_pdf(
        path,
        pages="1-end",
        flavor="stream",
        table_areas=["65, 558, 500, 298"],
        columns=["75, 107, 156, 212, 280, 336, 383, 450"],
        strip_text=".\n",
    )
print(tables)



print(tables[0].parsing_report)

camelot.plot(tables[0], kind="contour")
plt.show()

print("pause")