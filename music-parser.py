from HTMLParser import HTMLParser
import urllib2
import argparse
import subprocess
import os

"""
This class takes care of parsing the HTML document and figuring
out the anchor elements in the file.
"""
class MusicParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.song_mp3_link_dict = {}
        self.songlinks = []
        self.tag=""
        self.attrs=[]

    def check_if_mp3_link(self,tag,attrs):
        if (tag == 'a'):
            #attrs is a list of name,value pairs
            link = [value for(key,value) in attrs if(value.endswith('mp3') and value.strip().startswith('http'))]
            return link

    def handle_starttag(self,tag,attrs):
        #if it is an anchor tag, whose href points to an mp3 file, then store
        link = self.check_if_mp3_link(tag,attrs)
        if (link != None  and len(link) != 0):
            self.songlinks.extend(link)
    
    def handle_data(self,data):
        link = self.check_if_mp3_link(self.tag,self.attrs)
        if (link != None and len(link) != 0):
            print "data is %s" % data
            self.song_mp3_link_dict[data] = self.link

    #these would serve as the interface methods for this class
    def get_mp3_map(self):
        return self.song_mp3_link_dict
        
def command_line_parse():
    parser = argparse.ArgumentParser(description="Utility script which either downloads" + 
        "all mp3 files in the link specified by the s and p options or reads the secondary url options from" +
        "a file")

    parser.add_argument('-s','--site',help="web page which contains mp3 songs which you want to download",default="http://tamilmp3world.com")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-p','--path', help="part of the url following the site url",default="")
    group.add_argument('-i','--input',help="file from which we need to get the input, every top level input which we want to" +
    " parse for mp3 urls must be given as a single line in the file.  This option and the -p option are mutually exclusive",default=".")
    parser.add_argument('-t','--dir', help="directory where we store our downloaded files",default="~/Music")
    args = parser.parse_args()
    return args
    
def download_music(site,path,filepath):
    parser=MusicParser()
    filepath = os.path.join(filepath,path)
    if (os.path.exists(filepath)):
        print 'Folder : ' + path + ' already exists, so not recreating'
    else:
        os.makedirs(filepath)
    sitepath = site + '/' + path.strip() + '.html'
    resp=urllib2.urlopen(sitepath)
    data=resp.read()
    html = str(data)
    parser.feed(html)
    ua='"User-Agent:Chromium/17.0.963.79"'
    cmd = 'curl -L -#v -O -H {0} {1}'
    #move all mp3 files which are downloaded (currently we blindly move all mp3 files)
    movecmd = 'mv *.mp3 {0}'.format(filepath)
    song_link_map = parser.get_mp3_map()
    print song_link_map
    print parser.songlinks
    for link in parser.songlinks:
    #for link in song_link_map.keys():
        link = link.strip()
        print link
        encodedlink = urllib2.quote(link,safe="/:")
        command = cmd.format(ua,encodedlink.strip())
        print command
        subprocess.call(command,shell=True)
    subprocess.call(movecmd,shell=True)

if __name__ == '__main__':
    args = command_line_parse()
    site = args.site.strip()
    if site == None or site == "":
        print "Site name not given, unable to proceed further"
        exit()

    if (args.dir != '~/Music'):
        filepath = args.dir
    else:
        filepath = os.path.expanduser(args.dir)
    if (args.input != "."):
        f=open(args.input,'r')
        path_list=f.readlines()
        for path in path_list:
            download_music(site,path.strip(),filepath)
    else:
        download_music(site,args.path,filepath)    
