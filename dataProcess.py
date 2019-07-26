import os
from Model.InputManager import InputManager


def process():
    inputManager = InputManager()
    inputManager.transferToJson()
    inputManager.makeDuplicates()

if __name__ == "__main__":
    process()