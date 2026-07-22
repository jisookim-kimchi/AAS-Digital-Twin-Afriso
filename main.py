import sys
import glob
import os
from AAS.parsing import process_excel

def main():
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            try:
                process_excel(arg)
            except FileNotFoundError as e:
                print(f"Error: {e}")
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        xlsx_dir = os.path.join(base_dir, "xlsx")
        excel_files = glob.glob(os.path.join(xlsx_dir, "*.xlsx"))
        
        for excel_file in excel_files:
            try:
                process_excel(excel_file)
            except FileNotFoundError as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
