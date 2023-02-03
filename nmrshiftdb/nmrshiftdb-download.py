import os
import sys
import requests
from helpers import*


def main():
    print('NMRShiftDB downloading script has started. Please find downloaded items in the folder "output."\n')
    
    if not os.path.exists('output'):
        os.makedirs('output')
    os.chdir('./output')
    
    URL = "https://nmrshiftdb.nmr.uni-koeln.de/nmrshiftdb2.nmredata.sd"
    response = requests.get(URL)
    open("nmrshiftdb2.nmredata.sd", "wb").write(response.content)

    f = open("nmrshiftdb2.nmredata.sd", "r")
    text = f.read()
    f.close() 

    entries = text.split('$$$$\n')[:-1]
    print('The total number of NMReData entries found in NMRShiftDB with raw data, including duplicated molecules, is: '+ str(len(entries)) + '\n')
    
    number_of_projects =0
    number_of_studies =0
    number_of_spectra =0
    
    print('Downloading experimental NMR files. Here you can see the authors names from NMRShiftDB: ')

    for entry in entries:
        lst = download_zips(entry)
        number_of_projects +=lst[0]
        number_of_studies +=lst[1]
        number_of_spectra +=lst[2]

    print('NMRShiftDB downloading is finished\n')
    print('The number of unique authors combinations corresponding to nmrXiv projects is: ' + str(number_of_projects))
    print('The number of molecules corresponding to nmrXiv studies is: ' + str(number_of_studies))
    print('The number of downloaded spectra corresponding to nmrXiv datasets is: ' + str(number_of_spectra))

       
    create_datasets_folders()
    structure_folders()
        
if __name__ == "__main__":
    sys.exit(main())
