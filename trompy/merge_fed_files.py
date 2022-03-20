# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 13:11:39 2022

@author: jmc010
"""
import sys
import getopt
import pandas as pd

def merge_files(files, output):
    print("merging files...", files)

    dfs = []
    for file in files:
        dfs.append(pd.read_csv(file))
    
    df_out = pd.concat(dfs)
    
    print("creating file...", output)
    
    df_out.to_csv(output, index=False)
    
def parse_args(argv):
    arg_input = ""
    arg_output = ""
    arg_help = "{0} -i <input> -o <output>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hi:o:", ["help", "input=", "output="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_input = arg
        elif opt in ("-o", "--output"):
            arg_output = arg

    print('input:', arg_input)
    print('output:', arg_output)
    
    files = arg_input.split(",")
    files = [file.strip() for file in files]

    merge_files(files, arg_output)

if __name__ == "__main__":
    parse_args(sys.argv)