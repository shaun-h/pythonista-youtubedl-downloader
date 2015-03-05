# coding: utf-8
# author: Shaun Hevey
# youtube-dl downloader is used to download youtube_dl and make it work with pythonista.

import ui
import shutil
import console
import os
import time
import requests
import zipfile
import tempfile

youtubedl_dir = 'youtube_dl'
youtubedl_location = './site-packages/'
backup_location = './backup/youtube_dl/'
youtubedl_downloadurl = 'https://github.com/rg3/youtube-dl/archive/master.zip'
youtubedl_unarchive_location = './youtube-dl-master/'
youtubedl_ui_url = 'https://codeload.github.com/HyShai/youtube-dl/zip/ytdl-pythonista'
youtubedl_ui_extract_path = './youtube-dl-ytdl-pythonista/'
files_to_change = [('utils.py','import ctypes','#import ctypes'),('utils.py','import pipes','#import pipes'),('YoutubeDL.py','self._err_file.isatty() and ',''),('downloader/common.py','(\'\r\x1b[K\' if sys.stderr.isatty() else \'\r\')','\'r\''),('downloader/common.py','(\'\r\x1b[K\' if sys.stderr.isatty() else \'\r\')','\r'),('extractor/common.py',' and sys.stderr.isatty()','')]
                                                                                                                                                                                                                                                  
                                                                                                                                                                                    

def backup_youtubedl(sender):
	console.show_activity('Checking for youtube-dl')
	if os.path.isdir(youtubedl_location+youtubedl_dir):
		console.show_activity('Backing up youtube-dl')
		if not os.path.exists(backup_location):
			os.makedirs(backup_location)
		shutil.move(youtubedl_location+youtubedl_dir,backup_location+youtubedl_dir+ time.strftime('%Y%m%d%H%M%S'))
		
	console.hide_activity()
		
	
def delete_youtubedl_backups(sender):
	return 

@ui.in_background
def restore_youtubedl_backup(sender):
	if not os.path.isdir(backup_location) or len(os.listdir(backup_location))==0:
		console.alert('Nothing to do', 'No backups found to restore')
	else: 
		folders = os.listdir(backup_location)
		folder = folders[len(folders)-1]
		shutil.move(backup_location+folder,youtubedl_location+youtubedl_dir)
		console.alert('Success','Successfully restored '+folder)

def downloadfile(url):
	localFilename = url.split('/')[-1]
	if localFilename == '': localFilename = 'download'
	with open(localFilename, 'wb') as f:
		r = requests.get(url, stream=True)
		total_length = r.headers.get('content-length')
		if not total_length:
			f.write(r.content)
		else:
			dl = 0
			total_length = float(total_length)
			for chunk in r.iter_content(1024):
				dl += len(chunk)
				f.write(chunk)
				#.setprogress(dl/total_length*100.0)
	return localFilename

def process_file(path):
	if zipfile.is_zipfile(path):
		zipfile.ZipFile(path).extractall()

@ui.in_background	
def update_youtubedl(sender):
	if os.path.exists(youtubedl_location+youtubedl_dir):
		if not console.alert('Continue','Are you sure you want to update youtubedl exists in site-packages and will be overwritten','OK'):
			return
	console.show_activity('Downloading')
	file = downloadfile(youtubedl_downloadurl)
	console.show_activity('Extracting')
	process_file(file)
	console.show_activity('Moving')
	if os.path.exists(youtubedl_location+youtubedl_dir):
		shutil.rmtree(youtubedl_location+youtubedl_dir)
	shutil.move(youtubedl_unarchive_location+youtubedl_dir, youtubedl_location)
	
	console.show_activity('Cleaning Up Download Files')
	shutil.rmtree(youtubedl_unarchive_location)
	os.remove(file)
	console.show_activity('Making youtube-dl friendly')
	process_youtubedl_for_pythonista()
	
	console.hide_activity()
		
def process_youtubedl_for_pythonista():
	for file in files_to_change:
		replace(youtubedl_location+youtubedl_dir+'/'+file[0],file[1],file[2])
	

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = tempfile.mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file_path)
    for line in old_file:
    	new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    
    #Remove original file
    os.remove(file_path)
    #Move new file
    shutil.move(abs_path, file_path)

def setup_youtubedl_ui(sender):
	return

#ui.load_view('youtube-dl downloader').present('sheet')
view = ui.View()
view.background_color = 'white'
backup_button = ui.Button(title='Backup YoutubeDL')
backup_button.background_color ='lightgrey'
backup_button.border_color = 'black'
backup_button.border_width = 1
backup_button.center = (view.width * 0.5, view.y+backup_button.height)
backup_button.flex = 'WB'
backup_button.action = backup_youtubedl
view.add_subview(backup_button)

restore_button = ui.Button(title='Restore YoutubeDL')
restore_button.background_color ='lightgrey'
restore_button.border_color = 'black'
restore_button.border_width = 1
restore_button.center = (view.width * 0.5, backup_button.y+restore_button.height*1.75)
restore_button.flex = 'WB'
restore_button.action = restore_youtubedl_backup
view.add_subview(restore_button)

download_button = ui.Button(title='Download YoutubeDL')
download_button.background_color ='lightgrey'
download_button.border_color = 'black'
download_button.border_width = 1
download_button.center = (view.width * 0.5, restore_button.y+download_button.height*1.75)
download_button.flex = 'WB'
download_button.action = update_youtubedl
view.add_subview(download_button)

view.present('sheet')
