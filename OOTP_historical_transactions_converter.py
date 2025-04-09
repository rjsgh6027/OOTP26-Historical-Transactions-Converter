import csv
from struct import pack
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


# ─────────────────────────────
# 📤 CSV → ODB
# ─────────────────────────────
def build_odb_from_csv(csv_path, output_path):
    transactions = []
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                y, m, d = row["date"].split("-")
                date_str = f"{int(m)}/{int(d)}/{y}"
            except ValueError:
                print(f"⚠ Invalid date format: {row['date']}")
                continue
            tx_str = f'{row["playerID"]}\t{date_str}\t{row["type"]}\t{row["fromTeam"]}\t{row["toTeam"]}\t'
            tx_bytes = tx_str.encode("utf-8")
            length = len(tx_bytes)
            if length > 255:
                print(f"⚠ Transaction too long: {tx_str}")
                continue
            length_bytes = b'\x00' + pack("<B", length) + b'\x00'
            transactions.append(length_bytes + tx_bytes)

    header = b"\x00\x3D\x42\x04\x00\x00"
    start = b"\x2F\x00"
    fields = b"playerID\ttransactionDate1\tType\tFromTeam\tToTeam\t"
    full = header + start + fields + b''.join(transactions)

    with open(output_path, "wb") as f:
        f.write(full)


# ─────────────────────────────
# 📥 ODB → CSV
# ─────────────────────────────
def convert_date_to_iso(date_str):
    try:
        m, d, y = date_str.split("/")
        return f"{y}-{int(m):02d}-{int(d):02d}"
    except ValueError:
        return ""


def parse_odb_to_csv(odb_path, output_csv_path):
    with open(odb_path, "rb") as f:
        data = f.read()

    header_len = 6 + 2
    field_marker = b"playerID\ttransactionDate1\tType\tFromTeam\tToTeam\t"
    data_start = header_len + len(field_marker)

    i = data_start
    records = []
    while i < len(data):
        if data[i] != 0x00 or data[i+2] != 0x00:
            raise ValueError(f"Unexpected length byte structure at offset {i}")
        length = data[i+1]
        i += 3
        tx_data = data[i:i+length]
        i += length
        parts = tx_data.decode("utf-8").split("\t")
        if len(parts) >= 5:
            records.append({
                "playerID": parts[0],
                "date": convert_date_to_iso(parts[1]),
                "type": parts[2],
                "fromTeam": parts[3],
                "toTeam": parts[4]
            })

    with open(output_csv_path, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["playerID", "date", "type", "fromTeam", "toTeam"])
        writer.writeheader()
        writer.writerows(records)


# ─────────────────────────────
# 🎛️ 버튼 핸들러
# ─────────────────────────────
def convert_csv_to_odb():
    csv_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV Files", "*.csv")])
    if not csv_path:
        return
    output_path = filedialog.asksaveasfilename(title="Save ODB file", defaultextension=".odb", filetypes=[("ODB Files", "*.odb")])
    if not output_path:
        return
    try:
        build_odb_from_csv(csv_path, output_path)
        messagebox.showinfo("Success", "✅ CSV → ODB conversion completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {e}")


def convert_odb_to_csv():
    odb_path = filedialog.askopenfilename(title="Select ODB file", filetypes=[("ODB Files", "*.odb")])
    if not odb_path:
        return
    output_path = filedialog.asksaveasfilename(title="Save CSV file", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not output_path:
        return
    try:
        parse_odb_to_csv(odb_path, output_path)
        messagebox.showinfo("Success", "✅ ODB → CSV conversion completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred: {e}")


# ─────────────────────────────
# 🖥️ GUI 실행
# ─────────────────────────────
def launch_gui():
    root = tk.Tk()
    root.title("OOTP26 Historical Transaction Converter")
    root.geometry("400x250")
    root.configure(bg="#f5f5f5")

    style = ttk.Style()
    style.configure("TButton", font=("Segoe UI", 11), padding=10)
    style.configure("TLabel", font=("Segoe UI", 14, "bold"), background="#f5f5f5")

    ttk.Label(root, text="OOTP26 Historical Transaction Converter").pack(pady=5)

    ttk.Button(root, text="📥 Convert ODB → CSV", command=convert_odb_to_csv).pack(pady=5)
    ttk.Button(root, text="📤 Convert CSV → ODB", command=convert_csv_to_odb).pack(pady=10)
    ttk.Button(root, text="❌ Exit", command=root.destroy).pack(pady=20)

    root.mainloop()


# 실행
if __name__ == "__main__":
    launch_gui()
