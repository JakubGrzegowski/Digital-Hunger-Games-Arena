import numpy as np
import random
from random import randint
import time
import os
import json


class Gladiator:
    def __init__(self, position=[0,0], index=None, hp=randint(80, 100), speed=randint(1, 9), damage=randint(10, 20),
                 defense=randint(1, 10), name="X"):
        # Initialized with JSON
        self.index = index
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.defense = defense
        self.name = name

        self.position = position
        self.isDead = False

########################################################################################################################


class Cell:
    def __init__(self, row=0, col=0):
        self.gladiatorRef = None
        self.row = row
        self.col = col
        self.isOccupied = False
        self.dmgBuff = 1
        
########################################################################################################################


class World:
    def __init__(self, size=16, gladiatorAmount=4):
        self.cells = [[Cell(row, col) for row in range(size)] for col in range(size)] #2D array declaration, size 16x16
        self.gladiatorArray = []
        self.readGladiatorsfromJSON()
        self.readCellBuffsfromJSON()
        self.deployGladiators()
        self.sizeX = size
        self.sizeY = size
        self.gameOver = False
        self.roundCounter = 0
        self.arenaBoundary = 0

    def generateStats(self): 
        for idx, gladiator in enumerate(self.gladiatorArray):    #assign index to each gladiator in gladiatorArray
            self.gladiatorArray[idx].index = idx
        


    def deployGladiators(self):
        for idx, gladiator in enumerate(self.gladiatorArray):
            while True:
                tempx = random.randint(0,15)
                tempy = random.randint(0,15)
                if(self.cells[tempx][tempy].isOccupied == False):
                    self.cells[tempx][tempy].gladiatorRef = self.gladiatorArray[idx]
                    self.cells[tempx][tempy].isOccupied = True
                    self.gladiatorArray[idx].position = [tempx, tempy]
                    break

    def readGladiatorsfromJSON(self, path="gladiators.json"):
        try:
            # open and load JSON file with gladiator statistics
            jsonfile = open(path)
            gladiators = json.load(jsonfile)
            for gladiator in gladiators:
                # load stats for gladiator
                stats = gladiators[gladiator]
                # create and add gladiator to game
                self.gladiatorArray.append(Gladiator(index=stats["index"], hp=stats["hp"], damage=stats["damage"],
                                                     defense=stats["defense"], speed=stats["speed"], name=stats["name"]))
        except:
            print("gladiators JSON File Error - Creating random gladiators")
            for i in range(4):
                self.gladiatorArray.append(Gladiator())

    def readCellBuffsfromJSON(self, path="cellBuffs.json"):
        try:
            # open and load JSON file with gladiator statistics
            jsonfile = open(path)
            buffs = json.load(jsonfile)
            for dmgType in buffs["Damage"]:
                for pos in buffs["Damage"][dmgType]["indexes"]:
                    self.cells[pos[0]][pos[1]].dmgBuff = buffs["Damage"][dmgType]["multiplier"]

        except:
            print("cell Buffs JSON File Error")

    def printWorld(self):

        for row in self.cells:
            for cell in row:
                if not cell.isOccupied:
                    if cell.row < self.arenaBoundary or cell.row > self.sizeX - self.arenaBoundary - 1 or cell.col < self.arenaBoundary or cell.col > self.sizeY - self.arenaBoundary - 1:
                        print("# ", end='')
                    elif cell.dmgBuff == 1.2:
                        print("s ", end='')
                    elif cell.dmgBuff == 1.5:
                        print("b ", end='')
                    else:
                        print("| ", end='')
                    #print(" ", end='')
                else:
                    print(cell.gladiatorRef.name, end='')
            print()
        time.sleep(1)
        os.system('CLS')


    def executeMove(self, gladiator, drow, dcol):

        # clear gladiator reference from cell
        self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied = False
        self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef = None

        # new gladiator coordinates
        print("Gladiator ", gladiator.name, " is about to move: ", drow, " ", dcol)
        gladiator.position[0] += drow
        gladiator.position[1] += dcol

        # collision check
        if self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied:
            # initiate fight
            self.fight(gladiator, self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef)
        else:
            # create new gladiator reference in cell (make normal move)
            self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied = True
            self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef = gladiator

            # check buffs
            gladiator.damage *= self.cells[gladiator.position[0]][gladiator.position[1]].dmgBuff
            gladiator.damage = int(gladiator.damage)
            self.cells[gladiator.position[0]][gladiator.position[1]].dmgBuff = 1.0
            # TODO print info about collecting buff


    def move(self):
        for gladiator in self.gladiatorArray:
            for move in range(gladiator.speed):
                if gladiator.isDead:
                    self.gladiatorArray.remove(gladiator)
                    break

                all_moves = [[1, -1], [1, 0], [1, 1], [0, -1], [0, 1], [-1, -1], [-1, 0], [-1, 1]]
                # check what moves are valid
                moves = []
                for move in all_moves:
                    # check if a gladiator will end up inside arena after a move
                    if self.arenaBoundary <= gladiator.position[0] + move[0] < self.sizeX - self.arenaBoundary - 1 and \
                            self.arenaBoundary <= gladiator.position[1] + move[1] < self.sizeY - self.arenaBoundary - 1:
                        moves.append(move)

                # TODO make this shit not random
                # random choice of possible moves
                drow, dcol = random.choice(moves)

                print()
                print(gladiator.name, " position: ", gladiator.position)

                self.executeMove(gladiator,drow,dcol) # execute move of gladiator

                # TODO dodać widownię dookoła areny
                #os.system('cls')

                # check if the game is over
                if len(self.gladiatorArray) <= 1:
                    self.gameOver = True

                #self.printWorld()

        self.roundCounter += 1
        if self.roundCounter % 2 == 0 and self.roundCounter != 0 and self.arenaBoundary < min([self.sizeX, self.sizeY]) / 2 - 2:
            print()
            print("ALERT!! ARENA IS SHRINKING !!")
            self.arenaBoundary += 1


            # TODO push gladiator outside the boundaries
            for gladiator in self.gladiatorArray:

                # check if a gladiator is inside arena
                if self.arenaBoundary <= gladiator.position[0] < self.sizeX - self.arenaBoundary - 1 and \
                        self.arenaBoundary <= gladiator.position[1] < self.sizeY - self.arenaBoundary - 1:
                    continue
                else:
                    if not gladiator.position[0] > self.arenaBoundary:
                        drow = 1
                    elif not gladiator.position[0] < self.sizeX - self.arenaBoundary:
                        drow = -1
                    else:
                        drow = 0
                    if not gladiator.position[1] > self.arenaBoundary:
                        dcol = 1
                    elif not gladiator.position[1] < self.sizeY - self.arenaBoundary:
                        dcol = -1
                    else:
                        dcol = 0

                    print()
                    print(gladiator.name, " is about to being pushed into arena")
                    self.executeMove(gladiator, drow, dcol)





    def fight(self, attacker, defender):
        print(attacker.name, "is attacking ", defender.name, ". Prepare for battle!")
        time.sleep(1)
        round = 0
        attackerDefaultDefense = attacker.defense
        defenderDefaultDefense = defender.defense
        while True:
            round += 1
            print()
            print("Round: ", round)

            # attacker move
            damageToDeal = attacker.damage - defender.defense + random.randint(1, 6)
            if damageToDeal > 0:
                defender.hp -= damageToDeal
                print(attacker.name, "dealt ", damageToDeal, "damage, ", defender.name, " HP = ", defender.hp)
            else:
                pass
                print(attacker.name, " dealt 0 damage, ", defender.name, " HP = ", defender.hp)
            if defender.hp <= 0:
                print(defender.name, " died in a battle, ", attacker.name, " is victorious!")

                # delete defender
                defender.isDead = True
                self.cells[defender.position[0]][defender.position[1]].isOccupied = False
                self.cells[defender.position[0]][defender.position[1]].gladiatorRef = None
                self.gladiatorArray.remove(defender)
                time.sleep(2)
                # end of the fight - exit loop
                attacker.defense = attackerDefaultDefense
                break
            defender.defense += -1
            time.sleep(0.1)

            # defender move

            damageToDeal = defender.damage - attacker.defense + random.randint(1,6)
            if damageToDeal > 0:
                attacker.hp -= damageToDeal
                print(defender.name, "dealt ", damageToDeal, "damage, ", attacker.name, " HP = ",attacker.hp)
            else:
                print(defender.name," dealt 0 damage", attacker.name, " HP = ",attacker.hp)

            if attacker.hp <= 0:
                print(attacker.name, " died in a battle, ", defender.name, " is victorious!")
                # delete attacker

                attacker.isDead = True
                self.cells[attacker.position[0]][attacker.position[1]].isOccupied = False
                self.cells[attacker.position[0]][attacker.position[1]].gladiatorRef = None

                # time.sleep(5)
                # end of the fight - exit loop
                defender.defense = defenderDefaultDefense
                break
            attacker.defense += -1
            time.sleep(0.1)
        time.sleep(1)

########################################################################################################################


def main():

    world = World()

    while not world.gameOver:
         world.printWorld()
         world.move()


if __name__ == "__main__":
    main()
