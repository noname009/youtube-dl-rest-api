import schedule
import time
import subprocess
import os

MY_SC_TIME = os.environ['MY_SC_TIME']
update = subprocess.run(['pip', 'install', '--upgrade', 'pip'])
def job():
    update = subprocess.run(['pip', 'install', '--upgrade', 'youtube-dl'])

schedule.every().day.at(MY_SC_TIME).do(job)

while True:
    schedule.run_pending()
    time.sleep(1)