from HTMLParser import HTMLParser
import urllib2
import argparse
import subprocess
import os

class MusicParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.songlinks = []
        self.tag=""
        self.attrs=[]

    def mark_link(self,tag,attrs):
        if (tag == 'a'):
            #attrs is a list of name,value pairs
            link = [value for(key,value) in attrs if(value.endswith('mp3'))]
            return link

    def handle_starttag(self,tag,attrs):
        #if it is an anchor tag, whose href points to an mp3 file, then store
        link = self.mark_link(tag,attrs)
        if (link != None  and len(link) != 0):
            self.songlinks.extend(link)
    
    def handle_data(self,data):
        link = self.mark_link(self.tag,self.attrs)
        if (link != None and len(link) != 0):
            print data
        
def command_line_parse():
    parser = argparse.ArgumentParser(description="parses the website name")
    parser.add_argument('-s','--site',help="web page which contains mp3 songs which you want to download",default="http://tamilmp3world.com")
    parser.add_argument('-p','--path',help="part of the url following the site url",default="")
    args = parser.parse_args()
    return args
    
def download_music(site,path):
    parser=MusicParser()
    filepath = os.path.join('/home/sriram/Music',path)
    if (os.path.exists(filepath)):
        print 'Folder : ' + path + ' already exists, so not downloading'
        return
    else:
        os.makedirs(filepath)
    sitepath = site + '/' + path.strip() + '.html'
    resp=urllib2.urlopen(sitepath)
    data=resp.read()
    html = str(data)
    parser.feed(html)
    ua='"User-Agent:Chromium/17.0.963.79"'
    cmd = 'curl -#v -o {0} -H {1} {2}'
    for link in parser.songlinks:
        encodedlink = urllib2.quote(link,safe="/:")
        musicpath = os.path.join(filepath.strip(),urllib2.quote(link.split('-')[-1].strip()))
        command = cmd.format(musicpath,ua,encodedlink.strip())
        print command
        subprocess.call(command,shell=True)

if __name__ == '__main__':
    args = command_line_parse()
    site = args.site
    if (args.path == ""):
        f=open('/home/sriram/songs-needed','r')
        path_list=f.readlines()
        for path in path_list:
            download_music(site,path.strip())
    else:
        download_music(site,args.path)
    
