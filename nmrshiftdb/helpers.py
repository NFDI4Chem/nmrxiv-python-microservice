"""NMRshiftDB Import Helpers.

This module includes functions used to export NMRShiftDB database as an SDF file with NMReData entries,
which are to detect the locations of the raw NMR files and download them too. 
Finally, the downloaded files are unzipped and restructured for nmrXiv submission.
""" 

import os
import html
import wget
import shutil
import codecs
import zipfile
import requests
from rdkit import Chem
from io import StringIO
from rdkit.Chem.rdchem import Mol
from rdkit.Chem import SDMolSupplier


def get_sdf_as_SDMolSupplier(url, name):
    "Download an sdf file from a URL into a named file, and return an SDMolSupplier object with the entries there."
    
    print("""\nNMRShiftDB downloading script has started. Please find downloaded items in the folder 'output' where we provide two folders for projects that are ready for submission (without_issues), and the  problematic ones (with_issues) \n""")
    
    if not os.path.exists('output'):
        os.makedirs('output')
    os.chdir('./output')
    
    response = requests.get(url)
    open(name, "wb").write(response.content)
    
    return SDMolSupplier(name)

def get_authors(mol):
    """Returns the authors from the corresponding tag in a rdkit.Chem.rdchem Mol (mol)"""
    
    # Authors have different tags, but they are always the second tag.
    authors_tag = mol.GetPropNames()[1]
    authors = Mol.GetProp(mol, authors_tag)
    
    # Remove article name
    if ':' in authors:
        authors = authors[:authors.find(':')]
        
    
    Nils_names = ["Nils Schoerer", "Nils Schloerer"]
    if authors in Nils_names: 
        authors = "Nils Schlörer"
    return authors

def get_molecule_id(mol): 
    """Returns the molecule NMRShiftDB ID from the corresponding tag NMREDATA_ID 
    in a rdkit.Chem.rdchem Mol (mol)"""

    value = Mol.GetProp(mol, 'NMREDATA_ID')
    ID = value[value.find('DB_ID=')+6: -1]
    
    return ID

def get_links(mol):
    """Returns the all the spectra links from one rdkit.Chem.rdchem Mol (mol),
    which corresponds to one NMReData block."""
    
    spectra_tags = [tag for tag in mol.GetPropNames() if "1D" in tag or "2D" in tag]
    values = [Mol.GetProp(mol, tag) for tag in spectra_tags if 'http' in Mol.GetProp(mol, tag)]
    
    links = [value[value.find('=')+1:value.find('\\')] for value in values]
    
    return links

def get_name(mol):
    """Returns the molecule chemical name from the corresponding tag CHEMNAME 
    in a rdkit.Chem.rdchem Mol (mol)"""
    
    name = Mol.GetProp(mol, 'CHEMNAME')
    
    # removing the synonyms
    if 'InChI' in name and name[:5]=="InChI":
        name = name[:name.find(' ')]
    elif "IUPAC from" in name:
        name = name[:name.find(' (IUPAC from')]
    elif '; ' in name:
         if "methyl 2,3,4,6-tetra-O-methyl-" not in name:
            name = name[:name.find('; ')]
    
    #ensuring the molecule name doesn't affect the files pathes
    if '/' in name:
        name = name.replace('/', '\\')
        
    # replacing ascii characters with special HTML characters
    name = html.unescape(name)
    return name

def get_sample_name(mol):
    """A sample consists of molecule and solvent. 
    Its name has the NMRShiftDB molecule ID with the names of the molecule and the solvent, 
    taken from a rdkit.Chem.rdchem Mol (mol)"""
    
    ID =get_molecule_id(mol)
    name = get_name(mol)
    solvent = get_solvent(mol)
    sample_name = ID+ '_' + name+ '_'+ solvent
    
    return sample_name

def get_solvent(mol):
    """Returns the NMR solvent from the corresponding tag NMREDATA_SOLVENT 
    in a rdkit.Chem.rdchem Mol (mol)"""
    
    solvent = Mol.GetProp(mol, 'NMREDATA_SOLVENT')
        
    #ensuring the molecule name doesn't affect the files pathes
    if '/' in solvent:
        solvent = solvent.replace('/', ', ')
   
    solvent = solvent[:-1]
    return solvent

