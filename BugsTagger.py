from urllib.request import urlopen
import eyed3
from mp3_tagger import MP3File
from bs4 import BeautifulSoup
import os
import sys
import ssl

def bugs(burl):
	context = ssl._create_unverified_context()
	filedir = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])+'/downfolder/Album'
	print(filedir)
	file_list = []
	files = os.listdir(filedir)
	for f in files:
		if os.path.isdir(filedir+'/'+f) == False:
			file_list.append(f)

	url = burl
	html = urlopen(url, context=context)
	soup = BeautifulSoup(html, 'html.parser')

	Album_info = soup.find('table', class_='info').find_all('td')
	Album_Title = soup.title.text.replace(' - 벅스','')
	Album_Artists = Album_info[0].find_all('a')
	Album_Artist = ''
	if len(Album_Artists) != 1:
		for aa in Album_Artists:
			Album_Artist += ', ' + aa.text.strip()
			try:
				Album_Artist = Album_Artist.split('(')[0]
			except:
				pass
		Album_Artist = Album_Artist[2:]
	else: 
		Album_Artist = Album_Artists[0].text.strip()
		try:
			Album_Artist = Album_Artist.split('(')[0]
		except:
			pass
	try:
		Album_Artist = Album_Artist.replace('CONNECT 아티스트','')
	except:
		pass
	Album_Artist = Album_Artist.strip()
	print(Album_Artist)
	listnumnum = 0
	if soup.find('table', class_='info').find_all('th')[1].text == '참여 정보':
			listnumnum = 1
	Album_Release_Date = str(Album_info[2+listnumnum].text.strip()).replace('.','-')
	try:
		Album_Release_Date = Album_Release_Date.split("(")[1].replace("원발매","").replace(")","").strip()
	except:
		pass
	Album_Year = Album_Release_Date.split('-')[0]
	Album_Genre = Album_info[3+listnumnum].text.replace(',','/').replace('\n','').strip()
	Album_Art = soup.find('link', rel='image_src')['href']
	response = urlopen(Album_Art, context=context)  
	Album_Art = response.read()
	Album_Comment = str(soup.find('p', id='albumContents')).replace('<br/>','\n')
	Album_Comment = BeautifulSoup(Album_Comment, 'html.parser').text.strip()

	Track_number_list = soup.find_all('p',class_='trackIndex')
	Track_artist_list = soup.find_all('p',class_='artist')
	Track_title_list = soup.find_all('p', class_='title')
	Track_check = soup.find_all('td', class_='check')
	check_cout = 0
	for t_num, t in enumerate(Track_number_list):
		for tt in file_list:
			if tt.find('DS_Store') == 1:
				continue
			if int(tt.split('.')[0]) == t_num + 1:		
				Track_Number = t.find('em').text
				Track_Artists = Track_artist_list[t_num].find_all('a')
				Track_Artist = ''
				if len(Track_Artists) != 1:
					ta = Track_Artists[1]['onclick'].replace("bugs.layermenu.openMultiArtistSearchResultPopLayer(this, '","").replace("', ''); return false;","").split('\\\\')
					for taa in ta:
						Track_Artist += ', ' + taa.split('||')[1].split('(')[0]
					Track_Artist = Track_Artist[2:]
				else: 
					Track_Artist = Track_Artists[0].text.strip()
					try:
						Track_Artist = Track_Artist.split('(')[0]
					except:
						pass
						
				Track_Title = Track_title_list[t_num].find('a').text
				try:
					Track_Disc = Track_check[t_num+check_cout].find('input')['disc_id']
					Track_Vlue = Track_check[t_num+check_cout].find('input')['value']
				except:
					check_cout += 1
					Track_Disc = Track_check[t_num+check_cout].find('input')['disc_id']
					Track_Vlue = Track_check[t_num+check_cout].find('input')['value']
					
				Track_Html = urlopen('https://music.bugs.co.kr/track/'+Track_Vlue, context=context)
				Track_Soup = BeautifulSoup(Track_Html, 'html.parser')

				try:
					Track_Lyric = Track_Soup.find('div', class_="lyricsContainer").find('xmp').text
				except:
					Track_Lyric = ''
			
				file = filedir + '/' + tt
				mp3 = MP3File(file)
				mp3.year = Album_Year
				del mp3.comment, mp3.genre, mp3.album, mp3.artist, mp3.song, mp3.track, mp3.band, mp3.composer, mp3.copyright, mp3.publisher, mp3.url
				mp3.save()
				
				audiofile = eyed3.load(file)
				audiofile.tag.artist = Track_Artist
				audiofile.tag.album = Album_Title
				audiofile.tag.disc_num = int(Track_Disc)
				audiofile.tag.track_num = int(Track_Number)
				audiofile.tag.album_artist = Album_Artist
				audiofile.tag.title = Track_Title
				audiofile.tag.release_date = Album_Release_Date
				audiofile.tag.images.set(3, Album_Art , "image/jpeg" ,u"Spotify")
				audiofile.tag.comments.set(Album_Comment)
				audiofile.tag.genre = Album_Genre
				audiofile.tag.lyrics.set(Track_Lyric)
				audiofile.tag.save()
				
				def nameTrans(s):
					oldChars = '\/:*?"<>|'
					newChars = '_________'
					n = s.translate({ ord(x): y for (x, y) in zip(oldChars, newChars) })
					return n
				newfolder = filedir + '/{}/{} - {} ({})'.format(nameTrans(Album_Artist), nameTrans(Album_Artist), nameTrans(Album_Title), Album_Release_Date.split('-')[0])
				if not os.path.exists(newfolder):
					os.makedirs(newfolder)
				fext = os.path.splitext(file)[1]
				print(check_cout)
				if check_cout == 0:
					newfile = '{}/{}. {}{}'.format(newfolder, str(Track_Number).zfill(2), nameTrans(Track_Title), fext)
				else:
					if not os.path.exists(newfolder+'/CD'+Track_Disc):
						os.makedirs(newfolder+'/CD'+Track_Disc)
					newfile = '{}/CD{}/{}. {}{}'.format(newfolder, Track_Disc, str(Track_Number).zfill(2), nameTrans(Track_Title), fext)
				os.rename(file, newfile)