import subprocess
import threading
import asyncio
import qrcode
import shutil
import os
import sys

def get_mime(ext): 
    MIME_TYPE = {
        'txt': 'text/plain',
        'csv': 'text/csv',
        'log': 'text/plain',
        'md': 'text/markdown',
        'py': 'text/x-python',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'xml': 'application/xml',
        'java': 'text/x-java-source',
        'php': 'application/x-httpd-php',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'svg': 'image/svg+xml',
        'tiff': 'image/tiff',
        'ico': 'image/x-icon',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'flac': 'audio/flac',
        'aac': 'audio/aac',
        'mp4': 'video/mp4',
        'mkv': 'video/x-matroska',
        'webm': 'video/webm',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        'exe': 'application/octet-stream',
        'iso': 'application/x-iso9660-image',
        'apk': 'application/vnd.android.package-archive',
        'ttf': 'font/ttf',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'csv': 'text/csv',
        'ics': 'text/calendar',
        'epub': 'application/epub+zip',
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'm4a': 'audio/mp4',
        'aac': 'audio/aac',
        'flac': 'audio/flac',
        'weba': 'audio/webm',
        'amr': 'audio/amr',
        'opus': 'audio/opus',
      }

    return MIME_TYPE.get(ext, 'application/octet-stream')
    
def printQr(qr_code_url):
    qr = qrcode.QRCode()
    qr.add_data(qr_code_url)
    qr.make()
    qr.print_ascii(invert=True) 

def generate_qr(data, filename='qr.png'):
    qr = qrcode.QRCode(
        version=1, 
        error_correction=qrcode.constants.ERROR_CORRECT_L, 
        box_size=8,  
        border=1,)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(filename)
    return filename

class WAClient:
    def __init__(self):
        self.__process = None
        self.__loop = asyncio.get_event_loop()
        
    def __read_output(self):
        while True:
            output = self.__process.stdout.readline()
            if output:
                out = output.strip()
                if out.startswith("TG_TIGGER"):
                    data = out.replace("TG_TIGGER:","")
                    asyncio.run_coroutine_threadsafe(self.__trigger_async_function(data), self.__loop)
                else:
                    print(out)
            if self.__process.poll() is not None:  
                error = self.__process.stderr.readline()
                if error:
                    print(f'Error from Node.js: {error.strip()}')

    async def polling(self):
        self.__process = subprocess.Popen(
            args=['node','index.js'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=subprocess.PIPE,
            text=True
            )
        await asyncio.sleep(5)
        self.__read_thread = threading.Thread(target=self.__read_output)
        self.__read_thread.start()
    
    async def __do_post__(self,command,data):
        command = f"{command}|{data}"
        if self.__process.stdin:
            self.__process.stdin.write(command)  
            self.__process.stdin.flush()
        await asyncio.sleep(1)

    async def __trigger_async_function(self, data: str):
        if data.startswith('QR'):
            qr_data= data.replace('QR:','')
            printQr(qr_data)

        if data.startswith('Connected'):
            print("Connected")

        if data.startswith('Logged'):
            print("logout")
            try:
                for item in os.listdir("auth"):
                    item_path = os.path.join("auth", item)
                    shutil.rmtree(item_path) if os.path.isdir(item_path) else os.remove(item_path)
                os.execl(sys.executable, sys.executable, *sys.argv)
            except:pass

    async def send_message(self,chat_id: str,text: str):
        command = "sendMessage"
        data = f"{chat_id},{text}"
        await self.__do_post__(command,data)

    async def send_image(self,chat_id,Image_url,caption):
        command = "sendImage"
        data = f"{chat_id},{Image_url},{caption}"
        await self.__do_post__(command,data)

    async def send_document(self,chat_id: str,FilePath: str,caption: str):
        command = "sendDocument"
        fileName = str(FilePath).split('/')[-1] if '/' in str(FilePath) else FilePath
        extention = fileName.split(".")[-1]
        mimeType = get_mime(extention)
        data = f"{chat_id},{FilePath},{fileName},{mimeType},{caption}"
        await self.__do_post__(command,data)

    async def send_video(self,chat_id,video,caption):
        command = "sendVideo"
        data = f"{chat_id},{video},{caption}"
        await self.__do_post__(command,data)

    async def send_audio(self,chat_id: str,audio: str,send_as_voice: bool = False):
        command = "sendVoice" if send_as_voice else "sendAudio"
        extention = audio.split('.')[-1]
        mimeType = get_mime(extention)
        data = f"{chat_id},{audio},{mimeType}"
        await self.__do_post__(command,data)

    async def send_sticker(self,chat_id: str,sticker: str):
        command = "sendSticker"
        data = f"{chat_id},{sticker}"
        await self.__do_post__(command,data)
