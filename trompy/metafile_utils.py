# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:14:34 2020

@author: admin
"""

import csv
import xlrd

def metafilemaker(xlfile, metafilename, sheetname='metafile', fileformat='csv'):
    """
    Makes metafile (txt or csv) from Excel sheet for reading in by metafilereader

    Parameters
    ----------
    xlfile : String
        Path to Excel file to be opened containing sheet to be made into metafile.
    metafilename : String 
        Path for metafile to be saved into (without extension).
    sheetname : String, optional
        Name of sheet in Excel file. The default is 'metafile'.
    fileformat : String, optional
        File format to save in. Options are 'csv' or 'txt. The default is 'csv'.

    Returns
    -------
    None.

    """
    with xlrd.open_workbook(xlfile) as wb:
        sh = wb.sheet_by_name(sheetname)  # or wb.sheet_by_name('name_of_the_sheet_here')
        
        if fileformat == 'csv':
            with open(metafilename+'.csv', 'w', newline="") as f:
                c = csv.writer(f)
                for r in range(sh.nrows):
                    c.writerow(sh.row_values(r))
        if fileformat == 'txt':
            with open(metafilename+'.txt', 'w', newline="") as f:
                c = csv.writer(f, delimiter="\t")
                for r in range(sh.nrows):
                    c.writerow(sh.row_values(r))
    
def metafilereader(filename):
    """
    Reads in metafile.

    Parameters
    ----------
    filename : String
        Path to metafile to be read in and interpreted.

    Returns
    -------
    tablerows : List of lists
        Rows from metafile.
    header : List
        First row from metafile which provides column names.

    """
    
    f = open(filename, 'r')
    f.seek(0)
    header = f.readlines()[0]
    f.seek(0)
    filerows = f.readlines()[1:]
    
    tablerows = []
    
    for i in filerows:
        tablerows.append(i.split('\t'))
        
    header = header.split('\t')
    # need to find a way to strip end of line \n from last column - work-around is to add extra dummy column at end of metafile
    return tablerows, header