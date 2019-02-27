from astropy.utils.data import download_file

def ldl_parse(file, link=False):
	
	""" 
		Parses a .ldl file and returns it as a dictionary
		
		file: link or local file path
		link: True is file is a link, false if local file path

		returns: dictionary form of .lbl file
	"""

	# Dictionary that turn each variable into the .lbl into a key-value pair
	ret = dict()

	# A list to contain key-value pairs so that they can be filtered
	# before being put into the dictionary
	l = []

	# Download ldl and read content as a file if link
	# or use the path if local
	if link:
		ldl = download_file(file, cache=True)
		content = open(ldl,'r')

	else:
		content = open(file,'r')
	


	
	# Populate list of key-value pairs, incomplete lines, and eliminate blank lines 
	for line in content:

		# Spit lines at '=' sign
		keyVal = line.split('=')

		# Ignore blank lines; else add to list after stripping whitespace
		if (len(keyVal) == 1 and keyVal[0].strip() == ''):
			continue
		else:
			for i in range(len(keyVal)):
				keyVal[i] = keyVal[i].strip()
		
		l.append(keyVal)

	
	i = 0
	while(True):
		print(len(l[i]))
		if len(l[i]) == 1:
			# If length of list elem. is 1, check if it's the end
			if l[i][0] == 'END':
				l.remove(l[i])
				break
			# Else append it to the last value of the last sublist and delete it
			l[i - 1][1] = l[i - 1][1] + l[i][0]
			l.remove(l[i])
		i+=1

	# Put everything in a dictionary
	for item in l:
		ret[item[0]] = item[1]

	return ret

if __name__ == "__main__":
	# .lbl from link test
	res1 = ldl_parse('https://sbnarchive.psi.edu/pds3/neat/tricam/data/p20020306/obsdata/20020306022952d.lbl',1)
	# .lbl from local file test
	#res2 = ldl_parse('/home/mark/neat/20020306022952d.lbl')
	
	print(res1.items(),'\n')
	#print(res2.items(),'\n')