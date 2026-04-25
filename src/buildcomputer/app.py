from buildcomputer.agents.computerBuilderAgent import ComputerBuilderAgent
from buildcomputer.instrumentation.instrumentation import SetupTracing
def DIYComputer():
    SetupTracing()
    agent = ComputerBuilderAgent()
    maxIter = 10
    iter = 0
    agent.ProcessNewUserInput("hi")
    while iter < maxIter:
        userInput = input("\n>>> ")
        if userInput.lower() == "exit":
            break

        agent.ProcessNewUserInput(userInput)

def main():
    DIYComputer()