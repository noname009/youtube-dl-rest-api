from flask_restful import Resource
from flask_restful import reqparse
from flask import Flask
from flask_restful import Api
import subprocess
import threading
import os
from queue import Queue
from BugsTagger import bugs

flist = ['Album', 'Video', 'MP3']
for mlist in flist:
    if not(os.path.isdir('downfolder/' + mlist)):
                os.makedirs(os.path.join('downfolder/' + mlist))
else:
    pass

class Youtube_rest(Resource):
    def get(self):
        try:
            my_id = os.environ['MY_ID']
            my_pw = os.environ['MY_PW']
            my_lang = os.environ['MY_LANG']
            parser = reqparse.RequestParser()
            parser.add_argument('url', required=True, type=str)
            parser.add_argument('id', required=True, type=str)
            parser.add_argument('pw', required=True, type=str)
            parser.add_argument('youid', type=str)
            parser.add_argument('youpw', type=str)
            parser.add_argument('yousub', type=str)
            parser.add_argument('youresol', type=str)
            parser.add_argument('youalbum', type=str)
            parser.add_argument('bugs', type=str)

            args = parser.parse_args()
            uurl = ["youtube-dl", "-o", "./downfolder/.incomplete/%(title)s.%(ext)s"]
            if args['id'] == my_id and args['pw'] == my_pw:
                if args['youid'] != None:
                    uurl.append('-u')
                    uurl.append(args['youid'])
                if args['youpw'] != None:
                    uurl.append('-p')
                    uurl.append(args['youpw'])
                if args['yousub'] == 'True':
                    uurl.append('--write-sub')
                    uurl.append('--sub-lang')
                    uurl.append(my_lang)
                if args['youresol'] == 'Audio':
                    uurl.append('--extract-audio')
                    uurl.append('--audio-format')
                    uurl.append('mp3')
                if args['youalbum'] == 'Yes':
                    uurl = ["youtube-dl", "-o", "./downfolder/.incomplete/%(playlist_index)s.%(track)s.%(ext)s", "--extract-audio", "--audio-format", "mp3"]
                    if args['youid'] != None:
                        uurl.append('-u')
                        uurl.append(args['youid'])
                    if args['youpw'] != None:
                        uurl.append('-p')
                        uurl.append(args['youpw'])
                uurl.append('--exec')
                if args['youalbum'] == 'Yes':
                    uurl.append('touch {} && mv {} ./downfolder/Album/')
                elif args['youresol'] == 'Audio':
                    uurl.append('touch {} && mv {} ./downfolder/MP3/')
                else:
                    uurl.append('touch {} && mv {} ./downfolder/Video/')
                uurl.append(args['url'])
                print(uurl)
                dl_q.put(uurl)
                if args['bugs'] != None:
                   dl_q.put(args['bugs'])
        except Exception as e:
            return {'error': str(e)}

def down_start():
    while not done:
        item = dl_q.get()
        try:
            if item.find('bugs.co.kr') != -1:
                bugs(item)
            else:
                a = subprocess.run(item)
        except:
            a = subprocess.run(item)
        
        dl_q.task_done()

class Thr:
    def __init__(self):
        self.dl_thread =''
    def restart(self):
        self.dl_thread = threading.Thread(target=down_start)
        self.dl_thread.start()

app = Flask('Youtube DL Rest Api')
api = Api(app)
api.add_resource(Youtube_rest, '/yourest')

if __name__ == '__main__':
    dl_q = Queue()
    done = False
    Thr.dl_thread = threading.Thread(target=down_start)
    Thr.dl_thread.start()
    app.run(host='0.0.0.0', port=4287)
    done = True
    Thr.dl_thread.join()