def get_temperature(mol):
    """Returns the temperature from the corresponding tag NMREDATA_TEMPERATURE 
    in a rdkit.Chem.rdchem Mol (mol)"""
    
    try:
        temperature = Mol.GetProp(mol, 'NMREDATA_TEMPERATURE')
        temperature = temperature[:temperature.find(' ')]
    except:
        temperature = "unknown"
    
    return temperature

def write_nmredata(mol):
    """Writes a rdkit.Chem.rdchem Mol molecule in an NMReData file,
    named after its sample name and temperature."""
    
    sample_name = get_sample_name(mol)
    temp = get_temperature(mol)

    file_name =  sample_name+ '_' + temp+ '.nmredata'
    
    sio = StringIO()
    writer = Chem.SDWriter(sio)
    writer.write(mol)
    writer.close()
    sio.seek(0)
    open(file_name, "wb").write(str.encode(sio.read()))
    
    pass

def download_zips(MolSupplier):
    """
    - Create folders for projects with pending issues (with_issues), and the rest which don't (without_issues).
    - Create folders based on authors combinations (corresponding to nmrXiv projects).
    - Create folders within the authors folders based on the molecules they submitted 
    (corresponding to nmrXiv samples). 
    - Write the NMReData files in the corresponding samples folders.
    - Download all the raw NMR files from the links found in the NMReData file in the 
    corresponding samples folders.
    - Return the number of projects, molecules, samples, and spectra as a list.
    """

    print("""Downloading experimental NMR files. Here you can see the authors names from NMRShiftDB whose files are being downloaded: \n""")

    number_of_projects =0
    number_of_samples =0
    number_of_spectra =0
    
    mols = []
    
    os.makedirs("with_issues")
    os.makedirs("without_issues")
    
    with_issues = [
        'Nadine Kümmerer', 
        'Sean R. Johnson; Wajid Waheed Bhat; Radin Sadre; Garret P. Miller; Alekzander Sky Garcia; Björn Hamberger', 
        'Sean Johnson',
        'Franziska Reuß; Klaus-Peter Zeller; Hans-Ullrich Siehl; Stefan Berger; Dieter Sicker',
        'Stefan Kuhn',
        'Rainer Haessner',
        'Nils Schlörer',
        'Raphael Stoll',
        'Stefan Berger; Dieter Sicker'
    ]


    for mol in MolSupplier:
        authors = get_authors(mol)
        name = get_name(mol)
        sample_name = get_sample_name(mol)
        
        mols.append(name)
        
        if authors in with_issues:
            prefix = "with_issues/"
        else:
            prefix = "without_issues/"

        if not os.path.exists(prefix+authors):
            print(authors)
            number_of_projects +=1
            os.makedirs(prefix+authors)
        os.chdir('./'+ prefix+authors)

        if not os.path.exists(sample_name):
            number_of_samples +=1

            os.makedirs(sample_name)
        os.chdir('./'+ sample_name)
        write_nmredata(mol)

        links = get_links(mol)
        number_of_spectra += len(links)
        for link in links:
            try:
                wget.download(link)
            except:
                print(link)
                print(authors)
                print(name)

        os.chdir("../../..")
        
    mols = set(mols)
    number_of_mols = len(mols)
    return [number_of_projects, number_of_mols, number_of_samples, number_of_spectra]

def create_datasets_folders():
    """Create folders for each dataset to unzip the downloaded spectrum file there.
    The aim is to avoid unzipping files with the same content in the same folder.
    Then delete the zip files as not wanted in nmrXiv submission."""
    
    for folder in os.listdir("./"):
        if os.path.isdir("./" + folder):
            for authors in os.listdir("./" + folder):
                if os.path.isdir("./" + folder + '/' + authors):
                    project_folder = os.getcwd()+ '/' + folder + '/' + authors
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

    print("Creating folders to unzip spectra files is done. \n")
    pass


