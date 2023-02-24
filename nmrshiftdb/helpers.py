"""NMRshiftDB Import Helpers.

This module includes functions used to export NMRShiftDB database as NMReData files and to use those files to detect the locations of the raw NMR files and download them too. Finally, the downloaded files are unzipped and restructured to for 
nmrXiv submission.
"""

import os
import wget
import shutil
import zipfile

def get_name(entry):
    """Returns the name of the NMReData entry."""
    start = entry.find('<CHEMNAME>') +11
    end = entry.find('\n', start)
    
    name = entry[start:end]
    
    if 'InChI' in name:
        name = name[:name.find(' ')]
    elif ';' in name:
        name = name[:name.find(';')]
    if '/' in name:
        name = name.replace('/', '\\')
    
    return name

def get_solvent(entry):
    """Returns the solvent of the NMReData entry."""
    start = entry.find('_SOLVENT>') +10
    end = entry.find('\\', start)
    
    slv = entry[start:end]
    if '/' in slv:
        slv = slv.replace('/', '+')
    
    return slv

                     

def get_temp(entry):
    """Returns the temperature of the NMReData entry."""
    start = entry.find('_TEMPERATURE>') +14
    end = entry.find(' ', start)
    
    if start != 13:  
        temp = entry[start:end]
    else: 
        temp = 'unknown'
    
    return temp

def get_authors(entry):
    """Returns the authors of the NMReData entry."""
    start = entry.find('<AUTHOR')
    start = entry.find('\n', start) +1
    end = entry.find('\n', start)
    
    authors = entry[start:end]
    if ':' in authors:
        authors = authors[:authors.find(':')]
    return authors


def write_nmredata(entry):
    """Writes a molecule in an NMReData file named after its chemical name and temperature."""
    name = get_name(entry)
    solvent = get_solvent(entry)        
    temp = get_temp(entry)

    f = open(name+ '_'+ solvent+ '_' + temp+ '.nmredata', "w")
    f.write(entry)
    f.close()
    
    pass

def download_zips(entry):
    """download all the raw NMR files from the links found in the NMReData file, and return the number of projects, studies, and datasets in a list."""
    authors = get_authors(entry)
    name = get_name(entry) + '_' + get_solvent(entry) 
    
    number_of_projects =0
    number_of_studies =0
    number_of_spectra =0
    
    if not os.path.exists(authors):
        print(authors)
        number_of_projects +=1
        os.makedirs(authors)
    os.chdir('./'+ authors)
    
    
    if not os.path.exists(name):
        number_of_studies +=1
        os.makedirs(name)
    os.chdir('./'+ name)
    write_nmredata(entry)

    
    index = 0
    while entry.find('Spectrum_Location=http', index) != -1:
        number_of_spectra +=1
        start = entry.find('Spectrum_Location=http', index) + 18
        end = entry.find('rawdata', start) + 7
        index = end

        location = entry[start:end]
        wget.download(location)
        

    os.chdir("../..")
    return [number_of_projects, number_of_studies, number_of_spectra]

def create_datasets_folders():
    """Create folders for each dataset and unzip the downloaded spectrum file there. Then delete the zip files."""
    print('Unzipping spectra files in the corresponding created datasets folders. This might take a little while. Following, you can find the names of the authors folders where the spectra files are getting unzipped.\n')
    for authors in os.listdir("./"):
        if (authors != 'Nadine Kümmerer') and (os.path.isdir(authors)):
            print(authors)
            project_folder = os.getcwd() + '/' + authors
            for molecule in os.listdir(project_folder):
                if os.path.isdir(project_folder + '/' + molecule):
                    if os.path.isdir(project_folder + '/' + molecule):
                        study_folder = project_folder + '/' + molecule
                        for spectrum in os.listdir(study_folder):
                            if 'zip' in spectrum:
                                name = spectrum[:spectrum.find('.')]
                                dataset_folder = study_folder + '/' + name
                                os.makedirs(dataset_folder)
                                shutil.move(study_folder+ '/' +spectrum, dataset_folder)
                                for file in os.listdir(dataset_folder):
                                    if '.zip' in dataset_folder + '/' +file:
                                        try:
                                            with zipfile.ZipFile(dataset_folder + '/' +file, 'r') as zip_ref:
                                                zip_ref.extractall(dataset_folder)
                                            os.remove(dataset_folder + '/' +file)
                                        except:
                                            pass
    
    print('\nunzipping the following files has failed. Please try to unzip them manually:')
    for path, directories, files in os.walk("."):
        for file in files:
            if 'zip' in file:
                try: 
                    with zipfile.ZipFile(os.path.join(path, file), 'r') as zip_ref:
                        zip_ref.extractall(path)
                    os.remove(os.path.join(path, file))
                except:
                    print(os.path.join(path, file))
                            
    pass


          
def structure_folders():
    """Move files and folders to restructure them in a way suitable for nmrXiv submission."""
    print('\npreparing the folders structure for proper submision to nmrXiv. This might take a while. Here you find the names of molecules in preparation:\n')
    for authors in os.listdir("./"): 
        if authors != 'Nadine Kümmerer':
            if os.path.isdir(authors):
                print('\n')
                print(authors)
                project_folder = os.getcwd() + '/' + authors
                for molecule in os.listdir(project_folder):
                    print(molecule)
                    study_folder = project_folder + '/' + molecule
                    if os.path.isdir(study_folder):
                        for spectrum in os.listdir(study_folder):
                            if spectrum != '60003332_1H':
                                dataset_folder = study_folder + '/' + spectrum
                                if os.path.isdir(dataset_folder):
                                    innerFolder = dataset_folder
                                    #if "META-INF" not in os.listdir(innerFolder):
                                    while ("acqu" not in os.listdir(innerFolder)) and ("fid" not in os.listdir(innerFolder) and "ser" not in os.listdir(innerFolder)):
                                        for item in os.listdir(innerFolder):
                                            if item != "META-INF":
                                                if os.path.isdir(innerFolder + '/' + item):
                                                    innerFolder +=  '/' + item


                                    for f in os.listdir(innerFolder):
                                        try:
                                            shutil.move(innerFolder + '/'+ f, dataset_folder) 
                                        except:
                                            print(innerFolder)

pass