import os
import sys
import requests
from rdkit.Chem import SDMolSupplier
from helpers import*


def main():
    url = "https://nmrshiftdb.nmr.uni-koeln.de/nmrshiftdb2.nmredata.sd"
    suppl = get_sdf_as_SDMolSupplier(url, "nmrshiftdb2.nmredata.sd")
    print('The total number of NMReData entries found in NMRShiftDB with raw data, including duplicated molecules, is: '+ str(len(suppl)) + '\n')
    
    lst = download_zips(suppl)
    
    print('NMRShiftDB downloading is finished\n')
    print('The number of unique authors combinations corresponding to nmrXiv projects is: ' + str(lst[0]))
    print('The number of molecules is: ' + str(lst[1]))
    print('The number of unique molecules/solvent combinations corresponding to nmrXiv samples is: ' + str(lst[2]))
    print('The number of downloaded spectra corresponding to nmrXiv spectra is: ' + str(lst[3]))

       
    create_datasets_folders()
    unzipper()
    rename_folders()
    structure_folders()
    delete_empty_folders(os.getcwd())
    print('\nThe process has ended successfully')
if __name__ == "__main__":
    sys.exit(main())
