
def hello_world1():
	def hello_world2():
		print("Hello World2")

	print("hello world 1")
	hello_world2()

hello_world1()
#hello_world2() #this causes the error.
if __name__ == "__main__":
#	print_this()
	print (__name__)
