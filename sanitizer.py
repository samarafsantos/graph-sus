import csv
import pandas as pd

year = '2024'
month = '03'

input_file = f"./assets/original/RO_{year}{month}_HOSP_CONS.csv"
output_file = f"./assets/sanitized/RO_{year}{month}_HOSP_CONS_sanitized.xlsx"
target_column = "CID_1"
columns = ['ID_EVENTO_ATENCAO_SAUDE', 'FAIXA_ETARIA', 'SEXO', 'CD_MUNICIPIO_BENEFICIARIO', 'UF_PRESTADOR', 'TEMPO_DE_PERMANENCIA', 'PORTE', 'CID_1']


with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
   reader = csv.DictReader(infile, delimiter=';')
   filtered_rows = [
       {col: row[col] for col in columns if col in row}
       for row in reader
       if row.get(target_column, '').strip() != ''
   ]

df = pd.DataFrame(filtered_rows)
df.to_excel(output_file, index=False, engine='openpyxl')

# with open(output_file, mode='w', newline='', encoding='utf-8') as oufile:
#     writer = csv.DictWriter(oufile, fieldnames=columns, delimiter=';')
#     writer.writeheader()
#     writer.writerows(filtered_rows)

print(f'Filtered file saved as {output_file}')