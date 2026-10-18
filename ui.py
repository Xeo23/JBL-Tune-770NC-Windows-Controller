
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QFrame,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
)

from settings import normalize_address


ORANGE = "#ff6a00"
BG = "#0c0d0e"
TEXT = "#e5e6e8"
MUTED = "#777b80"


STYLE = f"""
QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI';
}}

QDialog {{
    background: {BG};
}}

QLabel {{
    background: transparent;
}}

QPushButton {{
    background: #151515;
    color: {TEXT};
    border: 1px solid #303030;
    border-radius: 12px;
    padding: 8px;
}}

QPushButton:hover {{
    background: #222426;
}}

QPushButton#mode {{
    background: #111315;
    border: 1px solid #303438;
    border-radius: 18px;
}}

QPushButton#mode[active="true"] {{
    background: #21140d;
    border: 2px solid {ORANGE};
}}

QProgressBar {{
    background: #292d31;
    border: 0;
    border-radius: 6px;
}}

QProgressBar::chunk {{
    background: {ORANGE};
    border-radius: 6px;
}}

QLineEdit {{
    background: #111315;
    border: 1px solid #303438;
    border-radius: 8px;
    padding: 9px;
}}

QDialogButtonBox QPushButton {{
    min-width: 100px;
}}
"""


def make_battery_icon(percentage, width=28, height=16):
    """Draw a minimal outlined battery with an orange charge indicator."""
    percentage = max(0, min(100, int(percentage)))

    pix = QPixmap(width, height)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Battery outline
    body_width = width - 5
    p.setPen(QPen(QColor(TEXT), 1.4))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(
        1, 2,
        body_width - 1, height - 4,
        3, 3,
    )

    # Battery terminal
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(TEXT))
    p.drawRoundedRect(
        body_width + 1,
        height // 2 - 2,
        3, 4,
        1, 1,
    )

    # Orange fill proportional to the battery percentage
    if percentage > 0:
        inner_width = body_width - 6
        fill_width = round(inner_width * percentage / 100)

        if fill_width > 0:
            p.setBrush(QColor(ORANGE))
            p.drawRoundedRect(
                4, 5,
                fill_width, height - 10,
                1, 1,
            )

    p.end()
    return QIcon(pix)


def make_icon(connected=True):
    color = ORANGE if connected else MUTED

    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    font = p.font()
    font.setFamily("Arial Black")
    font.setBold(True)
    font.setPixelSize(29)

    p.setFont(font)
    p.setPen(QPen(QColor(color)))
    p.drawText(
        pix.rect(),
        Qt.AlignmentFlag.AlignCenter,
        "JBL",
    )

    p.end()
    return QIcon(pix)


class SettingsDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Bluetooth Device Settings")
        self.setMinimumWidth(400)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout(self)

        title = QLabel("BLUETOOTH DEVICE")
        title.setStyleSheet(
            f"color: {ORANGE}; font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(title)

        hint = QLabel(
            "Enter the Bluetooth MAC address of your JBL Tune 770NC."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {MUTED};")
        layout.addWidget(hint)

        form = QFormLayout()

        self.address = QLineEdit(controller.address)
        self.address.setPlaceholderText("88:92:CC:D9:90:7D")
        self.address.setClearButtonEnabled(True)

        form.addRow("Bluetooth address", self.address)
        layout.addLayout(form)

        self.result = QLabel("")
        self.result.setWordWrap(True)
        self.result.setStyleSheet(f"color: {MUTED};")
        layout.addWidget(self.result)

        buttons = QDialogButtonBox()

        save = buttons.addButton(
            "Save Address",
            QDialogButtonBox.ButtonRole.AcceptRole,
        )
        test = buttons.addButton(
            "Test Connection",
            QDialogButtonBox.ButtonRole.ActionRole,
        )
        buttons.addButton(QDialogButtonBox.StandardButton.Cancel)

        save.clicked.connect(self.save)
        test.clicked.connect(self.test)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        controller.status_changed.connect(self._status)

    def save(self):
        try:
            self.controller.set_address(self.address.text())
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Bluetooth address",
                str(e),
            )
            return

        self.accept()

    def test(self):
        try:
            self.controller.set_address(self.address.text())
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Bluetooth address",
                str(e),
            )
            return

        self.result.setText("Testing RFCOMM channel 21…")
        self.controller.test_connection()

    def _status(self, text):
        if self.isVisible():
            self.result.setText(text)


