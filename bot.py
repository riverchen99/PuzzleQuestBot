import pyautogui
import os
import itertools
import collections

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

		moves = collections.defaultdict(list)
		for y in range(1, GRID_HEIGHT):
			for x in range(1, GRID_WIDTH):
				if (grid[y][x] != "?"): # brute force a detect 3 move, inspired by https://github.com/akleemans/bejeweled-bot/blob/master/bejeweled-bot.py
					# (from_x, from_y, to_x, to_y)
					if (grid[y][x] == grid[y][x-1]):
						if (in_bounds(x+1, y-1) and grid[y][x] == grid[y-1][x+1]):
							moves[(x+1, y-1, x+1, y)].append(grid[y][x])
						if (in_bounds(x+2, y) and grid[y][x] == grid[y][x+2]):
							moves[(x+2, y, x+1, y)].append(grid[y][x])
						if (in_bounds(x+1, y+1) and grid[y][x] == grid[y+1][x+1]):
							moves[(x+1, y+1, x+1, y)].append(grid[y][x])

						if (in_bounds(x-2, y-1) and grid[y][x] == grid[y-1][x-2]):
							moves[(x-2, y-1, x-2, y)].append(grid[y][x])
						if (in_bounds(x-3, y) and grid[y][x] == grid[y][x-3]):
							moves[(x-3, y, x-2, y)].append(grid[y][x])
						if (in_bounds(x-2, y+1) and grid[y][x] == grid[y+1][x-2]):
							moves[(x-2, y+1, x-2, y)].append(grid[y][x])

					if (grid[y][x] == grid[y-1][x]):
						if (in_bounds(x-1, y-2) and grid[y][x] == grid[y-2][x-1]):
							moves[(x-1, y-2, x, y-2)].append(grid[y][x])
						if (in_bounds(x, y-3) and grid[y][x] == grid[y-3][x]):
							moves[(x, y-3, x, y-2)].append(grid[y][x])
						if (in_bounds(x+1, y-2) and grid[y][x] == grid[y-2][x+1]):
							moves[(x+1, y-2, x, y-2)].append(grid[y][x])

						if (in_bounds(x-1, y+1) and grid[y][x] == grid[y+1][x-1]):
							moves[(x-1, y+1, x, y+1)].append(grid[y][x])
						if (in_bounds(x, y+2) and grid[y][x] == grid[y+2][x]):
							moves[(x, y+2, x, y+1)].append(grid[y][x])
						if (in_bounds(x+1, y+1) and grid[y][x] == grid[y+1][x+1]):
							moves[(x+1, y+1, x, y+1)].append(grid[y][x])

					if (in_bounds(x-2, y) and grid[y][x] == grid[y][x-2]):
						if (in_bounds(x-1, y-1) and grid[y][x] == grid[y-1][x-1]):
							moves[(x-1, y-1, x-1, y)].append(grid[y][x])
						if (in_bounds(x-1, y+1) and grid[y][x] == grid[y+1][x-1]):
							moves[(x-1, y+1, x-1, y)].append(grid[y][x])

					if (in_bounds(x, y-2) and grid[y][x] == grid[y-2][x]):
						if (in_bounds(x-1, y-1) and grid[y][x] == grid[y-1][x-1]):
							moves[(x-1, y-1, x, y-1)].append(grid[y][x])
						if (in_bounds(x+1, y-1) and grid[y][x] == grid[y-1][x+1]):
							moves[(x+1, y-1, x, y-1)].append(grid[y][x])
		
		# we couldn't find a move (mana drain animation clears the screen)
		if (moves == []):
			continue


		# prioritize a skull matching move
		priorities = ["5", "s", "c", "e", "r", "y", "g", "b"]
		moves = sorted(moves, key=lambda move: (len(moves[move]) + (1 if ("5" in moves[move] or "s" in moves[move]) else 0)), reverse = True)
		print(moves)
		finalMove = moves[0]
		# .5 to click center of tile
		pyautogui.click(x = (finalMove[0] + .5) * GEM_WIDTH + minLeft, y = (finalMove[1] + .5) * GEM_HEIGHT + minTop)
		pyautogui.click(x = (finalMove[2] + .5) * GEM_WIDTH + minLeft, y = (finalMove[3] + .5) * GEM_HEIGHT + minTop)

		for i in grid:
			print(i)

