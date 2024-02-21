# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:14:34 2020

@author: James Edgar McCutcheon
"""

from pathlib import Path
import openpyxl
import xlrd

def metafilereader(filename, sheetname="metafile", delimiter=","):
    """
    Reads in metafile. If an Excel file is given it uses the sheetname argument
    to specify sheet. Otherwise, text files work better than CSV files.

    Parameters
    ----------
    filename : String
        Path to metafile to be read in and interpreted.
    sheetname : String, optional
        Name of sheet within excel file to be used. Default is "metafile".
    delimiter : String, optional
        Delimiter used to separate values in the metafile. Default is ",".

    Returns
    -------
    tablerows : List of lists
        Rows from metafile.
    header : List
        First row from metafile which provides column names.
    """
    filename = Path(filename)
    extension = filename.suffix.lower()

    if extension == ".xlsx":
        
        wb = openpyxl.load_workbook(filename, data_only=True)
        sh = wb[sheetname]  # or wb.sheet_by_name('name_of_the_sheet_here')
        
        header = [cell.value for cell in sh[1]]
        
        tablerows=[]
        for row in sh.iter_rows(min_row=2):
            tablerows.append([cell.value for cell in row])
        
        wb.close()
    
    elif extension == ".xls":
        with xlrd.open_workbook(filename) as wb:
            sh = wb.sheet_by_name(sheetname)  # or wb.sheet_by_name('name_of_the_sheet_here')
            
            header = sh.row_values(0)
            
            tablerows=[]
            for r in range(1, sh.nrows):
                tablerows.append(sh.row_values(r))    
    
    elif extension == ".csv" or extension == '.txt':
        if extension == ".txt":
            delimiter = "\t"

        f = open(filename, 'r')
        f.seek(0)
        header = f.readlines()[0]
        f.seek(0)
        filerows = f.readlines()[1:]
        f.close()
        
        tablerows = []
        
        for i in filerows:
            tablerows.append(i.split(delimiter))
            
        header = header.split(delimiter)

        tablerows = [[item.strip() for item in sublist] for sublist in tablerows]
        header = [item.strip() for item in header]
    else:
        raise ValueError("File extension not supported. Please use .csv, .txt, .xls, or .xlsx")

    return tablerows, header
