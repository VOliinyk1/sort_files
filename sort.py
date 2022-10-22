

import argparse

import os
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description='Sorting folder')
parser.add_argument('--source', '-s', required=True, help='Source folder')
parser.add_argument('--output', '-o', default='Files', help='Output folder')
args = vars(parser.parse_args())
 
source = args.get('source')
output = args.get('output')

source_folder = Path(source)
output_folder = Path(output)

ua_alpha = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"   
eng_translit = ('a','b','v','g','g','d','e','ye','zh','z','y','i','yi','y','k',
    'l','m','n','o','p','r','s','t','u','f','kh','tc','ch','sh','sch','`','yu','ya')*2

tr = {ord(a) : b for a, b in zip(ua_alpha, eng_translit)}
tr.update({ord(a.upper()) : b[0].upper()+b[1:] for a,b in zip(ua_alpha, eng_translit)})

extens = [ ('.JPEG', '.PNG', '.JPG', '.SVG'),
    ('.AVI', '.MP4', '.MOV', '.MKV'),
    ('.DOC', '.DOCX', '.TXT', '.PDF', '.XLSX', '.PPTX'),
    ('.MP3', '.OGG', '.WAV', '.AMR'),
    ('.ZIP', '.TAR')]
    
categories ={0 : 'Images',
                1: 'Video',
                2: 'Documents',
                3: 'Audio',
                4: 'Unknown extensions',
                5: 'Archives',
                }
founded_ext = []
unknown_ext = []

history = {i : [] for i in categories.values()}
history['Unknown'] = []

def normalize(file: Path) -> Path :
    '''Rename files with latin latters, change all symbols except letters and digits to "_" '''
    
    file_name = file.name.removesuffix(file.suffix)
    trans_file = file_name.translate(tr)
    new_file_name = ''.join(ch if ch.isalpha() or ch.isdigit() else '_' for ch in trans_file)
    return Path(str(file).removesuffix(file.name)) / (new_file_name + file.suffix) # returns normalized path

def replace_file(file: Path) -> None:
    '''Distribute files to relative categories.'''

    ext = file.suffix
    new_path = normalize(output_folder)
    norm_file = normalize(file)
    os.rename(file, norm_file)
    
    if ext.upper() in extens[4]:
        founded_ext.append(ext)
        new_path = new_path / 'Archives'
        new_path.mkdir(exist_ok=True, parents=True)
        shutil.unpack_archive(norm_file, new_path / 
                            (norm_file.name.replace(norm_file.suffix,'')))
        os.remove(norm_file)
        history['Archives'].append(norm_file.name)
        
    elif ext.upper() not in ([el for tuple in extens for el in tuple]):
        unknown_ext.append(ext)
        new_path = new_path / 'Unknown extensions'
        new_path.mkdir(exist_ok=True, parents=True)
        os.replace(norm_file, new_path / norm_file.name)
        history['Unknown'].append(norm_file.name)
        
    for i in range(len(extens)-1):
        if ext.upper() in extens[i]:
            founded_ext.append(ext)
            new_path = new_path / categories[i]
            new_path.mkdir(exist_ok=True, parents=True)
            os.replace(norm_file, new_path / norm_file.name)
            history[categories[i]].append(norm_file.name)
                
def read_folder(path: Path) -> dict:
    '''Walk through directories and apply replace_file function to each file in it.  Returns dict with each file in it's category'''

    for file in path.iterdir():
        if file.is_dir() and file not in categories.values():
            read_folder(file)  
        else:
            replace_file(file) 
    return (history, founded_ext, unknown_ext)

def main():
    print(read_folder(source_folder))
    
    # delete empty folders in source folder
    for el in os.listdir(source_folder):
        print(el)
        if el not in list(categories.values()):
            shutil.rmtree(source_folder/el)
    
    
    
        

if __name__ == '__main__':
    main()
    
