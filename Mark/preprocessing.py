from lblparser import lbl_parse


def preprocess():
	pass





if __name__ == "__main__":
	# .lbl from link test
	res1 = lbl_parse('https://sbnarchive.psi.edu/pds3/neat/tricam/data/p20020306/obsdata/20020306022952d.lbl',1)
	# .lbl from local file test
	#res2 = lbl_parse('/home/mark/neat/20020306022952d.lbl')
	
	print(res1)
	#print(res2.items(),'\n')