import sys
from pathlib import Path
from datetime import datetime

from collections import defaultdict

import wget

from odf.opendocument import load
from odf import text, teletype

skip_words = ['RUNTIME', 'DESCRIPTION', 'Time', 'Title', 'Notes']

# Google Doc ID of the collection of timestamps etc.
# from link https://docs.google.com/document/d/1kA8u6UhjbutZ-b7TXzmX4qkOTg6nGC1vPg50WwCcZyo/
DOC_ID = '1kA8u6UhjbutZ-b7TXzmX4qkOTg6nGC1vPg50WwCcZyo'
# Get the actual PDF doc link
DL_URL = 'https://docs.google.com/document/export?format=odt&id=' + DOC_ID
# Location of file
# DL_PATH = Path('downloads') / ('minidiscs_' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.odt')

# print('Beginning download of Google Doc...')
# wget.download(DL_URL, str(DL_PATH))
# print('\nFile downloaded at ' + str(DL_PATH))

def is_time(line):
    allowed = set('1234567890:')
    if set(line).issubset(allowed):
        return True
    return False


def clean_file(file_path):
    doc = load(file_path)
    texts = doc.getElementsByType(text.P)
    s = len(texts)
    started = False

    line_items = []
    for i in range(s):
        line = teletype.extractText(texts[i])
        if 'END OF MINIDISCS' in line:
            break
        if not started and 'DISC 1' in line:
            started = True
        if started and line and not any(a_word in line for a_word in skip_words):
            line_items.append(line)

    return line_items

'''
    Extract text from file at path into dict for cue-file writing
'''
def extract_text(file_path):
    clean_lines = clean_file(file_path)

    cue_dict = defaultdict(list)
    md_num = 110
    current_disc = 0
    seeking = False

    i = 0
    while i < len(clean_lines):
        if 'DISC' in clean_lines[i]:
            print(clean_lines[i])
            current_disc += 1
            md_num += 1
            i += 1
        if is_time(clean_lines[i]):
            time = clean_lines[i]
            print(time)
            title = clean_lines[i + 1]
            print(title)
            cue_dict['MD'+str(md_num)].append([time, title])
            if (i + 2 < len(clean_lines)) and (not ':' in clean_lines[i + 2]):
                i += 3
            else:
                i += 2
        else:
            i += 1
    return cue_dict

'''
    Create and write cue file into main directory from cue dictionary
    FLAC naming scheme: Radiohead - MINIDISCS -HACKED- - 01 MD111
'''
def write_cue(cue_dict):
    # get disc name from disc number
    def f_num(num):
        if num < 10:
            return '0' + str(num)
        return str(num)

    def f_time(t):
        if t.count(':') < 2:
            t += ':00'
        return t

    disc_num = 1
    for disc in cue_dict.keys():
        with open('cues/' + disc + '.cue', 'w') as f:
            # begin writing to cue file
            f.write('REM GENRE ROCK\nREM DATE 2019\nPERFORMER Radiohead\nTITLE '+ disc + '\nFILE ' + 'Radiohead - MINIDISCS -HACKED- - ' + f_num(disc_num) + ' ' + disc + '\n')
            for i, track_info in enumerate(cue_dict[disc]):
                time = track_info[0]
                title = track_info[1]
                if ('- ' in title):
                    title = title.split('- ', 1)[1]
                    if (':' in title):
                        title = title.split(' ', 1)[1]

                f.write('  TRACK ' + f_num(i+1) + ' AUDIO\n')
                f.write('    TITLE ' + '"' + title + '"\n')
                f.write('    PERFORMER ' + '"Radiohead"\n')
                f.write('    INDEX ' + f_num(1) + ' ' + f_time(time) + '\n')

            disc_num += 1
        break

write_cue(extract_text(DL_PATH))

