
import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction

from ui import HeadsetWindow, make_icon
from controller import HeadsetController
from settings import load_config
from PySide6.QtGui import QAction, QActionGroup


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JBL Tune 770NC")
    app.setQuitOnLastWindowClosed(False)

    controller = HeadsetController(
        load_config().get("bluetooth_address", "")
    )
    window = HeadsetWindow(controller)

    controller.status_changed.connect(window.update_status)
    controller.battery_changed.connect(window.update_battery)
    controller.mode_changed.connect(window.update_mode)
    controller.connection_changed.connect(window.update_connection)

    def open_window():
        window.show()
        window.raise_()
        window.activateWindow()

    tray = QSystemTrayIcon(make_icon(False), app)
    tray.setToolTip("JBL Tune 770NC")

    controller.connection_changed.connect(
    lambda connected: tray.setIcon(make_icon(connected))
    )

    menu = QMenu()
    menu.setStyleSheet("""
        QMenu {
            background-color: #0c0d0e;
            color: #e5e6e8;
            border: 1px solid #303438;
            padding: 4px;
        }

        QMenu::item {
            background-color: transparent;
            color: #e5e6e8;
            padding: 7px 24px;
            border-radius: 4px;
        }

        QMenu::item:selected {
            background-color: #ff6a00;
            color: #0c0d0e;
        }

        QMenu::item:checked {
            background-color: #21140d;
            color: #ff6a00;
            font-weight: bold;
        }

        QMenu::item:checked:selected {
            background-color: #ff6a00;
            color: #0c0d0e;
        }

        QMenu::separator {
            height: 1px;
            background-color: #303438;
            margin: 4px 8px;
        }

        QMenu::item:disabled {
            color: #777b80;
        }
    """)
    menu.addAction("Open JBL Controller", open_window)
    menu.addSeparator()

    mode_group = QActionGroup(menu)
    mode_group.setExclusive(True)
    mode_actions = {}

    for label, command in [
        ("ANC", "anc"),
        ("Ambient Aware", "ambient"),
        ("TalkThru", "talkthru"),
        ("Off", "off"),
    ]:
        action = QAction(label, menu)
        action.setCheckable(True)
        mode_group.addAction(action)
        menu.addAction(action)

        mode_actions[command] = action

        action.triggered.connect(
            lambda checked=False, cmd=command:
                controller.run_command(cmd)
        )

    menu.addSeparator()

    power_action = QAction("Power Off Headphones", menu)
    power_action.triggered.connect(
        lambda: controller.run_command("poweroff")
    )
    menu.addAction(power_action)

    refresh_action = QAction("Refresh Status", menu)
    refresh_action.triggered.connect(controller.refresh)
    menu.addAction(refresh_action)

    settings_action = QAction("Bluetooth Device Settings…", menu)
    settings_action.triggered.connect(
        lambda: (open_window(), window.show_settings())
    )
    menu.addAction(settings_action)

    menu.addSeparator()

    exit_action = QAction("Exit", menu)
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)

    def update_tray_mode(mode):
        mode_map = {
            "ANC": "anc",
            "AmbientAware": "ambient",
            "AMBIENTAWARE": "ambient",
            "TalkThru": "talkthru",
            "TALKTHRU": "talkthru",
            "OFF": "off",
        }

        command = mode_map.get(str(mode).strip())

        if command in mode_actions:
            mode_actions[command].setChecked(True)


    controller.mode_changed.connect(update_tray_mode)
    menu.aboutToShow.connect(controller.refresh)    

    tray.setContextMenu(menu)

    tray.activated.connect(
        lambda reason: (
            controller.refresh()
            if reason == QSystemTrayIcon.ActivationReason.Trigger
            else open_window()
            if reason == QSystemTrayIcon.ActivationReason.DoubleClick
            else None
        )
    )

    tray.show()

    controller.refresh()
    #window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
