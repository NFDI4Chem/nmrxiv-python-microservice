import os
import sys
import requests
from rdkit.Chem import SDMolSupplier
from helpers import*


def main():
    print('NMRShiftDB downloading script has started. Please find downloaded items in the folder "output."\n')
    
    if not os.path.exists('output'):
        os.makedirs('output')
    os.chdir('./output')

    URL = "https://nmrshiftdb.nmr.uni-koeln.de/nmrshiftdb2.nmredata.sd"
    response = requests.get(URL)
    open("nmrshiftdb2.nmredata.sd", "wb").write(response.content)


    suppl =SDMolSupplier('nmrshiftdb2.nmredata.sd')
    print('The total number of NMReData entries found in NMRShiftDB with raw data, including duplicated molecules, is: '+ str(len(suppl)) + '\n')
    print('Downloading experimental NMR files. Here you can see the authors names from NMRShiftDB: ')
    
    lst = download_zips(suppl)
    
    print('NMRShiftDB downloading is finished\n')
    print('The number of unique authors combinations corresponding to nmrXiv projects is: ' + str(lst[0]))
    print('The number of molecules is: ' + str(lst[1]))
    print('The number of molecules corresponding to nmrXiv studies is: ' + str(lst[2]))
    print('The number of downloaded spectra corresponding to nmrXiv datasets is: ' + str(lst[3]))

       
    create_datasets_folders()
    unzipper()
    rename_folders()
    #structure_folders()
        
if __name__ == "__main__":
    sys.exit(main())
