from anthropic import Anthropic
from buildComputer.utilities import GetAPIKey
from buildComputer.tools import BuildComputerTools
import json


def DIYComputer(userMsg):
    client = Anthropic(api_key=GetAPIKey())

    system = "you are a expert in DIY computers, help users find components for the next PC build. if you can't do the request due to lacking tools, tell the user that you can't do it. if you are not certain about a specific fact such as pricing, availability, benchmark numbers, or compatibility details, say that you don't know rather than guessing."
    message = [{"role":"user", "content": userMsg}]

    maxIter = 10
    iter = 0

    while iter < maxIter:
        iter += 1

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system = system,
            messages = message,
            tools = BuildComputerTools.GetTools()
        )

        # this should resturn some thing like this as a response
        # content=[TextBlock(citations=None, text='Sure! Let me fetch the list of available motherboards for you right away!', type='text'), 
        #         ToolUseBlock(id='toolu_01Tv2fUWt6297CH5ncb2967m', caller=DirectCaller(type='direct'), input={}, name='getMotherboards', type='tool_use')],
        # model='claude-sonnet-4-6', role='assistant', stop_details=None, stop_reason='tool_use', stop_sequence=None, type='message', 
        # usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='global', input_tokens=572, output_tokens=54, server_tool_use=None, service_tier='standard'))

        toolUseBlockes =[block for block in response.content if block.type=="tool_use"]
        textBlocks = [block for block in response.content if block.type=="text"]

        for textBlock in textBlocks: 
            print(f"assstant: {textBlock.text}")

        message.append({"role": "assistant", "content": response.content})
        if toolUseBlockes:

            toolResults = []
            for toolUseBlock in toolUseBlockes: 
                print(f"----> Calling: {toolUseBlock.name}")
                print(f"args: {toolUseBlock.input}")

                result = BuildComputerTools.CallTool(toolName=toolUseBlock.name, **toolUseBlock.input)
                toolResults.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": toolUseBlock.id,
                        "content": json.dumps(result)
                    }
                )

            message.append({"role":"user", "content": toolResults})
            continue
        else:
            userInput = input("\n>>> ")
            if userInput.lower() == "exit":
                break

            message.append({"role":"user", "content": userInput})

        if iter >= maxIter:
            print(f"Max iterations {maxIter} reached. ending conversation.")
    

def main():
    DIYComputer("find me the list of available motherboards")

