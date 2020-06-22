'''
Created on Jun 22, 2020

@author: haels
'''
import re

tempo = 60

def main():
    #prompt = '>'
    #print('Enter file directory')
    #file_dir = input(prompt).replace('/', "\\")
    file_name = "C:/Users/haels/OneDrive/Documents/Recorder Player/Test.mscx"
    song_str = create_song_string(file_name)
    adjust_tempo(song_str)
    
def create_song_string(file_name):
    file_object  = open(file_name, 'r')
    song_str = file_object.read();
    return song_str

def adjust_tempo(song_str):
    '''Searches song_str for "<tempo>" mark and uses the extracted multiplier
    to adjust the global tempo
    Inputs:
        song_str: the contents of the .mscx file as a string
    '''
    global tempo
    index = song_str.find("<tempo>")
    if index != -1:
        end_index = song_str.find("</tempo>")
        tempo_multiplier = float(song_str[index+7:end_index])
        tempo = round(tempo*tempo_multiplier)

def find_notes_and_rests(song_str):
    notes = [m.start() for m in re.finditer('<Chord>', song_str)]
    rests = [m.start() for m in re.finditer('<Rest>', song_str)]
    print()

if __name__ == '__main__':
    main()
    