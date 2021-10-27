class Main:
    base = 'OBSbox'
    name = 'OBSdummy'
    description = 'Dummy OBS plugin'

    inputs = {
        'execute': 'button'
    }

    lastInstNo = 0
    instances = {}

    def __init__(self, inputs):
        print("bounce initialised")
        Main.lastInstNo += 1
        self.instNo = Main.lastInstNo
        Main.instances[self.instNo] = self
        self.data = inputs

    def setInput(self, inputs):
        self.data = inputs

    def update(self, input):
        if (input == 'execute'):
            self.data['execute'] = False

    def destroy(self):
        del Main.instances[self.instNo]