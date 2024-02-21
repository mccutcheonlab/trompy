import pytest
from pathlib import Path
import trompy as tp

def specify_filenames():
    string_csv_file = "./test_data/test_metafile.csv"
    string_txt_file = "./test_data/test_metafile.txt"
    string_xls_file = "./test_data/test_metafile.xls"
    string_xlsx_file = "./test_data/test_metafile.xlsx"

    files = [string_xlsx_file, string_xls_file, string_csv_file, string_txt_file]

    return files

def read_in_string_file():

    files = specify_filenames()
    for file in files:
        tablerows, header = tp.metafilereader(file)
        print(header)
        assert(len(header) == 3)

def read_in_pathlib_file():

    files = specify_filenames()
    for file in files:
        file = Path(file)
        tablerows, header = tp.metafilereader(file)
        assert(len(header) == 3)

# def test_delimiters():

#     for file in files:
#         tablerows, header = tp.metafilereader(file, delimiter=",")


if __name__ == "__main__":


    read_in_string_file()
    read_in_pathlib_file()
