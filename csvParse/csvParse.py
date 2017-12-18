import csv

with open("temp.csv", "r") as tempFile:
	fileReader = csv.reader(tempFile, delimiter=',')
	fileList = []
	for row in fileReader:
		if len(row) !=0:
			fileList = fileList + row

tempFile.close()
print fileList
