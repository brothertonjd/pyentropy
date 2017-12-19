
def HighLowEnt(entropyList):
	highEnt = 0
	lowEnt = 8
	highEntLoc = 0
	lowEntLoc = 0
	for i, ent in enumerate(entropyList):
		if i > 25:
			if ent > highEnt:
				highEnt = ent
				highEntLoc = i
			if ent < lowEnt:
				lowEnt = ent
				lowEntLoc = i
	print(highEntLoc)
	print(lowEntLoc)
	print(highEnt)
	print(lowEnt)