class HeadsetWindow(QWidget):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.setWindowTitle("JBL Tune 770NC")
        self.setWindowIcon(make_icon())
        self.setFixedSize(360, 400)
        self.setStyleSheet(STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(7)

        # Header
        header = QHBoxLayout()

        brand = QLabel("JBL")
        brand.setStyleSheet(
            f"color: {ORANGE}; font-size: 24px; font-weight: 800;"
        )
        header.addWidget(brand)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedHeight(26)
        header.addWidget(line)

        name = QLabel("TUNE 770NC")
        name.setStyleSheet(
            "font-size: 16px; font-weight: 700; letter-spacing: 1px;"
        )
        header.addWidget(name, 1)

        settings = QPushButton("⚙")
        settings.setFixedSize(28, 28)
        settings.clicked.connect(self.show_settings)
        header.addWidget(settings)

        outer.addLayout(header)

        # Battery
        battery = QHBoxLayout()
        battery.setSpacing(8)

        self.battery_icon = QLabel()
        self.battery_icon.setFixedSize(24, 14)
        self.battery_icon.setPixmap(
            make_battery_icon(0, 24, 14).pixmap(24, 14)
        )
        battery.addWidget(self.battery_icon)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(12)

        self.battery_text = QLabel("—%")
        self.battery_text.setStyleSheet(
            f"color: {MUTED}; font-size: 18px; font-weight: 700;"
        )

        battery.addWidget(self.bar, 1)
        battery.addWidget(self.battery_text)
        outer.addLayout(battery)

        # Noise control
        title = QLabel("NOISE CONTROL")
        title.setStyleSheet(
            f"color: {ORANGE}; font-size: 16px; "
            "font-weight: 700; letter-spacing: 2px;"
        )
        outer.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(7)

        self.buttons = {}

        modes = [
            ("ANC", "anc", "◉", "ANC"),
            ("Ambient Aware", "ambient", "◌", "AMBIENTAWARE"),
            ("TalkThru", "talkthru", "▤", "TALKTHRU"),
            ("Off", "off", "⊘", "OFF"),
        ]

        for i, (label, cmd, icon, mode) in enumerate(modes):
            b = QPushButton()
            b.setObjectName("mode")
            b.setMinimumHeight(72)

            v = QVBoxLayout(b)
            v.setContentsMargins(4, 3, 4, 3)
            v.setSpacing(1)

            ico = QLabel(icon)
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ico.setStyleSheet("font-size: 25px;")

            txt = QLabel(label)
            txt.setAlignment(Qt.AlignmentFlag.AlignCenter)

            dot = QLabel("●")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dot.setStyleSheet(
                "color: #5b6065; font-size: 10px;"
            )

            v.addWidget(ico)
            v.addWidget(txt)
            v.addWidget(dot)

            b.clicked.connect(
                lambda checked=False, c=cmd: self.controller.run_command(c)
            )

            self.buttons[mode] = (b, ico, dot)
            grid.addWidget(b, i // 2, i % 2)

        outer.addLayout(grid, 1)

        # Status
        self.status = QLabel("Ready")
        self.status.setStyleSheet(
            f"color: {MUTED}; font-size: 10px;"
        )
        self.status.setWordWrap(False)
        outer.addWidget(self.status)

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet("color: #24272a;")
        outer.addWidget(rule)

        # Bottom controls
        bottom = QHBoxLayout()

        self.power = QPushButton("⏻")
        self.power.setFixedSize(42, 42)
        self.power.setStyleSheet("""
            QPushButton {
                font-size: 30px;
                font-family: "Segoe UI Symbol";
                padding: 0px;
            }
        """)
        self.power.clicked.connect(
            lambda: self.controller.run_command("poweroff")
        )
        bottom.addWidget(self.power)

        pl = QLabel("Power Off")
        pl.setStyleSheet("font-size: 13px; font-weight: 700;")
        bottom.addWidget(pl, 1)

        refresh = QPushButton("⟳")
        refresh.setFixedSize(42, 42)
        refresh.setStyleSheet("""
            QPushButton {
                font-size: 30px;
                font-family: "Segoe UI Symbol";
                padding: 0px;
            }
        """)
        refresh.clicked.connect(self.controller.refresh)
        bottom.addWidget(refresh)

        rl = QLabel("Refresh")
        rl.setStyleSheet("font-size: 13px; font-weight: 700;")
        bottom.addWidget(rl, 1)

        outer.addLayout(bottom)

    def show_settings(self):
        SettingsDialog(self.controller, self).exec()

    def update_status(self, text):
        self.status.setText(text)

    def update_battery(self, p):
        # Update the icon only when a valid battery reading is available.
        if p >= 0:
            self.battery_icon.setPixmap(
                make_battery_icon(p, 24, 14).pixmap(24, 14)
            )
        else:
            self.battery_icon.clear()

        self.bar.setValue(max(0, p))
        self.battery_text.setText(f"{p}%" if p >= 0 else "—%")
        self.battery_text.setStyleSheet(
            f"color: {ORANGE if p >= 0 else MUTED}; "
            "font-size: 18px; font-weight: 700;"
        )

    def update_mode(self, mode):
        for key, (b, ico, dot) in self.buttons.items():
            active = key == mode

            b.setProperty("active", active)
            b.style().unpolish(b)
            b.style().polish(b)

            ico.setStyleSheet(
                f"font-size: 35px; color: {ORANGE if active else TEXT};"
            )
            dot.setStyleSheet(
                f'font-size: 10px; color: {ORANGE if active else "#5b6065"};'
            )

    def update_connection(self, connected):
        self.power.setStyleSheet(
            f'background: {"#102017" if connected else "#1b1212"};'
            f'border: 1px solid {"#245b39" if connected else "#442020"};'
            "border-radius: 12px;"
            f'color: {"#45d483" if connected else "#ff443f"};'
            "font-size: 27px;"
        )

    def closeEvent(self, event):
        event.ignore()
        self.hide()
