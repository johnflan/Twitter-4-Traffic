def soundexcompare(streetname, addr):
    strname = rmdoublespace(streetname).lower()
    addname = rmdoublespace(addr).lower()
    rng = strname.count(' ')
    if addname.lower().count(' ') == rng:
        for i in range(0, rng):
            if soundex(addname.split(' ')[i].strip()) == soundex(strname.split(' ')[i].strip()):
                continue
            else:
                return False
                break
                
        return True     
    else:
        return False  


def rmdoublespace(strg):
    newstrg = ''
    for word in strg.split():
        newstrg = newstrg+' '+word
    return newstrg


def soundex(name, len=4):
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


            
s = 'i am in london bridge Robert'
k = 'i am in london brigde Rubin'
print soundexcompare(s,k)

