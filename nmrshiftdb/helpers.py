"""NMRshiftDB Import Helpers.

This module includes functions used to export NMRShiftDB database as an SDF file with NMReData entried and to use those entries to detect the locations of the raw NMR files and download them too. Finally, the downloaded files are unzipped and restructured to for 
nmrXiv submission.
"""
import os
import html
import wget
import shutil
import codecs
import zipfile
from rdkit import Chem
from io import StringIO
from rdkit.Chem.rdchem import Mol

def get_authors(mol):
    """Returns the authors of the NMReData entry."""
    authors_tag = mol.GetPropNames()[1]
    authors = Mol.GetProp(mol, authors_tag)
    if ':' in authors:
        authors = authors[:authors.find(':')]
        
    
    Nils_names = ["Nils Schoerer", "Nils Schloerer"]
    if authors in Nils_names: 
        authors = "Nils Schlörer"
    return authors

def get_molecule_id(mol): 
    """Returns the molecule NMRShiftDB ID."""
    value = Mol.GetProp(mol, 'NMREDATA_ID')
    ID = value[value.find('DB_ID=')+6: -1]
    
    return ID

def get_links(mol):
    """Returns the name of the NMReData entry."""
    spectra_tags = [tag for tag in mol.GetPropNames() if "1D" in tag or "2D" in tag]
    values = [Mol.GetProp(mol, tag) for tag in spectra_tags if 'http' in Mol.GetProp(mol, tag)]
    
    links = []
    for value in values:
        link = value[value.find('=')+1:value.find('\\')]
        links.append(link)
    return links

def get_name(mol):
    """Returns the name of the NMReData entry."""
    name = Mol.GetProp(mol, 'CHEMNAME')
    
    if 'InChI' in name and name[:5]=="InChI":
        name = name[:name.find(' ')]
    elif "IUPAC from" in name:
        name = name[:name.find(' (IUPAC from')]
    elif '; ' in name:
         if "methyl 2,3,4,6-tetra-O-methyl-" not in name:
            name = name[:name.find('; ')]
    
    if '/' in name:
        name = name.replace('/', '\\')
    name = html.unescape(name)
    return name

def get_sample_name(mol):
    ID =get_molecule_id(mol)
    name = get_name(mol)
    solvent = get_solvent(mol)
    sample_name = ID+ '_' + name+ '_'+ solvent
    
    return sample_name

def get_solvent(mol):
    """Returns the solvent of the NMReData entry."""
    solvent = Mol.GetProp(mol, 'NMREDATA_SOLVENT')
        
    if '/' in solvent:
        solvent = solvent.replace('/', ', ')
   
    solvent = solvent[:-1]
    return solvent

def get_temperature(mol):
    """Returns the temperature of the NMReData entry."""
    try:
        temperature = Mol.GetProp(mol, 'NMREDATA_TEMPERATURE')
        temperature = temperature[:temperature.find(' ')]
    except:
        temperature = "unknown"
    
    return temperature

def write_nmredata(mol):
    """Writes a molecule in an NMReData file named after its chemical name, solvent and temperature."""
    sample_name = get_sample_name(mol)
    temp = get_temperature(mol)

    file_name = sample_name+ '_' + temp+ '.nmredata'
    
    sio = StringIO()
    writer = Chem.SDWriter(sio)
    writer.write(mol)
    writer.close()
    sio.seek(0)
    open(file_name, "wb").write(str.encode(sio.read()))
    
    pass



def download_zips(MolSupplier):
    """download all the raw NMR files from the links found in the NMReData file, and return the number of projects, studies, and datasets in a list."""

    number_of_projects =0
    number_of_studies =0
    number_of_spectra =0
    
    mols = []
    
    os.makedirs("with_issues")
    os.makedirs("without_issues")
    lst = ['Nadine Kümmerer', 
           "Sean R. Johnson; Wajid Waheed Bhat; Radin Sadre; Garret P. Miller; Alekzander Sky Garcia; Björn Hamberger", 
           "Sean Johnson",
           "Franziska Reuß; Klaus-Peter Zeller; Hans-Ullrich Siehl; Stefan Berger; Dieter Sicker",
           "Stefan Kuhn"]

    
    for mol in MolSupplier:
        authors = get_authors(mol)
        name = get_name(mol)
        solvent = get_solvent(mol) 
        sample_name = get_sample_name(mol)
        
        mols.append(name)
        
        if authors in lst:
            prefix = "with_issues/"
        else:
            prefix = "without_issues/"

        if not os.path.exists(prefix+authors):
            print(authors)
            number_of_projects +=1
            os.makedirs(prefix+authors)
        os.chdir('./'+ prefix+authors)

        if not os.path.exists(sample_name):
            number_of_studies +=1

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
    return [number_of_projects, number_of_mols, number_of_studies, number_of_spectra]

def create_datasets_folders():
    """Create folders for each dataset and unzip the downloaded spectrum file there. Then delete the zip files."""
    os.chdir('./without_issues')
    for authors in os.listdir("./"):
        if os.path.isdir(authors):
            project_folder = os.getcwd() + '/' + authors
            for molecule in os.listdir(project_folder):
                if os.path.isdir(project_folder + '/' + molecule):
                    if os.path.isdir(project_folder + '/' + molecule):
                        study_folder = project_folder + '/' + molecule
                        n = 0
                        for spectrum in os.listdir(study_folder):
                            if 'zip' in spectrum:
                                name = spectrum[:spectrum.find('.')]
                                dataset_folder = study_folder + '/' + name
                                os.makedirs(dataset_folder)
                                shutil.move(study_folder+ '/' +spectrum, dataset_folder)
    pass

def unzipper():
    """Create folders for each dataset and unzip the downloaded spectrum file there. Then delete the zip files."""
    print('Unzipping spectra files in the corresponding created datasets folders. This might take a little while. Following, you can find the names of the authors folders where the spectra files are getting unzipped.\n')
    for authors in os.listdir("./"):
        if os.path.isdir(authors):
            print(authors)
            project_folder = os.getcwd() + '/' + authors
            for molecule in os.listdir(project_folder):
                if os.path.isdir(project_folder + '/' + molecule):
                    if os.path.isdir(project_folder + '/' + molecule):
                        study_folder = project_folder + '/' + molecule
                        for spectrum in os.listdir(study_folder):
                            if os.path.isdir(study_folder + '/' + spectrum):
                                dataset_folder = study_folder + '/' + spectrum
                                for file in os.listdir(dataset_folder):
                                    if '.zip' in dataset_folder + '/' +file:
                                        try:
                                            with zipfile.ZipFile(dataset_folder + '/' +file, 'r') as zip_ref:
                                                zip_ref.extractall(dataset_folder)
                                            os.remove(dataset_folder + '/' +file)
                                        except:
                                            pass

    for path, directories, files in os.walk("."):
        for file in files:
            if 'zip' in file:
                with zipfile.ZipFile(os.path.join(path, file), 'r') as zip_ref:
                    zip_ref.extractall(path)
                os.remove(os.path.join(path, file))
               
    pass

def get_Bruker_number(innerFolder):
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
    for authors in os.listdir("./"): 
        if os.path.isdir(authors):
            project_folder = os.getcwd() + '/' + authors
            for molecule in os.listdir(project_folder):
                study_folder = project_folder + '/' + molecule
                if os.path.isdir(study_folder):
                    for spectrum in os.listdir(study_folder):
                        if spectrum != '60003332_1H':
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
                                print(target)
                                os.rename(innerFolder, target)
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