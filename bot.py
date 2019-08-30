import pyautogui
import os
import itertools

GRID_WIDTH = 8
GRID_HEIGHT = 8
GEM_WIDTH = 75
GEM_HEIGHT = 74

TURN_X_DELTA = 115
TURN_Y_DELTA = 53

gemImages = os.listdir("Assets/Gems")
gemScreenLocations = {}

def in_bounds(x, y):
	return x >= 0 and x < GRID_WIDTH and y >= 0 and y < GRID_HEIGHT

while(True):
	# try to find the top left edge of the grid
	topLeftLocations = pyautogui.locateOnScreen("Assets/topleft.PNG", confidence = .99)
	if (topLeftLocations is None): # the cv didn't work correctly
		continue

	minLeft = topLeftLocations.left + 15
	minTop = topLeftLocations.top + 15

	# check if it's our turn
	if (pyautogui.pixelMatchesColor(int(minLeft - TURN_X_DELTA), int(minTop - TURN_Y_DELTA), (250, 218, 38), tolerance=50)):
		print("our turn!")

		# detect the grid from the screen
		for gemImageName in gemImages:
			gemScreenLocations[gemImageName] = list(pyautogui.locateAllOnScreen("Assets/Gems/" + gemImageName, confidence=.97))

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

		moves = []
		for y in range(1, GRID_HEIGHT):
			for x in range(1, GRID_WIDTH):
				if (grid[y][x] != "?"): # brute force a detect 3 move, inspired by https://github.com/akleemans/bejeweled-bot/blob/master/bejeweled-bot.py
					if (grid[y][x] == grid[y][x-1]):
						if (in_bounds(x+1, y-1) and grid[y][x] == grid[y-1][x+1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-1, "x" : x+1}, "to" : {"y" : y, "x" : x+1}}]
						if (in_bounds(x+2, y) and grid[y][x] == grid[y][x+2]):
							moves += [{"type": grid[y][x], "from" : {"y" : y, "x" : x+2}, "to" : {"y" : y, "x" : x+1}}]
						if (in_bounds(x+1, y+1) and grid[y][x] == grid[y+1][x+1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+1, "x" : x+1}, "to" : {"y" : y, "x" : x+1}}]

						if (in_bounds(x-2, y-1) and grid[y][x] == grid[y-1][x-2]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-1, "x" : x-2}, "to" : {"y" : y, "x" : x-2}}]
						if (in_bounds(x-3, y) and grid[y][x] == grid[y][x-3]):
							moves += [{"type": grid[y][x], "from" : {"y" : y, "x" : x-3}, "to" : {"y" : y, "x" : x-2}}]
						if (in_bounds(x-2, y+1) and grid[y][x] == grid[y+1][x-2]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+1, "x" : x-2}, "to" : {"y" : y, "x" : x-2}}]

					if (grid[y][x] == grid[y-1][x]):
						if (in_bounds(x-1, y-2) and grid[y][x] == grid[y-2][x-1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-2, "x" : x-1}, "to" : {"y" : y-2, "x" : x}}]
						if (in_bounds(x, y-3) and grid[y][x] == grid[y-3][x]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-3, "x" : x}, "to" : {"y" : y-2, "x" : x}}]
						if (in_bounds(x+1, y-2) and grid[y][x] == grid[y-2][x+1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-2, "x" : x+1}, "to" : {"y" : y-2, "x" : x}}]

						if (in_bounds(x-1, y+1) and grid[y][x] == grid[y+1][x-1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+1, "x" : x-1}, "to" : {"y" : y+1, "x" : x}}]
						if (in_bounds(x, y+2) and grid[y][x] == grid[y+2][x]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+2, "x" : x}, "to" : {"y" : y+1, "x" : x}}]
						if (in_bounds(x+1, y+1) and grid[y][x] == grid[y+1][x+1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+1, "x" : x+1}, "to" : {"y" : y+1, "x" : x}}]

					if (in_bounds(x-2, y) and grid[y][x] == grid[y][x-2]):
						if (in_bounds(x-1, y-1) and grid[y][x] == grid[y-1][x-1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-1, "x" : x-1}, "to" : {"y" : y, "x" : x-1}}]
						if (in_bounds(x-1, y+1) and grid[y][x] == grid[y+1][x-1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y+1, "x" : x-1}, "to" : {"y" : y, "x" : x-1}}]

					if (in_bounds(x, y-2) and grid[y][x] == grid[y-2][x]):
						if (in_bounds(x-1, y-1) and grid[y][x] == grid[y-1][x-1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-1, "x" : x+1}, "to" : {"y" : y-1, "x" : x}}]
						if (in_bounds(x+1, y-1) and grid[y][x] == grid[y-1][x+1]):
							moves += [{"type": grid[y][x], "from" : {"y" : y-1, "x" : x+1}, "to" : {"y" : y-1, "x" : x}}]
		
		# we couldn't find a move (mana drain animation clears the screen)
		if (moves == []):
			continue

		print(moves)

		# prioritize a skull matching move
		finalMove = None
		for move in moves:
			print(move["type"])
			if move["type"] == "s":
				finalMove = move
				break

		finalMove = moves[0] if finalMove is None else finalMove
		# .5 to click center of tile
		pyautogui.click(x = (finalMove["from"]["x"] + .5) * GEM_WIDTH + minLeft, y = (finalMove["from"]["y"] + .5) * GEM_HEIGHT + minTop)
		pyautogui.click(x = (finalMove["to"]["x"] + .5) * GEM_WIDTH + minLeft, y = (finalMove["to"]["y"] + .5) * GEM_HEIGHT + minTop)

		for i in grid:
			print(i)