def unzipper():
    """Create folders for each dataset and unzip the downloaded spectrum file there. 
    Then delete the zip files."""
    
    print("""Unzipping spectra files in the corresponding created datasets folders. This might take a little while. Following, you can find the names of the authors folders where the spectra files are getting unzipped.\n""")
    with_siiues = ['Nadine Kümmerer']
    

    for authors in os.listdir("./without_issues"): 
        if os.path.isdir("./without_issues/" + authors):
            project_folder = os.getcwd() + '/without_issues/' + authors
            print(authors)
            for molecule in os.listdir(project_folder):
                if os.path.isdir(project_folder + '/' + molecule):
                    sample_folder = project_folder + '/' + molecule
                    for spectrum in os.listdir(sample_folder):
                        if os.path.isdir(sample_folder + '/' + spectrum):
                            spectrum_folder = sample_folder + '/' + spectrum
                            for file in os.listdir(spectrum_folder):
                                if '.zip' in spectrum_folder + '/' +file:
                                    try:
                                        with zipfile.ZipFile(spectrum_folder + '/' +file, 'r') as zip_ref:
                                            zip_ref.extractall(spectrum_folder)
                                        os.remove(spectrum_folder + '/' +file)
                                    except:
                                        print(spectrum_folder + '/' +file)

    for path, directories, files in os.walk("./without_issues"):
        for file in files:
            if '.zip' in file:
                try:
                    with zipfile.ZipFile(os.path.join(path, file), 'r') as zip_ref:
                        zip_ref.extractall(path)
                    os.remove(os.path.join(path, file))
                except:
                    print(path)
               
    print('unzipping has ended')
    pass

def get_Bruker_number(innerFolder):
    """Find the Bruker instrument original sample number from 'acqu' file."""
    
    if "acqu" in os.listdir(innerFolder):
        with codecs.open(innerFolder + '/acqu', 'r', encoding='utf-8',
                         errors='ignore') as f:

            lines = f.readlines()
        for line in lines:
            if 'acqu' in line:
                break
        else:
            print(innerFolder)
        line = line[:line.rfind('/acqu')]
        if line[-1] == '/':
            line = line[:-1]
        line = line[line.rfind('/')+1:]
        return line
    else:
        print(innerFolder)
        pass
    pass

def rename_folders():
    """Rename the Bruker folders for spectra that were initially named by users to 
    their original instrument name."""
    for authors in os.listdir("./without_issues"): 
        if os.path.isdir("./without_issues/" + authors):
            project_folder = os.getcwd() + '/without_issues/' + authors
            for molecule in os.listdir(project_folder):
                study_folder = project_folder + '/' + molecule
                if os.path.isdir(study_folder):
                    for spectrum in os.listdir(study_folder):
                        dataset_folder = study_folder + '/' + spectrum
                        if os.path.isdir(dataset_folder):
                            innerFolder = dataset_folder
                            while ("acqu" not in os.listdir(innerFolder)) and ("fid" not in os.listdir(innerFolder) and "ser" not in os.listdir(innerFolder)):
                                for item in os.listdir(innerFolder):
                                    if os.path.isdir(innerFolder + '/' + item):
                                        innerFolder +=  '/' + item


                            suffix = innerFolder[innerFolder.rfind("/")+1:]
                            n = get_Bruker_number(innerFolder)
                            target = innerFolder[:innerFolder.rfind(suffix)] +n
                            os.rename(innerFolder, target)
    print("""Spectra folders were renamed to their original instrument number.""")
    pass

def structure_folders():
    """Move files and folders to restructure them in a way suitable for nmrXiv submission."""
    print('\npreparing the folders structure for proper submision to nmrXiv. This might take a while. Here you find the names of molecules in preparation:\n')
    for authors in os.listdir("./without_issues"): 
        if os.path.isdir("./without_issues/" + authors):
            project_folder = os.getcwd() + '/without_issues/' + authors
            for molecule in os.listdir(project_folder):
                study_folder = project_folder + '/' + molecule
                if os.path.isdir(study_folder):
                    for spectrum in os.listdir(study_folder):
                        dataset_folder = study_folder + '/' + spectrum
                        if os.path.isdir(dataset_folder):
                            innerFolder = dataset_folder
                            while ("acqu" not in os.listdir(innerFolder)) and ("fid" not in os.listdir(innerFolder) and "ser" not in os.listdir(innerFolder)):
                                for item in os.listdir(innerFolder):
                                    if os.path.isdir(innerFolder + '/' + item):
                                        innerFolder +=  '/' + item


                            if innerFolder[innerFolder.rfind('/')+1:] not in os.listdir(study_folder):
                                try:
                                    shutil.move(innerFolder, study_folder) 
                                except:
                                    pass
                            else:
                                print(innerFolder)
    pass

def delete_empty_folders(root):

    deleted = set()
    
    for current_dir, subdirs, files in os.walk(root, topdown=False):

        still_has_subdirs = any(
            subdir for subdir in subdirs
            if os.path.join(current_dir, subdir) not in deleted
        )
    
        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted