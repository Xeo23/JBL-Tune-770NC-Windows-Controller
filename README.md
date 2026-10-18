# JBL Tune 770NC Windows Controller

A lightweight Windows system-tray controller for the **JBL Tune 770NC** headphones, built with Python and PySide6.

This project is a Windows port of my [JBL Tune 770NC Quickshell Widget](https://github.com/Xeo23/JBL_Tune_70_NC-Quickshell-Widget), bringing headphone controls to Windows with a dedicated interface and system-tray integration.

## Features

- Control ANC (Active Noise Cancelling).
- Switch between Ambient Aware and TalkThru modes.
- Turn noise control off.
- Power off the headphones.
- View headphone battery percentage.
- Access controls from the Windows system tray.
- Dark, JBL-orange-inspired interface.

## Requirements

- Windows
- Python 3.10 or newer
- PySide6
- JBL Tune 770NC headphones connected over Bluetooth

## Installation

Clone the repository:

```bash
git clone https://github.com/Xeo23/JBL-Tune-770NC-Windows-Controller
cd JBL-Tune-770NC-Windows-Controller
```

Install the dependencies:

```bash
py -m pip install PySide6
```

Run the application:

```bash
py main.py
```

## Usage

Launch the application and use the system-tray icon to access the controls. Connect your JBL Tune 770NC headphones over Bluetooth before using the controller.

## Credits and Acknowledgements

- **Original project:** [JBL Tune 770NC Quickshell Widget](https://github.com/Xeo23/JBL_Tune_70_NC-Quickshell-Widget) — the original project that inspired this Windows port.
- **Bluetooth protocol reference:** [JBL headphone control script by wielkiborsuk](https://gist.github.com/wielkiborsuk/f46f6792ce9bba167a0736a2cc5ad6ae) — this project uses parts of the original script and builds upon and enhances its implementation to integrate the functionality more effectively into a dedicated Windows application.

Please refer to the original sources for their respective licensing and attribution requirements.

## Disclaimer

This is an unofficial, community-developed project and is not affiliated with or endorsed by JBL or Harman.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
