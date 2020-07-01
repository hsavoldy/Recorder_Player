'''
Created on Jun 22, 2020

@author: hsavoldy
'''
import re
import serial, time

#arduino_port = 'COM5'
tempo = 60
length_values = {"whole": 4, "half": 2, "quarter": 1, "eighth": .5, "sixteenth": .25}
note_encodings = {'78': 'a', '77': 'b', '76': 'c', '75': 'd', '74': 'e', '73': 'f', '72': 'g', '71': 'h', 
                  '70': 'i', '69': 'j', '68': 'k', '67': 'l', '66': 'm', '65': 'n', '64': 'o', '63': 'p', 
                  '62': 'q', '61': 'r', '60': 's', 'rest': 't'}

def main():
    #prompt = '>'
    #print('Enter file directory')
    #file_dir = input(prompt).replace('/', "\\")
    file_name = "C:/Users/haels/OneDrive/Documents/Recorder Player/Test.mscx"
    song_str = create_raw_song_string(file_name)
    adjust_tempo(song_str)
    arduino_str = find_notes_and_rests(song_str)
    send_to_arduino("COM5", arduino_str)
    
def create_raw_song_string(file_name):
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
        instructions: string containing notes and rests in order. Two values for 
        each note: note pitch and length value
    '''
    note_indices = [m.start() for m in re.finditer('<Chord>', song_str)]
    rest_indices = [m.start() for m in re.finditer('<Rest>', song_str)]
    instructions = []
    
    for note_ind in note_indices:
        instructions.append(create_note_tuple(song_str, note_ind))
        
    for rest_ind in rest_indices:
        instructions.append(create_rest_tuple(song_str, rest_ind))
    
    #sort by index so that notes and rests are in order
    instructions.sort(key=lambda tup: tup[0])
    
    instructions = [ i[1]+str(i[2]) for i in instructions]
    
    return ''.join(instructions)
    
def create_rest_tuple(song_str, rest_ind):
    ''' Find and put together rest index, pitch (None for rest), and 
    length values as a tuple 
    Inputs:
        song_str: the contents of the .mscx file as a string
        note_ind: the starting index of the note in song_str
    Returns:
        note_tup: a tuple containing: (int representing index of note, 
        string representing pitch, float representing note length)
    '''
    #(index, pitch, length)
        
    length = find_length(song_str, rest_ind, False)
    pitch = 't'
        
    rest_tup = (rest_ind, pitch, length) 
    return rest_tup

    
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
        
    length = find_length(song_str, note_ind, True)
    pitch = find_pitch(song_str, note_ind)
        
    note_tup = (note_ind, pitch, length) 
    return note_tup

def find_length(song_str, note_ind, note):
    ''' Find note/rest length, including dots
    Inputs:
        song_str: the contents of the .mscx file as a string
        note_ind: the starting index of the note in song_str
        note: boolean that is True if it is a note and False if it is a rest
    Returns:
        length: float representing how many beats the note/rest gets
    '''
    #extract length
    length_ind = song_str.find("<durationType>", note_ind)
    length_ind_end = song_str.find("</durationType>", note_ind)
    length = song_str[length_ind+14: length_ind_end]
    length = length_values[length]
        
    #adjust length by dots if need be
    if note:
        note_ind_end = song_str.find("</Chord>", note_ind)
    else:
        note_ind_end = song_str.find("</Rest>", note_ind)
    dot_ind = song_str.find("<dots>", note_ind, note_ind_end)
        
    if dot_ind != -1:
        dot_ind_end = song_str.find("</dots>", note_ind)
        dots = int(song_str[dot_ind+6: dot_ind_end])
        #add dot to value
        length = length*1.5*(1/dots)
            
    return length

def find_pitch(song_str, note_ind):
    ''' Find note pitch
    Inputs:
        song_str: the contents of the .mscx file as a string
        note_ind: the starting index of the note in song_str
    Returns:
        pitch: character representing the pitch of the note (identifiable by Arduino code)
    '''
    #extract pitch
    pitch_ind = song_str.find("<pitch>", note_ind)
    pitch_ind_end = song_str.find("</pitch>", note_ind)
    pitch = song_str[pitch_ind+7: pitch_ind_end]
    encoded_pitch = note_encodings[pitch]
    return encoded_pitch

def send_to_arduino(arduino_port, arduino_str):
    ''' Sends a string of pitch values and lengths to the arduino to 
    be played by recorder
    Inputs:
        arduino_port: string containing the current port connecting 
            the arduino to the machine. example: "COM5"
        arduino_str: string containing encoded pitch value followed 
            by length value for every note in the file.
            example: whole note E followed by half note D: "a4c2"
    '''
    arduino = serial.Serial(arduino_port, 115200, timeout=None)
    time.sleep(1)
    arduino_bytes = bytes(arduino_str, 'utf-8')

    arduino.write(arduino_bytes)
    print('Sending song to arduino...')
    arduino.close()
    print('Processing on arduino...')

if __name__ == '__main__':
    main()
    