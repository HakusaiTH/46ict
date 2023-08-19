from googletrans import Translator
import openai
import requests
from playsound import playsound
import wave, struct
from pydub import AudioSegment
from pydub.playback import play
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
# import cv2
import numpy as np
from datetime import datetime
from multiprocessing import Process
import speech_recognition as sr

from tkinter import *
from tkinter.scrolledtext import ScrolledText
import speech_recognition as sr
import threading

import os
import time

'''
from dotenv import load_dotenv

load_dotenv()
'''

cred = credentials.Certificate('D:\\ubon-project\\tomodachi\\ai-chan-3074e-firebase-adminsdk-8sgnr-694671ceac.json')
firebase_admin.initialize_app(cred, {'databaseURL': 'https://ai-chan-3074e-default-rtdb.asia-southeast1.firebasedatabase.app/'})

# OpenAI
# openai.api_key = "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"
openai.api_key = "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"
model_engine = "text-davinci-003"

# GUI
root = Tk()

root.geometry("900x600")
root.resizable(False, False)

icon_img = PhotoImage(file="D:\\ubon-project\\tomodachi\\img\\n.png")
root.iconphoto(False, icon_img)

root.title("Yokai Watch")
image = PhotoImage(file="D:\\ubon-project\\tomodachi\\img\\n.png") # D:\168-education-main\ai\img\n.png

label = Label(root, image=image)

text1 = ScrolledText(root, width=40, height=10, font=("Helvetica", 12),
                     bg="white", insertbackground="black", wrap="word")

vsb1 = Scrollbar(root, orient="vertical", command=text1.yview)
text1.configure(yscrollcommand=vsb1.set)

label.pack(side="left", padx=5, pady=5)
text1.pack(side="top", fill="both", expand=True, padx=5, pady=5)
vsb1.pack(side="right", fill="y")

def update_image(img):
    image.configure(file=img)

def play_sound(sound_file): 
    threading.Thread(target=play, args=(sound_file,)).start()


'''
def control_led(led_sta) :
    led_ref = db.reference('/led')
    led_ref.set(led_sta)
    print("set to",led_sta)
'''

def set_led(user_text) :
    '''
    if user_text == "เปิดไฟ" or user_text == "ปิดไฟ":
        led_sta = 1 if user_text == "เปิดไฟ" else 0 # 0 is off, 1 is on

        gui_text = ( f'User : {user_text} \n'
            f'Sensei : กำลัง{user_text} \n' )
        
        update_image("D:\\ubon-project\\tomodachi\\img\\h.png") 
        control_led(led_sta)
    
    '''
    if user_text == "ตรวจจับควัน" or user_text == "พบผุ้บุกรุก":  # ตรวจจับควัน    พบผุ้บุกรุก

        gui_text = ( f'User : ( {user_text} ) \n'
            f'Sensei : {user_text}ได้ในขณะนี้ \n' )
        
        update_image("D:\\ubon-project\\tomodachi\\img\\s.png")

    set_sound = AudioSegment.from_wav(f'{user_text}.wav')
    play_sound(set_sound)

    text1.insert(END, gui_text)
    text1.see(END)
    time.sleep(3)

def start_recording():
    # spech to text
    r = sr.Recognizer()
    beep_sound = "D:\\ubon-project\\tomodachi\\signal.mp3"
    with sr.Microphone() as source:

        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="th-TH")
        process_user_input(text)  # Pass the recognized text as user_input            
    except:
        print("not recognize")
    
    # iot 
    '''
    text = str(input("input :"))
    if "เปิดไฟ" in text:
        set_led("เปิดไฟ")
    elif "ปิดไฟ" in text:
        set_led("ปิดไฟ")
    else :
        process_user_input(text)  # Pass the recognized text as user_input
    
    '''

    '''
    text = str(input("input :"))
    process_user_input(text)  # Pass the recognized text as user_input
    '''


button = Button(root, text="Submit", command=start_recording)
button.pack(side="bottom", padx=5, pady=5)

def translate(user_input, la):
    translator = Translator()
    translation = translator.translate(user_input, dest=la)
    return translation.text

def update_text(user_input):
    prompt = translate(user_input, 'en')

    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response = completion.choices[0].text
    response_output = translate(response, 'th')
    print(user_input, response_output)
    
    # vaja 
    url_vaja = 'https://api.aiforthai.in.th/vaja'
    headers_vaja = {'Apikey':'If66yNxYjCF1T5XtBgQ3k9VczUbHJn51','Content-Type' : 'application/x-www-form-urlencoded'}
    params_vaja = {'text':response_output,'mode':'st'}
    response_vaja = requests.get(url_vaja, params=params_vaja, headers=headers_vaja).json()

    result = response_vaja["output"]["audio"]["result"]
    numChannels = response_vaja["output"]["audio"]["numChannels"]
    validBits = response_vaja["output"]["audio"]["validBits"]
    sizeSample = response_vaja["output"]["audio"]["sizeSample"]
    sampleRate = response_vaja["output"]["audio"]["sampleRate"]

    audio_file_path = 'D:\\ubon-project\\tomodachi\\audio\\sound.wav'

    obj = wave.open('sound.wav', 'wb') 
    obj.setparams((1, int(validBits/8), sampleRate, 0, 'NONE', 'not compressed'))
    for i in range(sizeSample):
        value = int(result[i])
        data = struct.pack('<h', value)  
        obj.writeframesraw(data)
    obj.close()

    sound = AudioSegment.from_wav('sound.wav')

    # sen
    url_sen = "https://api.aiforthai.in.th/ssense" 
    params_sen = {'text':response_output}
    headers_sen = {
        'Apikey': "If66yNxYjCF1T5XtBgQ3k9VczUbHJn51"
    }
    response_sen = requests.get(url_sen, headers=headers_sen, params=params_sen).json()
    polarity_score = response_sen['sentiment']['polarity']

    if polarity_score == 'negative':
        # D:\ubon-project\tomodachi\img
        update_image("D:\\ubon-project\\tomodachi\\img\\s.png")
    elif polarity_score == 'positive':
        update_image("D:\\ubon-project\\tomodachi\\img\\h.png")
    else:
        polarity_score = 'neutral'
        update_image("D:\\ubon-project\\tomodachi\\img\\n.png")

    text1.insert(END, f'User : {user_input} \n'
                     f'Sensei : {response_output} \n')
    text1.see(END)
    play_sound(sound)

def process_user_input(user_input):
    t = threading.Thread(target=update_text, args=(user_input,))
    t.start()


# Read data from status.txt file
def read_status_from_file():
    try:
        with open('status.txt', 'r') as status_file:
            status_data = status_file.read()
            return int(status_data.strip())  # Convert the read data to an integer
    except FileNotFoundError:
        return None  # Return None if the file is not found


def check_data():
    '''
    smoke_ref = db.reference('/smoke')
    smoke_data = smoke_ref.get()
    '''

    # Example usage
    alert_data = read_status_from_file()

    '''
    if smoke_data == 1 :
        print("smoke is on !")
        set_led("ตรวจจับควัน")
    '''

    if alert_data == 1 :
        print("alert is on !")
        set_led("พบผุ้บุกรุก")      


    root.after(1000, check_data)

# Call the check_data function to start the loop
check_data()

# Start the main Tkinter event loop
root.mainloop()
