'''
Created on Jun 22, 2020

@author: haels
'''
import re

tempo = 60
note_values = {"whole": 4, "half": 2, "quarter": 1, "eight": .5, "sixteenth": .25}

def main():
    #prompt = '>'
    #print('Enter file directory')
    #file_dir = input(prompt).replace('/', "\\")
    file_name = "C:/Users/haels/OneDrive/Documents/Recorder Player/Test.mscx"
    song_str = create_song_string(file_name)
    adjust_tempo(song_str)
    find_notes_and_rests(song_str)
    
def create_song_string(file_name):
    '''Turns input file_name into a string
    Inputs:
        file_name: string containing path directory and name of .mscx file
    Returns:
        song_str: the contents of the .mscx file as a string
    '''
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
    ''' Locates all notes and rests in song_str and extracts the associated
    pitch and length values    
    Inputs:
        song_str: the contents of the .mscx file as a string
    Returns:
        instructions: list of tuples representing notes and rests.
        (int representing index of note, string representing pitch, float
        representing note length)
    '''
    note_indices = [m.start() for m in re.finditer('<Chord>', song_str)]
    rest_indices = [m.start() for m in re.finditer('<Rest>', song_str)]
    instructions = []
    for note_ind in note_indices:
        instructions.append(create_note_tuple(song_str, note_ind))
        
    print()
    
def create_note_tuple(song_str, note_ind):
    ''' Find and put together note index, pitch, and length values as a tuple 
    Inputs:
        song_str: the contents of the .mscx file as a string
        note_ind: the starting index of the note in song_str
    Returns:
        note_tup: a tuple containing: (int representing index of note, 
        string representing pitch, float representing note length)
    '''
    #(index, pitch, length)
    note_tup = (note_ind,)
        
    #extract pitch
    pitch_ind = song_str.find("<pitch>", note_ind)
    pitch_ind_end = song_str.find("</pitch>", note_ind)
    pitch = song_str[pitch_ind+7: pitch_ind_end]
        
    #extract length
    length_ind = song_str.find("<durationType>", note_ind)
    length_ind_end = song_str.find("</durationType>", note_ind)
    length = song_str[length_ind+14: length_ind_end]
    length = note_values[length]
        
    #adjust length by dots if need be
    note_ind_end = song_str.find("</Chord>", note_ind)
    dot_ind = song_str.find("<dots>", note_ind, note_ind_end)
        
    if dot_ind != -1:
        dot_ind_end = song_str.find("</dots>", note_ind)
        dots = int(song_str[dot_ind+6: dot_ind_end])
        #add dot to value
        length = length*1.5*(1/dots)
            
    #concatenate note tuple
    note_tup = note_tup + (pitch,) + (length,)
       
    return note_tup

if __name__ == '__main__':
    main()
    