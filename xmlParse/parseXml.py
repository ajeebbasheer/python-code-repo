from xml.dom import minidom

xmldoc = minidom.parse("books.xml") #the whole xml is read now.

#book = xmldoc.getElementsByTagName("book")[0] #returns a list that all tags that match a tag 'book'.
# ("book")[0]  - first element of the list
# print book => <DOM Element: book at 0x7f45b2d7cb00>

books = xmldoc.getElementsByTagName("book")

for book in books:
	author = book.getElementsByTagName("author")[0].firstChild.data
	title = book.getElementsByTagName("title")[0].firstChild.data
	print "author: "+ author+ "\t\t\t" + "book: "+ title
