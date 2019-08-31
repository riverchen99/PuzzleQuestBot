import pyautogui
import os
import itertools
import collections

GRID_WIDTH = 8
GRID_HEIGHT = 8

GEM_WIDTH = 75
GEM_HEIGHT = 74

SPELL_WIDTH = 180
SPELL_HEIGHT = 38

TURN_X_DELTA = 115
TURN_Y_DELTA = 53

gemImageNames = os.listdir("Assets/Gems")
spellImageNames = os.listdir("Assets/Spells")

def in_bounds(x, y):
	return x >= 0 and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT

def can_match(a, b):
	skulls = ["5", "s"]
	manas = ["r", "g", "b", "y"]
	wilds = ["2", "3", "4", "6", "8"]
	return (a == b) or (a in skulls and b in skulls) or (a in manas and b in wilds) or (a in wilds and b in manas)

def move_type(a, b, c):
	for special_type in ("5", "2", "3", "4", "6", "8"):
		if special_type in (a, b, c):
			return special_type
	return a

def find_moves(grid):
	moves = collections.defaultdict(list)
	for y in range(GRID_HEIGHT):
		for x in range(GRID_WIDTH):
			if (grid[y][x] != "?"): # brute force a detect 3 move, inspired by https://github.com/akleemans/bejeweled-bot/blob/master/bejeweled-bot.py
				# (from_x, from_y, to_x, to_y)
				if (in_bounds(x-1, y) and can_match(grid[y][x], grid[y][x-1])):
					# move into spot right
					for [dy, dx] in [[-1, 1], [0, 2], [1, 1]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x+1, y)].append(move_type(grid[y][x], grid[y][x-1], grid[y+dy][x+dx]))

					# move into spot left
					for [dy, dx] in [[-1, -2], [0, -3], [1, -2]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x-2, y)].append(move_type(grid[y][x], grid[y][x-1], grid[y+dy][x+dx]))

				if (in_bounds(y-1, x) and can_match(grid[y][x], grid[y-1][x])):
					# move into spot above
					for [dy, dx] in [[-2, -1], [-3, 0], [-2, 1]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x, y-2)].append(move_type(grid[y][x], grid[y-1][x], grid[y+dy][x+dx]))

					# move into spot below
					for [dy, dx] in [[1, -1], [2, 0], [1, 1]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x, y+1)].append(move_type(grid[y][x], grid[y-1][x], grid[y+dy][x+dx]))

				# need additional in_bounds condition because loop limits don't protect against this case
				if (in_bounds(x-2, y) and can_match(grid[y][x], grid[y][x-2])):
					for [dy, dx] in [[-1, -1], [1, -1]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x-1, y)].append(move_type(grid[y][x], grid[y][x-2], grid[y+dy][x+dx]))

				if (in_bounds(x, y-2) and can_match(grid[y][x], grid[y-2][x])):
					for [dy, dx] in [[-1, -1], [-1, 1]]:
						if (in_bounds(x+dx, y+dy) and can_match(grid[y][x], grid[y+dy][x+dx])):
							moves[(x+dx, y+dy, x, y-1)].append(move_type(grid[y][x], grid[y-2][x], grid[y+dy][x+dx]))

	return moves

def construct_grid(gemScreenLocations):
	# convert the pixel locations into a grid representation
	grid = [["?" for i in range(GRID_WIDTH)] for j in range(GRID_HEIGHT)]
	gemGridLocations = {} # maybe use this later for smarter AI
	for gemImageName in gemScreenLocations:
		gemGridLocations[gemImageName] = []
		for gemLocation in gemScreenLocations[gemImageName]:
			gridY = int(round((gemLocation.top-minTop)/GEM_HEIGHT))
			gridX = int(round((gemLocation.left-minLeft)/GEM_WIDTH))
			grid[gridY][gridX] = gemImageName[0]
			gemGridLocations[gemImageName] += [{"y": gridY, "x": gridX}]
	return grid

def detect_gems():
	gemScreenLocations = {}
	# detect the grid from the screen
	for gemImageName in gemImageNames:
		gemScreenLocations[gemImageName] = list(pyautogui.locateAllOnScreen("Assets/Gems/" + gemImageName, confidence=.97))
		if (gemImageName == "5skull_small.PNG"):
			for i in range(len(gemScreenLocations[gemImageName])):
				gemScreenLocations[gemImageName][i] = gemScreenLocations[gemImageName][i]._replace(top = gemScreenLocations[gemImageName][i].top - 14)
				gemScreenLocations[gemImageName][i] = gemScreenLocations[gemImageName][i]._replace(left = gemScreenLocations[gemImageName][i].left - 19)
	return gemScreenLocations

