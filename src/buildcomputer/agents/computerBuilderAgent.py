from buildcomputer.agents.agent import Agent
from buildcomputer.agents.mainUnitAgent import MainUnitAgent
from buildcomputer.agents.monitorAgent import MonitorAgent

class ComputerBuilderAgent(Agent):
    def __init__(self):
        super().__init__(
            name="ComputerBuilderAgent",
            description="Build a complete PC setup recommendation including main unit, monitor, mouse, and keyboard",
            properties={
                "price": {
                    "type": "integer",
                    "description": "total budget in USD"
                },
                "use_case": {
                    "type": "string",
                    "description": "intended use case, e.g. gaming, creative, office"
                }
            },
            system="""You are an expert PC builder who helps users assemble a complete computer setup.
                You coordinate recommendations across all components:
                * Main unit (CPU, GPU, motherboard, RAM, case, storage, PSU)
                * Monitor
                * Mouse
                * Keyboard
                Use the available tools to gather options and then recommend a cohesive, compatible build
                that fits the user's budget and use case.
            """
        )
        self.AddSubAgent(MainUnitAgent())
        self.AddSubAgent(MonitorAgent())

    def GetAgentTools(self):
        return [
            {
                "name": self.GetAvailableMice.__name__,
                "description": "get the available mice",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wireless": {
                            "type": "boolean",
                            "description": "filter by wireless (true) or wired (false)"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "filter by use case: 'gaming', 'productivity'"
                        },
                        "priceMax": {
                            "type": "integer",
                            "description": "maximum price in USD"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            },
            {
                "name": self.GetAvailableKeyboards.__name__,
                "description": "get the available keyboards",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "wireless": {
                            "type": "boolean",
                            "description": "filter by wireless (true) or wired (false)"
                        },
                        "layout": {
                            "type": "string",
                            "description": "filter by layout: 'full', 'tenkeyless', '75%', '65%'"
                        },
                        "priceMax": {
                            "type": "integer",
                            "description": "maximum price in USD"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            }
        ]


    def GetAvailableMice(self, wireless=None, use_case=None, priceMax=None):
        mice = {
            "Logitech G Pro X Superlight 2": {
                "wireless": True,
                "dpi_max": 32000,
                "weight_g": 60,
                "buttons": 5,
                "battery_life_hours": 95,
                "sensor": "HERO 2",
                "use_cases": ["gaming"],
                "price_usd": 159,
            },
            "Razer DeathAdder V3 HyperSpeed": {
                "wireless": True,
                "dpi_max": 26000,
                "weight_g": 77,
                "buttons": 6,
                "battery_life_hours": 300,
                "sensor": "Razer Focus Pro",
                "use_cases": ["gaming"],
                "price_usd": 99,
            },
            "Zowie EC2-C": {
                "wireless": False,
                "dpi_max": 3200,
                "weight_g": 73,
                "buttons": 5,
                "sensor": "3crosshair",
                "use_cases": ["gaming"],
                "price_usd": 69,
            },
            "Logitech MX Master 3S": {
                "wireless": True,
                "dpi_max": 8000,
                "weight_g": 141,
                "buttons": 7,
                "battery_life_hours": 70,
                "sensor": "Darkfield",
                "use_cases": ["productivity"],
                "price_usd": 99,
            },
            "Microsoft Arc Mouse": {
                "wireless": True,
                "dpi_max": 1800,
                "weight_g": 86,
                "buttons": 4,
                "battery_life_hours": 180,
                "sensor": "BlueTrack",
                "use_cases": ["productivity"],
                "price_usd": 79,
            },
            "Logitech G305": {
                "wireless": True,
                "dpi_max": 12000,
                "weight_g": 99,
                "buttons": 6,
                "battery_life_hours": 250,
                "sensor": "HERO",
                "use_cases": ["gaming"],
                "price_usd": 39,
            },
        }

        if wireless is not None:
            mice = {name: m for name, m in mice.items() if m["wireless"] == wireless}
        if use_case is not None:
            mice = {name: m for name, m in mice.items() if use_case in m["use_cases"]}
        if priceMax is not None:
            mice = {name: m for name, m in mice.items() if m["price_usd"] <= priceMax}

        return mice

    def GetAvailableKeyboards(self, wireless=None, layout=None, priceMax=None):
        keyboards = {
            "Logitech MX Keys S": {
                "wireless": True,
                "layout": "full",
                "switch_type": "Scissor",
                "backlit": True,
                "battery_life_days": 10,
                "connectivity": ["Bluetooth", "USB-C"],
                "use_cases": ["productivity"],
                "price_usd": 109,
            },
            "Keychron Q3 Pro": {
                "wireless": True,
                "layout": "tenkeyless",
                "switch_type": "Gateron G Pro (hot-swap)",
                "backlit": True,
                "battery_life_hours": 4000,
                "connectivity": ["Bluetooth", "USB-C"],
                "use_cases": ["productivity", "gaming"],
                "price_usd": 199,
            },
            "Corsair K70 RGB Pro": {
                "wireless": False,
                "layout": "full",
                "switch_type": "Cherry MX (hot-swap)",
                "backlit": True,
                "connectivity": ["USB-A"],
                "use_cases": ["gaming"],
                "price_usd": 139,
            },
            "SteelSeries Apex Pro TKL": {
                "wireless": False,
                "layout": "tenkeyless",
                "switch_type": "OmniPoint Adjustable",
                "backlit": True,
                "connectivity": ["USB-A"],
                "use_cases": ["gaming"],
                "price_usd": 179,
            },
            "Keychron K2 Pro": {
                "wireless": True,
                "layout": "75%",
                "switch_type": "Gateron G Pro (hot-swap)",
                "backlit": True,
                "battery_life_hours": 4000,
                "connectivity": ["Bluetooth", "USB-C"],
                "use_cases": ["productivity", "gaming"],
                "price_usd": 99,
            },
            "Wooting 60HE": {
                "wireless": False,
                "layout": "65%",
                "switch_type": "Lekker (Hall Effect)",
                "backlit": True,
                "connectivity": ["USB-C"],
                "use_cases": ["gaming"],
                "price_usd": 175,
            },
            "Logitech K120": {
                "wireless": False,
                "layout": "full",
                "switch_type": "Membrane",
                "backlit": False,
                "connectivity": ["USB-A"],
                "use_cases": ["productivity"],
                "price_usd": 19,
            },
        }

        if wireless is not None:
            keyboards = {name: k for name, k in keyboards.items() if k["wireless"] == wireless}
        if layout is not None:
            keyboards = {name: k for name, k in keyboards.items() if k["layout"] == layout}
        if priceMax is not None:
            keyboards = {name: k for name, k in keyboards.items() if k["price_usd"] <= priceMax}

        return keyboards
