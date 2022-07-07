import random
import sys
from random import randint
import os
import json
import math
from tools import wait, clearScreen
import numpy as np


class Gladiator:
    def __init__(self, position=None, index=None, hp=randint(80, 100), speed=randint(1, 9), damage=randint(10, 20),
                 defense=randint(1, 10), name="X", tactic="yellow"):
        # Initialized with JSON
        if position is None:
            position = [0, 0]
        self.index = index
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.defense = defense
        self.name = name
        self.tactic = tactic
        self.position = position
        self.isDead = False


########################################################################################################################


class Cell:
    def __init__(self, row=0, col=0):
        self.gladiatorRef = None
        self.row = row
        self.col = col
        self.isOccupied = False
        self.isActive = True


########################################################################################################################


class World:
    def __init__(self, size=16):
        self.sizeX = size
        self.sizeY = size

        self.readConfig()
        self.cells = [[Cell(row, col) for col in range(self.sizeX)]
                      for row in range(self.sizeY)]  # 2D array declaration, size 16x16
        self.gladiatorArray = []

        self.buffs = {}

        # Load configuration files
        self.readGladiatorsfromJSON()

        yellowstrategy = random.randint(1, 3)  # assigning random tactic to yellow gladiator
        for gladiator in self.gladiatorArray:
            if gladiator.tactic == "yellow":
                if yellowstrategy == 1:
                    gladiator.tactic = "red"
                elif yellowstrategy == 2:
                    gladiator.tactic = "blue"
                else:
                    gladiator.tactic = "green"

        self.readCellBuffsfromJSON()

        self.deployGladiators()

        self.gameOver = False
        self.roundCounter = 0
        self.shrinkTime = 2  # after this number of rounds arena will shrink by 1  tile
        self.arenaBoundary = 0
        self.yellowStrategy = 0

    def generateStats(self):
        for idx, gladiator in enumerate(self.gladiatorArray):  # assign index to each gladiator in gladiatorArray
            self.gladiatorArray[idx].index = idx

    def deployGladiators(self):
        for idx, gladiator in enumerate(self.gladiatorArray):
            while True:
                tempx = random.randint(0, 15)
                tempy = random.randint(0, 15)
                if not self.cells[tempx][tempy].isOccupied:
                    self.cells[tempx][tempy].gladiatorRef = self.gladiatorArray[idx]
                    self.cells[tempx][tempy].isOccupied = True
                    self.gladiatorArray[idx].position = [tempx, tempy]
                    break

    def readConfig(self, path="config.json"):
        try:
            # open and load JSON file with config for arena
            jsonfile = open(path)
            config = json.load(jsonfile)
            self.shrinkTime = config["shrinkTime"]
            self.sizeX = config["arenaDimensionX"]
            self.sizeY = config["arenaDimensionY"]
        except:
            print("Load config failed")

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
                                                     defense=stats["defense"], speed=stats["speed"],
                                                     name=stats["name"], tactic=stats["tactic"]))
        except:
            print("gladiators JSON File Error - Creating random gladiators")
            for i in range(4):
                self.gladiatorArray.append(Gladiator())

    def readCellBuffsfromJSON(self, path="cellBuffs.json"):
        try:
            # open and load JSON file with cell buffs
            jsonfile = open(path)
            buffs = json.load(jsonfile)
            self.buffs = buffs
            for dmgType in buffs["Damage"]:
                for pos in buffs["Damage"][dmgType]["indicies"]:
                    self.cells[pos[0]][pos[1]].dmgBuff = buffs["Damage"][dmgType]["multiplier"]

        except:
            print("cell Buffs JSON File Error")

    def printWorld(self):
        wait(3)
        clearScreen()

        for row in self.cells:
            for cell in row:
                if not cell.isOccupied:
                    if not cell.isActive:
                        print("# ", end='')
                    elif [cell.row, cell.col] in self.buffs["Damage"]["small"]["indicies"]:
                        print("s ", end='')
                    elif [cell.row, cell.col] in self.buffs["Damage"]["big"]["indicies"]:
                        print("b ", end='')
                    else:
                        print("| ", end='')
                    # print(" ", end='')
                else:
                    print(cell.gladiatorRef.name, end='')
            print()

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
            for type in self.buffs:  # for now there is only "Damage"
                for size in self.buffs[type]:  # rozmiar buffa "small" or "big":
                    if [gladiator.position[0], gladiator.position[1]] in self.buffs[type][size]["indicies"]:
                        gladiator.damage = int(gladiator.damage * self.buffs[type][size]["multiplier"])
                        self.buffs[type][size]["indicies"].remove(gladiator.position)
            # gladiator.damage *= self.cells[gladiator.position[0]][gladiator.position[1]].dmgBuff
            # gladiator.damage = int(gladiator.damage)
            # self.cells[gladiator.position[0]][gladiator.position[1]].dmgBuff = 1.0

            # TODO print info about collecting buff

    def followTarget(self, gladiator, target):
        deltaRow = gladiator.position[0] - target.row
        deltaCol = gladiator.position[1] - target.col
        if deltaRow > 0:
            deltaRow = -1
        elif deltaRow < 0:
            deltaRow = 1

        if deltaCol > 0:
            deltaCol = -1
        elif deltaCol < 0:
            deltaCol = 1

        return deltaRow, deltaCol


    def findClosestBuff(self, gladiator, type):
        # return target position with buff
        # and None if there is no more buffs
        buffsIdx = self.buffs["Damage"][type]["indicies"]
        if buffsIdx:
            pos = gladiator.position

            distance = np.subtract(buffsIdx, pos)
            distance = np.sqrt(distance[:, 0]**2 + distance[:, 1]**2)
            idx = np.argmin(distance)
            return buffsIdx[idx]
        else:
            return False, False

    def findWeakestEnemy(self, gladiator):
        if len(self.gladiatorArray) > 1:
            target = None
            damage = 100
            for enemy in self.gladiatorArray:
                if enemy == gladiator:
                    continue
                elif enemy is None:
                    target = enemy
                    damage = enemy.damage
                else:
                    if enemy.damage < damage:
                        target = enemy
                        damage = enemy.damage
                    else:
                        continue
            return target.position[0], target.position[1]
        else:
            return False, False

    # red gladiator movement
    def findClosestEnemy(self, gladiator):
        target = None
        distance = 0
        targetdistance = 0
        distanceformula = 0
        if len(self.gladiatorArray) > 1:
            for targetHelp in self.gladiatorArray:
                if targetHelp == gladiator:
                    continue
                elif target is None:
                    target = targetHelp
                    distanceformula = (pow((targetHelp.position[0] - gladiator.position[0]), 2)) + (
                        pow((targetHelp.position[1] - gladiator.position[1]), 2))
                    targetdistance = math.sqrt(distanceformula)
                else:
                    distanceformula = (pow((targetHelp.position[0] - gladiator.position[0]), 2)) + (
                        pow((targetHelp.position[1] - gladiator.position[1]), 2))
                    distance = math.sqrt(distanceformula)
                    if distance < targetdistance:
                        target = targetHelp
                        targetdistance = distance
                    else:
                        continue
            return target.position[0], target.position[1]
        else:
            return False, False

    def move(self):
        for gladiator in self.gladiatorArray:
            for move in range(gladiator.speed):
                if gladiator.isDead:
                    self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied = False
                    self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef = None
                    self.gladiatorArray.remove(gladiator)
                    break

                all_moves = [[1, -1], [1, 0], [1, 1], [0, -1], [0, 1], [-1, -1], [-1, 0], [-1, 1]]
                # check what moves are valid
                moves = []
                for move in all_moves:
                    # check if a gladiator will end up inside arena after a move
                    if self.arenaBoundary <= gladiator.position[0] + move[0] < self.sizeX - self.arenaBoundary and \
                            self.arenaBoundary <= gladiator.position[1] + move[1] < self.sizeY - self.arenaBoundary:
                        moves.append(move)

                drow = None
                dcol = None

                if gladiator.tactic == "green":
                    targetRow, targetCol = self.findClosestBuff(gladiator, "big")
                    if not targetRow:
                        targetRow, targetCol = self.findClosestEnemy(gladiator)
                    drow, dcol = self.followTarget(gladiator, self.cells[targetRow][targetCol])
                elif gladiator.tactic == "blue":
                    targetRow, targetCol = self.findClosestBuff(gladiator, "small")
                    if not targetRow:
                        targetRow, targetCol = self.findWeakestEnemy(gladiator)
                    drow, dcol = self.followTarget(gladiator, self.cells[targetRow][targetCol])
                elif gladiator.tactic == "red":
                    targetRow, targetCol = self.findClosestEnemy(gladiator)
                    drow, dcol = self.followTarget(gladiator, self.cells[targetRow][targetCol])

                # TODO make this shit not random POGCHAMP
                # random choice of possible moves
                # drow, dcol = random.choice(moves)
                # drow, dcol = self.followTarget(gladiator, self.cells[8][8])

                # check if calculated move is valid
                if not [drow, dcol] in moves:
                    drow, dcol = random.choice(moves)

                print()
                print(gladiator.name, " position: ", gladiator.position)

                self.executeMove(gladiator, drow, dcol)  # execute move of gladiator

                # TODO dodać widownię dookoła areny que?
                # os.system('cls')

                # check if the game is over
                if len(self.gladiatorArray) <= 1:
                    self.gameOver = True
                    print(self.gladiatorArray[0].name + "won the game!!!")
                    break

                self.printWorld()

        self.roundCounter += 1
        if self.roundCounter % 2 == 0 and self.roundCounter != 0 and \
                self.arenaBoundary < min([self.sizeX, self.sizeY]) / self.shrinkTime - 2:
            print()
            print("ALERT!! ARENA IS SHRINKING !!")
            self.arenaBoundary += 1

            # push gladiator outside the boundaries
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

            # disable a cell that is no longer valid
            for row in self.cells:
                for cell in row:
                    if cell.row < self.arenaBoundary or cell.row > self.sizeX - self.arenaBoundary - 1 or \
                            cell.col < self.arenaBoundary or cell.col > self.sizeY - self.arenaBoundary - 1:
                        cell.isActive = False
                    # remove buff
                    if [cell.row, cell.col] in self.buffs["Damage"]["small"]["indicies"]:
                        self.buffs["Damage"]["small"]["indicies"].remove([cell.row, cell.col])

    def fight(self, attacker, defender):
        print(attacker.name, "is attacking ", defender.name, ". Prepare for battle!")
        wait(3)
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
                wait(3)
                # end of the fight - exit loop
                attacker.defense = attackerDefaultDefense
                break
            defender.defense += -1
            wait(0.3)

            # defender move

            damageToDeal = defender.damage - attacker.defense + random.randint(1, 6)
            if damageToDeal > 0:
                attacker.hp -= damageToDeal
                print(defender.name, "dealt ", damageToDeal, "damage, ", attacker.name, " HP = ", attacker.hp)
            else:
                print(defender.name, " dealt 0 damage", attacker.name, " HP = ", attacker.hp)

            if attacker.hp <= 0:
                print(attacker.name, " died in a battle, ", defender.name, " is victorious!")
                # delete attacker

                attacker.isDead = True

                # wait(5)
                # end of the fight - exit loop
                defender.defense = defenderDefaultDefense
                break
            attacker.defense += -1
            wait(0.3)
        wait(3)


########################################################################################################################


def main():
    world = World()
    while not world.gameOver:
        # world.printWorld()
        world.move()


def test():
    for i in range(1000):
        # disable print
        sys.stdout = sys.__stdout__
        # enable print
        print(i)
        sys.stdout = open(os.devnull, 'w')
        main()
    print("Zajebiście działa")

if __name__ == "__main__":
    main()
    # test()