def detect_spells():
	spellScreenLocations = {}
	for spellImageName in spellImageNames:
		spellScreenLocations[spellImageName] = pyautogui.locateOnScreen("Assets/Spells/" + spellImageName, confidence = .99)
	return spellScreenLocations

def spin_attack(grid):
	maxSkullCount = 0
	optimalX, optimalY = None, None
	for y in range(1, GRID_HEIGHT-1):
		for x in range(1, GRID_WIDTH-1):
			skullCount = 0
			for [dy, dx] in [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1], [1, -1], [1, 0], [1, -1]]:
				if (grid[y+dy][x+dx] == "s"):
					skullCount += 1
				elif (grid[y+dy][x+dx] == "5"):
					skullCount += 5
			if (skullCount > maxSkullCount):
				optimalY, optimalX = y, x
				maxSkullCount = skullCount
	return optimalY, optimalX, maxSkullCount

def cleave_count(grid):
	return sum(1 if grid[y][x] == "y" else 0 for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH))

def gridXToPixelX(x):
	return (x + .5) * GEM_WIDTH + minLeft

def gridYToPixelY(y):
	return (y + .5) * GEM_HEIGHT + minTop

while(True):
	# try to find the top left edge of the grid
	topLeftLocations = pyautogui.locateOnScreen("Assets/topleft.PNG", confidence = .99)
	if (topLeftLocations is None): # the cv didn't work correctly
		print("couldn't find top left")
		continue

	minLeft = topLeftLocations.left + 15
	minTop = topLeftLocations.top + 15

	# check if it's our turn
	if (pyautogui.pixelMatchesColor(int(minLeft - TURN_X_DELTA), int(minTop - TURN_Y_DELTA), (250, 218, 38), tolerance=75)):
		print("our turn!")

		pyautogui.moveTo(x = 1, y = 1) # make sure mouse doesn't get in the way of detection
		# detect gems
		gemScreenLocations = detect_gems()
		detectedGemCount = sum(len(gemScreenLocations[gemType]) for gemType in gemScreenLocations)
		print(detectedGemCount)
		if (detectedGemCount < 60):
			print("didn't detect enough gems")
			continue

		# detect spells
		spellScreenLocations = detect_spells()

		# construct our grid
		grid = construct_grid(gemScreenLocations)

		for i in grid:
			print(i)

		# find possible moves
		moves = find_moves(grid)

		# we couldn't find a move (mana drain animation clears the screen)
		if (moves == {}):
			print("couldn't find a move")
			continue

		# prioritize a skull matching move
		priorities = {
			"5" : .91, 
			"s" : .92, 
			"c" : .01, 
			"e" : .01, 
			"r" : .15, 
			"y" : .14, 
			"g" : .14, 
			"b" : 0,
			"2" : .22,
			"3" : .23,
			"4" : .24,
			"6" : .26,
			"8" : .28
		}
		sortedMoves = sorted(moves, key=lambda move: len(moves[move]) + sum(priorities[move_type] for move_type in moves[move]), reverse = True)
		
		for m in sortedMoves:
			print(m, moves[m])
		
		finalMove = sortedMoves[0]

		# .5 to click center of tile

		# we don't have a good move, try to cast a spell
		if (len(moves[finalMove]) == 1 
			and moves[finalMove][0] != "s" 
			and moves[finalMove][0] != "5"):

			if (spellScreenLocations["cleave.PNG"] is not None):
				yellowCount = cleave_count(grid)
				if (yellowCount > 5):
					pyautogui.click(x = spellScreenLocations["cleave.PNG"].left + SPELL_WIDTH * .5, y = spellScreenLocations["cleave.PNG"].top + SPELL_HEIGHT * .5)
					continue

			if (spellScreenLocations["spin_attack.PNG"] is not None):				
				spinTargetY, spinTargetX, maxSkullCount = spin_attack(grid)
				print("spin target", spinTargetX, spinTargetY)
				if (spinTargetY is not None):
					pyautogui.click(x = spellScreenLocations["spin_attack.PNG"].left + SPELL_WIDTH * .5, y = spellScreenLocations["spin_attack.PNG"].top + SPELL_HEIGHT * .5)
					pyautogui.click(x = gridXToPixelX(spinTargetX), y = gridYToPixelY(spinTargetY))
					continue

		# do a regular move
		pyautogui.click(x = gridXToPixelX(finalMove[0]), y = gridYToPixelY(finalMove[1]))
		pyautogui.click(x = gridXToPixelX(finalMove[2]), y = gridYToPixelY(finalMove[3]))