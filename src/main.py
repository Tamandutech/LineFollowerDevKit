import asyncio
import os

from bleak import BleakScanner

os.system("color")  # Enable ANSI color codes on Windows


# Section: Terminal Print Functions
TERM_COLOR = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",  # orange on some systems
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "LIGHT_GRAY": "\033[37m",
    "DARK_GRAY": "\033[90m",
    "BRIGHT_RED": "\033[91m",
    "BRIGHT_GREEN": "\033[92m",
    "BRIGHT_YELLOW": "\033[93m",
    "BRIGHT_BLUE": "\033[94m",
    "BRIGHT_MAGENTA": "\033[95m",
    "BRIGHT_CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m",  # called to return to standard terminal text color
}


APP_TAG = f"{TERM_COLOR['BRIGHT_MAGENTA']}[LF_DevKit]{TERM_COLOR['RESET']}"


class Terminal:
    @staticmethod
    def log(message: str, color: str = "WHITE"):
        print(f"{APP_TAG} {TERM_COLOR[color]}{message}{TERM_COLOR['RESET']}")

    @staticmethod
    def input(message: str, color: str = "WHITE"):
        return input(f"{APP_TAG} {TERM_COLOR[color]}{message}{TERM_COLOR['RESET']}")


# Section: Main Function
async def main():
    Terminal.log("Scanning for devices...")

    has_any_devices = False
    while not has_any_devices:
        devices = await BleakScanner.discover(4.0, return_adv=True)
        devices = {k: v for k, v in devices.items() if v[0].name}
        has_any_devices = bool(devices)
        if not has_any_devices:
            Terminal.log("No devices found. Retrying...", "YELLOW")

    enumerated_devices = {}
    for index, d in enumerate(devices):
        Terminal.log(f"{index}. " + devices[d][0].name)
        enumerated_devices[index] = d

    valid_input = False
    while not valid_input:
        option_input = int(Terminal.input("Enter the device number: "))
        if option_input >= len(devices) or option_input < 0:
            Terminal.log("Invalid device number!", "RED")
            continue
        # else:
        valid_input = True

    choosen_device = enumerated_devices[option_input]
    Terminal.log(f"Connecting to {devices[choosen_device][0].name}...")


if __name__ == "__main__":
    asyncio.run(main())
