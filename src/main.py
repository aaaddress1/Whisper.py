from datetime import timedelta
import os, subprocess, whisper, hashlib, sys, shutil
currPath = os.path.dirname(os.path.abspath(__file__))
path2ffmpeg = os.path.join( currPath, "ffmpeg.exe" )
if not os.path.isfile( path2ffmpeg ):
    print("[!] 您的 FFMPEG.EXE 文件是否丟失？")
    os._exit(-1)

def transcribe_audio(path):
    # https://github.com/openai/whisper/discussions/3
    model = whisper.load_model("base") # Change this to your desired model
    print("Whisper model loaded.")
    transcribe = model.transcribe(audio=path)
    segments = transcribe['segments']
    ret = []
    for segment in segments:
        startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
        endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
        text = segment['text']
        segmentId = segment['id']+1
        segment = f"[#{segmentId}][{startTime} --> {endTime}] {text[1:] if text[0] == ' ' else text}"
        ret.append(segment)
    return ret

def transform_video_toText(file) -> []:

    try:
            
        if not os.path.isfile( file ):
            print(f"[!] 您想轉換逐字稿的文件 {file} 不存在嗎？")
            return []

        pathTo_tempWAV = hashlib.md5( file.encode() ).hexdigest() + ".wav"

        if not os.path.isfile( pathTo_tempWAV ):
            subprocess.check_output( [path2ffmpeg, "-i", file, "-ar", "16000", pathTo_tempWAV] )
            if not os.path.isfile( pathTo_tempWAV ):
                print(f"[!] FFMPEG 轉換過程出錯 :(")
                return []

        ret = transcribe_audio(pathTo_tempWAV)
        shutil.rmtree( pathTo_tempWAV, ignore_errors=True)
        return ret
    except Exception as e:
        statusRichText.insert(END, f"[ERROR] 異常錯誤... {str(e)}")
        return []
    
import threading

import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog
import tkinter.ttk, easygui
from tkinter.constants import *
from tkinter import messagebox
import time

def selectPhotoFolder():
    outputDir = easygui.diropenbox("字幕存放資料夾")
    output_dir.delete(0, 'end')
    output_dir.insert(0, outputDir)

def selectAudioFile():
    paths = filedialog.askopenfilenames()
    for path in paths:
        displayAudioFilePath.insert(END, path)


def workerMain():
    start = time.time()
    total_count = (displayAudioFilePath.size())
    dir_to_output = output_dir.get()
    
    for i in range(total_count):
        path = displayAudioFilePath.get(i)
        textfile_to_output = os.path.join(dir_to_output, os.path.basename(path).split(".")[0] + ".txt")
        statusRichText.insert(END, f"[{i+1}/{total_count}] 處理文件 - {os.path.basename(path)}")
        ret = transform_video_toText(path)
        if len(ret) < 1:
            statusRichText.insert(END, f"[{i+1}/{total_count}][ER] 轉換失敗 QQ")
        else:
            with open(textfile_to_output, "w") as fp:
                fp.write('\n'.join(ret))
                statusRichText.insert(END, f"[{i+1}/{total_count}][OK] 完成! 逐字稿保存於 {os.path.basename(textfile_to_output)}")
    end = time.time()
    messagebox.showinfo(title="訊息", message="處理完成\n花費時間%.2f秒"%(end-start))
    processButton['state'] = 'normal'

def process():
    if displayAudioFilePath.size() == 0:
        messagebox.showerror(title="錯誤", message='未選擇音檔')
        return 0
    processButton['state'] = 'disabled'
    t=threading.Thread(target=workerMain, args=())
    t.start()

heightFix_1 = 70

window = tk.Tk()
window.title('Whisper.py - by aaaddress1@chroot.org')
window.geometry('580x250')
window.resizable(False, False)

label1 = tk.Label(text='選取影音檔')
label1.place(x=0, y=10)
displayAudioFilePath = tk.Listbox(width=60, height=5)
displayAudioFilePath.place(x=80, y=10)
selectAudioFileButton = ttk.Button(text='＋添加', command=selectAudioFile)
selectAudioFileButton.place(x=510, y=20)
selectAudioFileButton = ttk.Button(text='－刪除', bootstyle='danger', command=lambda x=displayAudioFilePath: x.delete("active"))
selectAudioFileButton.place(x=510, y=50)



label2 = tk.Label(text='輸出逐字稿存放路徑')
label2.place(x=0, y=30+heightFix_1)
output_dir = tk.Entry(width=55)
output_dir.place(x=120, y=30+heightFix_1)
output_dir.insert(0, os.getcwd() + "\\output")
selectPhotoPathButton = tk.Button(text='....', command=selectPhotoFolder)
selectPhotoPathButton.place(x=500, y=30+heightFix_1)

statusRichText = tk.Listbox(width=580,height=10)
statusRichText.place(x=0, y=60+heightFix_1)
statusRichText.insert(END, "W̶h̶i̶s̶p̶e̶r̶.̶p̶y̶")
statusRichText.insert(END, "github.com/aaaddress1/Whisper.py")
statusRichText.insert(END, " --\n\n")

processButton = tk.Button(text='生成逐字稿', width=20, command=process)
processButton.place(anchor='center', x=290, y=160+heightFix_1)

window.mainloop()