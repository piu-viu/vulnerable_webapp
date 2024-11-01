def tegnsum(s):
    if not s: return 0
    return ord( s[0] ) + tegnsum( s[1:] )

print(tegnsum("hei på deg"))