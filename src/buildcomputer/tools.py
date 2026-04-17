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

            {
                "name": cls.GetCPUS.__name__,
                "description": "get the available cpus",
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
        motherboards ={
            "ASUS ROG Maximus Z790 Hero": {
                "color": "Black",
                "price_usd": 629,
                "socket": "LGA1700",
                "chipset": "Intel Z790",
                "memory_type": "DDR5",
                "memory_slots": 4,
                "memory_channels": 2,
                "max_memory_gb": 128,
                "max_memory_speed_mhz": 7800,
                "form_factor": "ATX",
            },
            "MSI MAG B650 Tomahawk WiFi": {
                "color": "Black",
                "price_usd": 229,
                "socket": "AM5",
                "chipset": "AMD B650",
                "memory_type": "DDR5",
                "memory_slots": 4,
                "memory_channels": 2,
                "max_memory_gb": 128,
                "max_memory_speed_mhz": 6600,
                "form_factor": "ATX",
            },
            "Gigabyte B760M DS3H": {
                "color": "Black",
                "price_usd": 109,
                "socket": "LGA1700",
                "chipset": "Intel B760",
                "memory_type": "DDR4",
                "memory_slots": 4,
                "memory_channels": 2,
                "max_memory_gb": 128,
                "max_memory_speed_mhz": 3200,
                "form_factor": "Micro-ATX",
            },
            "ASUS ProArt X670E Creator WiFi": {
                "color": "Black/Silver",
                "price_usd": 549,
                "socket": "AM5",
                "chipset": "AMD X670E",
                "memory_type": "DDR5",
                "memory_slots": 4,
                "memory_channels": 2,
                "max_memory_gb": 128,
                "max_memory_speed_mhz": 6400,
                "form_factor": "ATX",
            },
            "MSI MEG X299 XPOWER Gaming AC": {
                "color": "Black",
                "price_usd": 459,
                "socket": "LGA2066",
                "chipset": "Intel X299",
                "memory_type": "DDR4",
                "memory_slots": 8,
                "memory_channels": 4,
                "max_memory_gb": 256,
                "max_memory_speed_mhz": 4266,
                "form_factor": "ATX",
            }
        }

        return motherboards

    
    @classmethod
    def GetCPUS(cls):
        cpus = {
            "Intel Core i9-14900K": {
                "architecture": "Raptor Lake Refresh",
                "socket": "LGA1700",
                "cores": {"performance": 8, "efficient": 16, "total": 24},
                "threads": 32,
                "base_clock_ghz": {"performance": 3.2, "efficient": 2.4},
                "boost_clock_ghz": 6.0,
                "cache": {
                    "L1i_kb": 64,   # per P-core
                    "L1d_kb": 48,   # per P-core
                    "L2_mb": 32,
                    "L3_mb": 36,
                },
                "memory_type": "DDR5/DDR4",
                "memory_channels": 2,
                "tdp_w": 125,
                "max_tdp_w": 253,
                "price_usd": 549,
                "igpu": "Intel UHD Graphics 770",
            },
            "Intel Core i7-14700K": {
                "architecture": "Raptor Lake Refresh",
                "socket": "LGA1700",
                "cores": {"performance": 8, "efficient": 12, "total": 20},
                "threads": 28,
                "base_clock_ghz": {"performance": 3.4, "efficient": 2.5},
                "boost_clock_ghz": 5.6,
                "cache": {
                    "L1i_kb": 64,
                    "L1d_kb": 48,
                    "L2_mb": 28,
                    "L3_mb": 33,
                },
                "memory_type": "DDR5/DDR4",
                "memory_channels": 2,
                "tdp_w": 125,
                "max_tdp_w": 253,
                "price_usd": 379,
                "igpu": "Intel UHD Graphics 770",
            },
            "Intel Core i5-14600K": {
                "architecture": "Raptor Lake Refresh",
                "socket": "LGA1700",
                "cores": {"performance": 6, "efficient": 8, "total": 14},
                "threads": 20,
                "base_clock_ghz": {"performance": 3.5, "efficient": 2.6},
                "boost_clock_ghz": 5.3,
                "cache": {
                    "L1i_kb": 64,
                    "L1d_kb": 48,
                    "L2_mb": 20,
                    "L3_mb": 24,
                },
                "memory_type": "DDR5/DDR4",
                "memory_channels": 2,
                "tdp_w": 125,
                "max_tdp_w": 181,
                "price_usd": 299,
                "igpu": "Intel UHD Graphics 770",
            },
            "Intel Core i3-13100": {
                "architecture": "Raptor Lake",
                "socket": "LGA1700",
                "cores": {"performance": 4, "efficient": 0, "total": 4},
                "threads": 8,
                "base_clock_ghz": {"performance": 3.4, "efficient": None},
                "boost_clock_ghz": 4.5,
                "cache": {
                    "L1i_kb": 64,
                    "L1d_kb": 48,
                    "L2_mb": 5,
                    "L3_mb": 12,
                },
                "memory_type": "DDR5/DDR4",
                "memory_channels": 2,
                "tdp_w": 60,
                "max_tdp_w": 89,
                "price_usd": 139,
                "igpu": "Intel UHD Graphics 730",
            },
            "AMD Ryzen 9 7950X": {
                "architecture": "Zen 4",
                "socket": "AM5",
                "cores": {"total": 16},
                "threads": 32,
                "base_clock_ghz": 4.5,
                "boost_clock_ghz": 5.7,
                "cache": {
                    "L1i_kb": 32,   # per core
                    "L1d_kb": 32,   # per core
                    "L2_mb": 16,
                    "L3_mb": 64,
                },
                "memory_type": "DDR5",
                "memory_channels": 2,
                "tdp_w": 170,
                "max_tdp_w": 230,
                "price_usd": 549,
                "igpu": "AMD Radeon Graphics (RDNA 2)",
            },
            "AMD Ryzen 9 7900X": {
                "architecture": "Zen 4",
                "socket": "AM5",
                "cores": {"total": 12},
                "threads": 24,
                "base_clock_ghz": 4.7,
                "boost_clock_ghz": 5.6,
                "cache": {
                    "L1i_kb": 32,
                    "L1d_kb": 32,
                    "L2_mb": 12,
                    "L3_mb": 64,
                },
                "memory_type": "DDR5",
                "memory_channels": 2,
                "tdp_w": 170,
                "max_tdp_w": 230,
                "price_usd": 379,
                "igpu": "AMD Radeon Graphics (RDNA 2)",
            },
            "AMD Ryzen 7 7800X3D": {
                "architecture": "Zen 4 + 3D V-Cache",
                "socket": "AM5",
                "cores": {"total": 8},
                "threads": 16,
                "base_clock_ghz": 4.5,
                "boost_clock_ghz": 5.0,
                "cache": {
                    "L1i_kb": 32,
                    "L1d_kb": 32,
                    "L2_mb": 8,
                    "L3_mb": 96,    # 3D V-Cache stacked
                },
                "memory_type": "DDR5",
                "memory_channels": 2,
                "tdp_w": 120,
                "max_tdp_w": 162,
                "price_usd": 349,
                "igpu": "AMD Radeon Graphics (RDNA 2)",
            },
            "AMD Ryzen 5 7600X": {
                "architecture": "Zen 4",
                "socket": "AM5",
                "cores": {"total": 6},
                "threads": 12,
                "base_clock_ghz": 4.7,
                "boost_clock_ghz": 5.3,
                "cache": {
                    "L1i_kb": 32,
                    "L1d_kb": 32,
                    "L2_mb": 6,
                    "L3_mb": 32,
                },
                "memory_type": "DDR5",
                "memory_channels": 2,
                "tdp_w": 105,
                "max_tdp_w": 142,
                "price_usd": 229,
                "igpu": "AMD Radeon Graphics (RDNA 2)",
            },
            "AMD Threadripper PRO 7985WX": {
                "architecture": "Zen 4",
                "socket": "sTR5",
                "cores": {"total": 64},
                "threads": 128,
                "base_clock_ghz": 3.2,
                "boost_clock_ghz": 5.1,
                "cache": {
                    "L1i_kb": 32,
                    "L1d_kb": 32,
                    "L2_mb": 128,
                    "L3_mb": 256,
                },
                "memory_type": "DDR5",
                "memory_channels": 8,
                "tdp_w": 350,
                "max_tdp_w": 350,
                "price_usd": 5499,
                "igpu": None,
            },
            "Apple M3 Max": {
                "architecture": "ARM (Apple Silicon)",
                "socket": None,     # soldered on SoC
                "cores": {"performance": 12, "efficient": 4, "total": 16},
                "threads": 16,      # no SMT on Apple Silicon
                "base_clock_ghz": None,     # Apple does not publish
                "boost_clock_ghz": 4.05,
                "cache": {
                    "L1i_kb": 192,  # per P-core
                    "L1d_kb": 128,  # per P-core
                    "L2_mb": 48,
                    "L3_mb": None,  # uses unified SLC instead
                    "SLC_mb": 48,   # System Level Cache
                },
                "memory_type": "Unified LPDDR5",
                "memory_channels": 8,   # 400 GB/s bandwidth
                "tdp_w": 30,
                "max_tdp_w": 92,
                "price_usd": 1999,      # as part of MacBook Pro
                "igpu": "Apple 40-core GPU (integrated)",
            },
        }

        return cpus



    @classmethod
    def CallTool(cls, toolName, **toolInputs):
        method = getattr(cls, toolName)
        return method(**toolInputs)
