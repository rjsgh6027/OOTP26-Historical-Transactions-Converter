 =B  / playerID	transactionDate1	Type	FromTeam	ToTeam	  11252	10/1/2013	Fg			import csv
from struct import pack

def build_odb_from_csv(csv_path, output_path):
    with open(csv_path, newline='', encoding='utf-8-sig') as f:  
        reader = csv.DictReader(f)
        transactions = []
        for row in reader:
            y, m, d = row["date"].split("-")
            date_str = f"{int(m)}/{int(d)}/{y}"
            tx = f'{row["playerID"]}\t{date_str}\t{row["type"]}\t{row["fromTeam"]}\t{row["toTeam"]}\t'
            b = tx.encode("utf-8")
            transactions.append(pack("<H", len(b)) + b)

    header = b"\x00\x3D\x42\x04\x00\x00"
    start = b"\x2F\x00"
    fields = b"playerID\ttransactionDate1\tType\tFromTeam\tToTeam\t"
    end = b"\x00"

    full = header + start + fields + end + b''.join(transactions)
    with open(output_path, "wb") as f:
        f.write(full)

build_odb_from_csv("/content/transactions.csv", "/content/historical_transactions.odb")

