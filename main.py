import numpy as np
import random
import time
import os

class Gladiator:
    def __init__(self):
        self.position = [0, 0]
        self.index = None
        self.hp = random.randint(1,9)
        self.speed = random.randint(1,9)  
        self.damage = random.randint(1,9) 
        self.name = "gladiator"

####################################################################################################################################### 
        
class Cell:
    def __init__(self, x=0, y=0):
        self.gladiatorRef = None
        self.x = x
        self.y = y
        self.isOccupied = False
        
#######################################################################################################################################        

class World:
    def __init__(self, size=16, gladiatorAmount=4):
        self.cells = [[Cell() for i in range(size)] for i in range(size)] #2D array declaration, size 16x16
        self.gladiatorArray = [Gladiator() for i in range(gladiatorAmount)] 
        self.sizeX=size
        self.sizeY=size
        
        
    def generateStats(self): 
        for idx, gladiator in enumerate(self.gladiatorArray):    #assign index to each gladiator in gladiatorArray
            self.gladiatorArray[idx].index = idx
        
        self.gladiatorArray[0].name = "A "
        self.gladiatorArray[1].name = "B "
        self.gladiatorArray[2].name = "C "
        self.gladiatorArray[3].name = "D "
    

    def deployGladiators(self):
        for idx, gladiator in enumerate(self.gladiatorArray):
            while True:
                tempx = random.randint(0,15)
                tempy = random.randint(0,15)
                if(self.cells[tempx][tempy].isOccupied==False):
                    self.cells[tempx][tempy].gladiatorRef=self.gladiatorArray[idx]
                    self.cells[tempx][tempy].isOccupied=True
                    self.gladiatorArray[idx].position = [tempx, tempy]
                    break
                

    def printWorld(self):
        for row in self.cells:
            for cell in row:
                if(cell.isOccupied==False):
                    print("| ", end='')
                    #print(" ", end='')
                else:
                    print (cell.gladiatorRef.name, end='')
            print()

    def move(self):
        for gladiator in self.gladiatorArray:
            while (True):
                dx = random.randint(-1,1)
                dy = random.randint(-1,1)
            
                if  0 <= gladiator.position[0] + dx <= self.sizeX and 0 <= gladiator.position[1] + dy <= self.sizeY:

                    #TODO wyczyścić refy z cell  
                    self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied=False;
                    self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef=None;
                    
                    print("Gladiator ", gladiator.name, " is about to move: ", dx, " ", dy)
                    gladiator.position[0] += dx
                    gladiator.position[1] += dy
                    
                    #TODO sprawdzić kolizje
                    #TODO zmienic osie x oraz y                 

                    #TODO wpierdolić refy do nowych cell
                    self.cells[gladiator.position[0]][gladiator.position[1]].isOccupied=True;
                    self.cells[gladiator.position[0]][gladiator.position[1]].gladiatorRef=gladiator;

                    print(gladiator.name, " position: ", gladiator.position)

                    #TODO dodać widownię dookoła areny
                    print("(づ ᴗ _ᴗ)づ♡")
                    break

#######################################################################################################################################      

def main():
    world = World()
    world.generateStats()
    world.deployGladiators()
    for x in range(1000):
        os.system('CLS')
        world.printWorld()
        world.move()
        time.sleep(1)
        



if __name__ == "__main__":
    main()
        


















