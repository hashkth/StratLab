
from states import *

def main():
    Core.init(1280, 720, "StratLab")
    Core.activate_state("StartMenu")
    Core.run()

if __name__ == "__main__":
    main()