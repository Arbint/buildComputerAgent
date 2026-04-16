class BuildComputerTools:

    def __init__(self):
        pass
    
    @classmethod
    def GetTools(cls):
        return [
            {
                "name": cls.GetMotherBoards.__name__,
                "description": "get the available motherboards",
                "input_schema": {
                    "type": "object",
                    "properties": 
                    {
                    }
                }
            },

        ]


    @classmethod
    def GetMotherBoards(cls):
        motherboards = {
            "ASUS ROG Strix B550-F Gaming": 189.99,
            "MSI MAG B660 Tomahawk WiFi": 189.99,
            "Gigabyte B550 AORUS Elite V2": 139.99,
            "ASRock B550M Pro4": 104.99,
            "ASUS TUF Gaming X570-Plus WiFi": 199.99,
            "MSI PRO Z790-A WiFi": 219.99,
            "Gigabyte Z790 AORUS Elite AX": 249.99,
            "ASUS ROG Strix Z790-E Gaming": 399.99,
            "MSI MPG Z690 Edge WiFi": 269.99,
            "ASRock B760M Pro RS": 109.99,
            "ASUS Prime B550M-A WiFi II": 124.99,
            "Gigabyte B650 AORUS Elite AX": 199.99,
            "MSI MAG X670E Tomahawk WiFi": 299.99,
            "ASUS ROG Crosshair X670E Hero": 699.99,
            "ASRock X670E Taichi": 449.99,
        } 
        return motherboards

    @classmethod
    def CallTool(cls, toolName, **toolInputs):
        method = getattr(cls, toolName)
        return method(**toolInputs)
