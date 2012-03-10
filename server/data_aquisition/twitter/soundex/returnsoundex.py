class returnSoundex:

		
	def rmdoublespace(self, strg):
		"""Remove double space from the string"""
		newstrg = ''
		for word in strg.split():
			newstrg = newstrg+' '+word
		return newstrg.strip()
		
		
	def soundex(self, name, len=4):
		""" soundex module conforming to Knuth's algorithm
			implementation 2000-12-24 by Gregory Jorgensen
			public domain
		"""

		# digits holds the soundex values for the alphabet
		digits = '01230120022455012623010202'
		sndx = ''
		fc = ''

		# translate alpha chars in name to soundex digits
		for c in name.upper():
			if c.isalpha():
				if not fc: fc = c   # remember first letter
				d = digits[ord(c)-ord('A')]
				# duplicate consecutive soundex digits are skipped
				if not sndx or (d != sndx[-1]):
					sndx += d

		# replace first digit with first alpha character
		sndx = fc + sndx[1:]

		# remove all 0s from the soundex code
		sndx = sndx.replace('0','')

		# return soundex code padded to len characters
		return (sndx + (len * '0'))[:len]

		
	def soundexstring(self, streetname):
		"""Return the soudex for the streetname"""
		strname = self.rmdoublespace(streetname)
		strname = strname.lower()
		rng = strname.count(' ')
		newsoundex = ''
		for i in range(0, rng+1):
			newsoundex = newsoundex + self.soundex(strname.split(' ')[i].strip())                
		return newsoundex

