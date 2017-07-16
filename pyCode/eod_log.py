class log_entry:
	def create(self,no,machine,db):
		self.no = no
		self.machine = machine
		self.db = db
	def display(self):
		print "%d\t%s\t%s\n" %(self.no,self.machine,self.db)

num = input("\nenter number of entries: ")
lst = []
for i in range(num):
	lst.append(log_entry())
	machine = raw_input("Machine")
	db = raw_input("DB")
	lst[i].create(i,machine,db)

for j in range(num):
	lst[j].display()
