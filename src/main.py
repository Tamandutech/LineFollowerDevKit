import asyncio
import os
import platform

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

if platform.system() == "Windows":
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


# Section: BLE Connection
UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
STREAM_UUID = "3a8328fc-3768-46d2-b371-b34864ce8025"


async def main():
    Terminal.log("Scanning for devices...")

    has_any_devices = False
    while not has_any_devices:
        devices = await BleakScanner.discover(5.0)
        devices = [i for i in devices if i.name]
        has_any_devices = bool(devices)
        if not has_any_devices:
            Terminal.log("No devices found. Retrying...", "YELLOW")

    enumerated_devices: list[BLEDevice] = []
    for index, d in enumerate(devices):
        Terminal.log(f"{index}. " + d.name, "CYAN")
        enumerated_devices.append(d)

    valid_input = False
    while not valid_input:
        option_input = int(Terminal.input("Enter the device number: ", "CYAN"))
        if option_input >= len(devices) or option_input < 0:
            Terminal.log("Invalid device number!", "RED")
            continue
        valid_input = True

    choosen_device = enumerated_devices[option_input]

    Terminal.log(f"Connecting to {choosen_device}...")

    def handle_disconnect(_: BleakClient):
        Terminal.log("Device was disconnected.", "RED")
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_rx(_: BleakGATTCharacteristic, data: bytearray):
        Terminal.log(f"received: {data}")

    async with BleakClient(
        choosen_device.address, disconnected_callback=handle_disconnect
    ) as client:
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)

        nus = client.services.get_service(UART_SERVICE_UUID)
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)
        services = client.services.characteristics
        services = {str(j) for i, j in services.items()}
        Terminal.log(f"Services: {services}", "GREEN")
        Terminal.log("Running bluetooth terminal:", "CYAN")
        Terminal.log("Type 'close' to exit the app.", "YELLOW")
        while True:
            command = Terminal.input("$ ", "CYAN")
            Terminal.log(f"Running {command}...")

            if command == "close":
                Terminal.log("Closing app...", "RED")
                break
            else:
                # for s in sliced(
                #     bytes(string=command, encoding="utf-8"),
                #     rx_char.max_write_without_response_size,
                # ):
                Terminal.log(f"{command.encode("utf-8")}")

                try:
                    await asyncio.wait_for(
                        client.write_gatt_char(
                            rx_char, command.encode("utf-8"), response=True
                        ),
                        timeout=5,
                    )
                except asyncio.TimeoutError:
                    Terminal.log(f"{command} timeout.", "RED")

                # await client.write_gatt_char(
                #     rx_char, command.encode("utf-8"), response=True
                # )

            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
        # asyncio.run(uart_terminal())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass
