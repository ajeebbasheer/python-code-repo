import urllib2
import urlparse
from bs4 import BeautifulSoup
import os,sys
import unicodedata
import re #for reg expressions
import StringIO
#from BeautifulSoup import BeautifulSoup          # For processing HTML
#from BeautifulSoup import BeautifulStoneSoup     # For processing XML
#import BeautifulSoup                             # To get everything

#urlin=raw_input("enter url:")
key= raw_input("Enter the key to be searched:")
print "fetching links..............."
print "............................................................................................."
urlmain='http://192.168.4.221'
#urlmain='http://nitc.ac.in'
k=urllib2.urlopen(urlmain)
p=urllib2.urlopen(urlmain)
sp=BeautifulSoup(k)
nam=urlparse.urlparse(urlmain).hostname
g=1
h=1
try:
	os.makedirs('downloadedfiles')
except:
	pass
fh1=open('downloadedfiles/mainpage.html'+nam,"w")
#fh1.write(p.read())
list1=[]
for img in sp.findAll('img'):
	images=img.get('src')
	imgtail=urlparse.urlparse(images)
	print images
	it=imgtail.path+imgtail.params+imgtail.query+imgtail.fragment
	if not imgtail.scheme and not imgtail.netloc:
		realimg=urlparse.urljoin(urlmain,it)
		#print "joined.."
	else:
		realimg=urlparse.urljoin(urls,'')
		#print "this"
			#except:
	
	foldpath=imgtail.path
	length=len(foldpath)
	if foldpath[0]=='/':
		refoldpath=foldpath[1:length]
	else:
		refoldpath=foldpath[0:length]
		#print "downloading......."+refoldpath
	print "downloading image..."+realimg
	try:
		os.makedirs('downloadedfiles/'+refoldpath)	
	except:
		print "aalready exists.."+refoldpath
	try:
		imgobj=urllib2.urlopen(realimg)
	except:
		print"network error..!"
		continue	
	k=realimg.rsplit('/',1)
	
	img_link=open('downloadedfiles/'+refoldpath+'/image'+'_'+str(h)+'_'+'.jpg',"wb")
	img_link.write(imgobj.read())
	img_link.close()
	imgobj.close()
	print os.getcwd()
	img['src']= os.getcwd()+'/downloadedfiles/'+refoldpath+'/image'+'_'+str(h)+'_'+'.jpg'
	#print img['src']
	h=h+1




for links in sp.findAll('a'):	## BeautifulSoup(urllib2.urlopen('url')).findAll('a')
	urls=links.get('href')
	#urls = re.sub(r' ',r'%20',urlall)
	l=len(urls)
	#print urls
	if urls[0]=='/':
		reurl=urls[1:l]
	else:
		reurl=urls[0:l]
	#name=urlparse.urlparse(urls).hostname	#get host names from url
	#sname=urlparse.urlparse(urls).hostname
	fullurl=urlparse.urlparse(reurl)
	
	#fullurl1=fullurl.scheme+fullurl.netloc+fullurl.path+fullurl.params+fullurl.query+fullurl.fragment		
	
	tail=fullurl.path+fullurl.params+fullurl.query+fullurl.fragment

	#print newtail
	#print fullurl.path
	#print fullurl.scheme
	#print fullurl.netloc
	#print tail
	#print urlmain
	#print fold
	#print path1
	if not fullurl.scheme and not fullurl.netloc:
		realurl=urlparse.urljoin(urlmain,tail)
		#print "joined.."
	else:
		realurl=urlparse.urljoin(urls,'')
		#print "this"
	#print realurl
	print "========================================================="
	try:	
		foldpath=fullurl.path
		length=len(foldpath)
		if foldpath[0]=='/':
			refoldpath=foldpath[1:length]
		else:
			refoldpath=foldpath[0:length]
		print "downloading......."+refoldpath
		try:
			os.makedirs('downloadedfiles/'+refoldpath)	
		except:
			print "aalready exists.."+refoldpath
		try:		
			fileobj=urllib2.urlopen(realurl)
		except:
			print"network error..!"
			continue		
		fh_link=open('downloadedfiles/'+refoldpath+'/page'+'_'+str(g)+'_'+'.html',"w")
		string='downloadedfiles/'+refoldpath+'/page'+'_'+str(g)+'_'+'.html'
		list1.append(string)
		g=g+1
		fh_link.write(fileobj.read())
		fh_link.close()	
		fileobj.close()
	except:
		pass


print "Downloading Completed..!"
html = sp.prettify()
#print html
fh1.write(html)
#exit()
fh5=open('out.txt',"w")
for f in list1:
	fh4=open(f,"r")
	s=fh4.read()
	try:
		soup=BeautifulSoup(s)
		asc=StringIO.StringIO(soup.text.encode('utf-8'))
		lines=asc.readlines()
		print "searching"+key+f
		for line in lines:
			#print line
			#print key
			if re.search(key,line,re.I):
				fh5.write(line)
				print "match"
				
		fh4.close()

	except:
		pass
