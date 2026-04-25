from anthropic import Anthropic
import json
from buildcomputer.utilities import GetAPIKey, GetGreyBG, GetReset
from opentelemetry import trace

_tracer = trace.get_tracer("buildcomputer.agent")

class Agent:
    def __init__(self, name, description, properties, system, userInput="", maxIter=10):
        self.name = name
        self.description = description
        self.properties = properties
        self.system = system
        self.messages = []
        self.model = "claude-sonnet-4-6"
        self.maxTokens = 1024
        if userInput:
            self.messages.append({"role":"user", "content": userInput})

        self.maxIter = maxIter
        self.subAgents = {}

        self.client = Anthropic(api_key=GetAPIKey())


    def ProcessNewUserInput(self, userInput):
        with _tracer.start_as_current_span(self.name) as span:
            span.set_attribute("agent.name", self.name)
            self.messages.append({"role":"user", "content": userInput})
            self.Run()


    def Run(self):
        with _tracer.start_as_current_span(f"{self.name}.Run") as span:
            iter = 0
            response = None
            while iter < self.maxIter:
                iter += 1

                print(f"\n------- Interation {iter} -------")
                self.__PrintContextWindow()

                response = self._SendRequestToAgent()

                toolUseBlocks =[block for block in response.content if block.type=="tool_use"]
                textBlocks = [block for block in response.content if block.type=="text"]

                for textBlock in textBlocks: 
                    print(f"assstant: {textBlock.text}")

                self.messages.append({"role": "assistant", "content": response.content})

                if toolUseBlocks:
                    toolResults = self.__ProcessToolUse(toolUseBlocks)
                    self.messages.append({"role":"user", "content": toolResults})
                else:
                    break

            finalResponseTextBlocks = [block for block in response.content if block.type=="text"]
            finalResponse = ""
            for textBlock in finalResponseTextBlocks:
                finalResponse += textBlock.text

            if finalResponse == "":
                finalResponse = "no response"
            span.set_attribute("agent.interators", iter)
            return finalResponse
            

    def ConfigureInput(self, **inputs):
        pass


    def AddSubAgent(self, newAgent):
        self.subAgents[newAgent.name] = newAgent


    def GetTools(self):
        tools = self.GetAgentTools() + self.GetSubAgentAsTools()
        return tools


    def GetAgentTools(self):
        return []


    def GetSubAgentAsTools(self):
        tools = []
        for subAgent in self.subAgents.values():
            tools.append(subAgent.GetToolDescription())

        return tools


    def GetToolDescription(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.properties
            }
        }


    def __CallTool(self, toolName, **toolInputs):
        method = getattr(self, toolName, None)
        if method:
            return method(**toolInputs)
        else:
            return self.__CallSubAgent(toolName, **toolInputs)


    def __CallSubAgent(self, agentName, **inputs):
        subAgent = self.subAgents.get(agentName, None)
        if subAgent:
            subAgent.ConfigureInput(**inputs)
            return subAgent.Run()


    def __PrintContextWindow(self):
        print(f"\n{GetGreyBG()}---- Context Window ({len(self.messages)+1} messages) ----{GetReset()}")

        for tool in self.GetTools():
            params = list(tool["input_schema"].get("properties", {}).keys())
            required = tool["input_schema"].get("required", [])
            paramStr = ", ".join(f"{p}{'*' if p in required else '?'}" for p in params)
            print(f"{GetGreyBG()}[function call defination] {tool['name']}({paramStr}) - {tool['description']}{GetReset()}")

        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]

            if isinstance(content, str):
                print(f"{GetGreyBG()}[{role}]: {content}{GetReset()}")
            elif isinstance(content, list):
                hasText = any(not isinstance(block, dict) and block.type=="text" for block in content)
                if not hasText: 
                    print(f"{GetGreyBG()}[{role}]:{GetReset()}")
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type")=="tool_result":
                            print(f"{GetGreyBG()}[{role} (tool_result id={block['tool_use_id']})]: {block['content']}{GetReset()}")

                    else:
                        if block.type=="text":
                            print(f"{GetGreyBG()}[{role}]: {block.text}{GetReset()}")
                        elif block.type=="tool_use":
                            print(f"{GetGreyBG()} -> tool_use (id={block.id}): {block.name}({json.dumps(block.input)}){GetReset()}")

        print(f"{GetGreyBG()}----{GetReset()}\n")
                    

    def __ProcessToolUse(self, toolUseBlocks):
        toolResults = []
        for toolUseBlock in toolUseBlocks: 
            print(f"----> Calling: {toolUseBlock.name}")
            print(f"args: {toolUseBlock.input}")

            result = self.__CallTool(toolName=toolUseBlock.name, **toolUseBlock.input)
            toolResults.append(
                {
                    "type": "tool_result",
                    "tool_use_id": toolUseBlock.id,
                    "content": json.dumps(result)
                }
            )

        return toolResults


    def _SendRequestToAgent(self):
        with _tracer.start_as_current_span("claude", kind=trace.SpanKind.CLIENT) as span:
            span.set_attribute("gen_ai.system", "anthropic")
            span.set_attribute("gen_ai.request.model", self.model)
            span.set_attribute("gen_ai.request.max_tokens", self.maxTokens)

            span.set_attribute("langfuse.input", json.dumps(self.messages, default=str))

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.maxTokens,
                system = self.system,
                messages = self.messages,
                tools = self.GetTools()
            )

            span.set_attribute("gen_ai.usage.input_tokens", response.usage.input_tokens)
            span.set_attribute("gen_ai.usage.output_tokens", response.usage.output_tokens)
            span.set_attribute("gen_ai.response.model", response.model) 

            completion = " ".join(block.text for block in response.content if block.type == "text")
            span.set_attribute("langfuse.output", completion)

            return response