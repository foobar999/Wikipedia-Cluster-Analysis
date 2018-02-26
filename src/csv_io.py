import csv

def write_rows(csv_filename, rows):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=' ')
        csv_writer.writerows(rows)   # schreibe Einträge der Form [(0,CONTRIBUTOR_1),(1,CONTRIBUTOR_2),...]
    