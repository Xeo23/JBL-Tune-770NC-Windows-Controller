<img width="451" height="577" alt="{7D9B2211-F9B4-4F10-8DD8-E5D744157960}" src="https://github.com/user-attachments/assets/81c14a56-6435-48e9-82d3-f4845902c4cc" />

<img width="322" height="418" alt="{9850114D-4F10-42E3-8F2B-FCBAD4A76B5D}" src="https://github.com/user-attachments/assets/9a6b2c6c-76b0-4afd-9bde-db3685ee7658" />

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
