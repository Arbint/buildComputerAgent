from buildcomputer.agents.agent import Agent

class MonitorAgent(Agent):
    def __init__(self):
        super().__init__(
            name="MonitorAgent",
            description="Get a monitor recommendation based on use case and budget",
            properties={
                "price": {
                    "type": "integer",
                    "description": "the price limit"
                },
                "use_case": {
                    "type": "string",
                    "description": "intended use case, e.g. gaming, creative, office"
                }
            },
            system="""You are an expert in PC monitors. You help users select the best monitor for their needs.
                Consider the following factors when making recommendations:
                * Resolution and panel type
                * Refresh rate and response time for gaming
                * Color accuracy and coverage for creative work
                * Size and ergonomics
                * Connectivity (HDMI, DisplayPort, USB-C)
                * Price-to-performance ratio
            """
        )

    def ConfigureInput(self, **inputs):
        priceLimit = inputs.get("price", 1000)
        useCase = inputs.get("user_case", "regular use")
        self.messages.append({"role":"user", "content": f"any suggestions on getting a monitor under {priceLimit} that is used for: {useCase}"})

    def GetAgentTools(self):
        return [
            {
                "name": self.GetAvailableMonitors.__name__,
                "description": "get the available monitors",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "resolution": {
                            "type": "string",
                            "description": "filter by resolution, e.g. '1080p', '1440p', '4K'"
                        },
                        "use_case": {
                            "type": "string",
                            "description": "filter by use case: 'gaming', 'creative', 'office'"
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


    def GetAvailableMonitors(self, resolution=None, use_case=None, priceMax=None):
        monitors = {
            "LG 27GP950-B 27\" 4K 144Hz": {
                "size_inches": 27,
                "resolution": "4K",
                "panel": "Nano IPS",
                "refresh_rate_hz": 144,
                "response_time_ms": 1,
                "hdr": "VESA DisplayHDR 600",
                "color_coverage": {"srgb": 98, "dci_p3": 98},
                "ports": ["2x HDMI 2.1", "1x DisplayPort 1.4", "3x USB-A", "1x USB-B"],
                "use_cases": ["gaming", "creative"],
                "price_usd": 699,
            },
            "Dell S2722DGM 27\" 1440p 165Hz": {
                "size_inches": 27,
                "resolution": "1440p",
                "panel": "VA",
                "refresh_rate_hz": 165,
                "response_time_ms": 2,
                "hdr": "VESA DisplayHDR 400",
                "color_coverage": {"srgb": 99, "dci_p3": 90},
                "ports": ["2x HDMI 2.0", "1x DisplayPort 1.4"],
                "use_cases": ["gaming"],
                "price_usd": 279,
            },
            "ASUS ProArt PA279CRV 27\" 4K": {
                "size_inches": 27,
                "resolution": "4K",
                "panel": "IPS",
                "refresh_rate_hz": 60,
                "response_time_ms": 5,
                "hdr": "VESA DisplayHDR 400",
                "color_coverage": {"srgb": 100, "dci_p3": 99, "adobe_rgb": 99},
                "ports": ["2x HDMI 2.0", "1x DisplayPort 1.4", "1x USB-C 90W", "4x USB-A"],
                "use_cases": ["creative"],
                "price_usd": 549,
            },
            "Samsung Odyssey G7 32\" 1440p 240Hz": {
                "size_inches": 32,
                "panel": "VA",
                "resolution": "1440p",
                "refresh_rate_hz": 240,
                "response_time_ms": 1,
                "hdr": "VESA DisplayHDR 600",
                "color_coverage": {"srgb": 95, "dci_p3": 83},
                "ports": ["2x HDMI 2.0", "1x DisplayPort 1.4", "2x USB-A"],
                "use_cases": ["gaming"],
                "price_usd": 499,
            },
            "BenQ GW2490 24\" 1080p IPS": {
                "size_inches": 24,
                "resolution": "1080p",
                "panel": "IPS",
                "refresh_rate_hz": 100,
                "response_time_ms": 5,
                "hdr": None,
                "color_coverage": {"srgb": 99},
                "ports": ["1x HDMI 1.4", "1x DisplayPort 1.2", "1x VGA"],
                "use_cases": ["office"],
                "price_usd": 129,
            },
            "LG 34WP65C-B 34\" 1440p Ultrawide": {
                "size_inches": 34,
                "resolution": "1440p",
                "panel": "VA",
                "refresh_rate_hz": 160,
                "response_time_ms": 5,
                "hdr": "VESA DisplayHDR 400",
                "color_coverage": {"srgb": 99, "dci_p3": 90},
                "ports": ["2x HDMI 2.0", "1x DisplayPort 1.4", "2x USB-A", "1x USB-B"],
                "use_cases": ["gaming", "office"],
                "price_usd": 349,
            },
            "ASUS PA32UCG 32\" 4K 120Hz Pro": {
                "size_inches": 32,
                "resolution": "4K",
                "panel": "IPS",
                "refresh_rate_hz": 120,
                "response_time_ms": 4,
                "hdr": "VESA DisplayHDR 1400",
                "color_coverage": {"srgb": 100, "dci_p3": 99, "adobe_rgb": 99},
                "ports": ["4x HDMI 2.0", "2x DisplayPort 1.4", "1x USB-C 96W", "4x USB-A"],
                "use_cases": ["creative"],
                "price_usd": 1999,
            },
        }

        if resolution is not None:
            monitors = {name: m for name, m in monitors.items() if m["resolution"] == resolution}
        if use_case is not None:
            monitors = {name: m for name, m in monitors.items() if use_case in m["use_cases"]}
        if priceMax is not None:
            monitors = {name: m for name, m in monitors.items() if m["price_usd"] <= priceMax}

        return monitors
