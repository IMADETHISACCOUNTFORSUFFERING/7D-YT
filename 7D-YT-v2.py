"""
7D-YT — V2

"""

import json, os, re, shutil, subprocess, sys, tarfile, threading, webbrowser, zipfile
import tempfile
import urllib.request
from io import BytesIO
from pathlib import Path

from PySide6.QtCore import (Qt, QThread, Signal, QObject, QTimer,
                             QPropertyAnimation, QEasingCurve, QSize, QPoint)
from PySide6.QtGui  import (QColor, QFont, QFontDatabase, QPainter, QPainterPath,
                             QPixmap, QLinearGradient, QBrush, QPen, QIcon,
                             QKeySequence)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFrame,
    QFileDialog, QStackedWidget, QScrollArea, QSizePolicy, QComboBox,
    QMessageBox, QGraphicsDropShadowEffect, QButtonGroup, QSpacerItem
)

# ================== palettes, colors n shi ============================
DARK_PALETTE = {
    "bg":       "#111111",
    "surface":  "#111111",
    "surface2": "#1A1A1A",
    "surface3": "#222222",
    "border":   "#2A2A2A",
    "border2":  "#111111",
    "red":      "#FF0000",
    "red_dim":  "#CC0000",
    "red_glow": "#A7474733",
    "text":     "#FFFFFF",
    "grey1":    "#BBBBBB",
    "grey2":    "#777777",
    "grey3":    "#833C3C",
    "green":    "#72D1B4",
    "amber":    "#D3A86F",
    "blue":     "#2979FF",
    "is_dark":  True,
}

LIGHT_PALETTE = {
    "bg":       "#FFFFFF",
    "surface":  "#FFFFFF",
    "surface2": "#F0F0F0",
    "surface3": "#E8E8E8",
    "border":   "#DDDDDD",
    "border2":  "#CCCCCC",
    "red":      "#D50000",
    "red_dim":  "#B71C1C",
    "red_glow": "#D5000033",
    "text":     "#0A0A0A",
    "grey1":    "#333333",
    "grey2":    "#666666",
    "grey3":    "#999999",
    "green":    "#00897B",
    "amber":    "#F57F17",
    "blue":     "#1565C0",
    "is_dark":  False,
}
# eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

C = dict(DARK_PALETTE)
C["white"] = C["text"]


def _make_stylesheet(p: dict) -> str:

    return f"""
* {{
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    color: {p['text']};
    outline: none;
}}
QMainWindow, QWidget#root {{
    background: {p['bg']};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: {p['surface2']};
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {p['grey3']};
    border-radius: 5px;
    min-height: 36px;
    margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p['red']};
}}
QScrollBar::handle:vertical:pressed {{
    background: {p['red_dim']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
    background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
QScrollBar:horizontal {{
    background: {p['surface2']};
    height: 10px;
    border-radius: 5px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {p['grey3']};
    border-radius: 5px;
    min-width: 36px;
    margin: 2px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {p['red']};
}}
QScrollBar::handle:horizontal:pressed {{
    background: {p['red_dim']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
    background: none;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}
QLineEdit {{
    background: {p['surface2']};
    border: 1px solid {p['border2']};
    border-radius: 10px;
    padding: 0 16px;
    font-size: 14px;
    color: {p['text']};
    selection-background-color: {p['red_dim']};
}}
QLineEdit:focus {{
    border-color: {p['red']};
}}
QLineEdit::placeholder {{
    color: {p['grey3']};
}}
QTextEdit {{
    background: {p['surface2']};
    border: 1px solid {p['border']};
    border-radius: 10px;
    padding: 12px;
    font-family: 'Consolas', 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px;
    color: {p['grey2']};
}}
QComboBox {{
    background: {p['surface2']};
    border: 1px solid {p['border2']};
    border-radius: 10px;
    padding: 0 16px;
    font-size: 13px;
    color: {p['text']};
    min-height: 44px;
}}
QComboBox:hover {{
    border-color: {p['grey3']};
}}
QComboBox:focus {{
    border-color: {p['red']};
}}
QComboBox::drop-down {{
    border: none;
    width: 32px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {p['grey2']};
    width: 0; height: 0;
}}
QComboBox QAbstractItemView {{
    background: {p['surface3']};
    border: 1px solid {p['border2']};
    border-radius: 10px;
    selection-background-color: {p['red_dim']};
    selection-color: {p['text']};
    padding: 4px;
    outline: none;
}}
QProgressBar {{
    background: {p['surface3']};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {p['red_dim']}, stop:1 {p['red']});
    border-radius: 4px;
}}
QLabel {{
    background: transparent;
}}
QToolTip {{
    background: {p['surface3']};
    border: 1px solid {p['border2']};
    color: {p['grey1']};
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
"""

APP_STYLE = _make_stylesheet(DARK_PALETTE)


# ================== light dark modes ===============
class ThemeManager:
   
    _listeners: list = []
    _dark: bool = True

    @classmethod
    def is_dark(cls) -> bool:
        return cls._dark

    @classmethod
    def register(cls, fn):
        
        cls._listeners.append(fn)

    @classmethod
    def toggle(cls):
        cls._dark = not cls._dark
        palette = DARK_PALETTE if cls._dark else LIGHT_PALETTE
        C.update(palette)
        C["white"] = C["text"]
        QApplication.instance().setStyleSheet(_make_stylesheet(palette))
        for fn in cls._listeners:
            try:
                fn(palette)
            except Exception:
                pass

# ============================================================================
#  widgets
# ============================================================================

def shadow(widget, radius=24, color="#000000", opacity=180, offset=(0, 4)):
    fx = QGraphicsDropShadowEffect(widget)
    fx.setBlurRadius(radius)
    c = QColor(color)
    c.setAlpha(opacity)
    fx.setColor(c)
    fx.setOffset(*offset)
    widget.setGraphicsEffect(fx)
    return fx


class Card(QFrame):
    def __init__(self, parent=None, radius=16):
        super().__init__(parent)
        self._radius = radius
        self._restyle(C)
        ThemeManager.register(self._restyle)

    def _restyle(self, p):
        self.setStyleSheet(f"""
            Card {{
                background: {p['surface']};
                border: 1px solid {p['border']};
                border-radius: {self._radius}px;
            }}
        """)


class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None, height=48):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restyle(C)
        ThemeManager.register(self._restyle)

    def _restyle(self, p):
        self.setStyleSheet(f"""
            PrimaryButton {{
                background: {p['red']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 24px;
                letter-spacing: 0.3px;
            }}
            PrimaryButton:hover {{
                background: {p['red_dim']};
            }}
            PrimaryButton:pressed {{
                background: {p['red_dim']};
            }}
            PrimaryButton:disabled {{
                background: {p['surface3']};
                color: {p['grey3']};
            }}
        """)


class GhostButton(QPushButton):
    def __init__(self, text, parent=None, height=44):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restyle(C)
        ThemeManager.register(self._restyle)

    def _restyle(self, p):
        self.setStyleSheet(f"""
            GhostButton {{
                background: {p['surface2']};
                color: {p['grey1']};
                border: 1px solid {p['border2']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 20px;
            }}
            GhostButton:hover {{
                background: {p['surface3']};
                border-color: {p['grey3']};
                color: {p['text']};
            }}
            GhostButton:pressed {{
                background: {p['border']};
            }}
            GhostButton:disabled {{
                color: {p['grey3']};
                border-color: {p['border']};
            }}
        """)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self._restyle(C)
        ThemeManager.register(self._restyle)

    def _restyle(self, p):
        self.setStyleSheet(f"background: {p['border']}; max-height: 1px; border: none;")


class Badge(QLabel):
    def __init__(self, text, color=None, parent=None):
        super().__init__(text, parent)
        self._badge_color = color
        self._restyle(C)
        ThemeManager.register(self._restyle)

    def _restyle(self, p):
        color = self._badge_color or p['surface3']
        self.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: {p['grey1']};
                border-radius: 6px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)


# ====================icons=====================================
class Icons:
    _cache: dict = {}

    @classmethod
    def get(cls, name: str, size: int = 20, color: str = "#FFFFFF") -> QIcon:
        key = (name, size, color)
        if key in cls._cache:
            return cls._cache[key]
        icon = cls._draw(name, size, color)
        cls._cache[key] = icon
        return icon

    @classmethod
    def px(cls, name: str, size: int = 20, color: str = "#FFFFFF") -> QPixmap:
        return cls.get(name, size, color).pixmap(size, size)

    @classmethod
    def _draw(cls, name: str, size: int, color: str) -> QIcon:
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(color)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(c))

        s = size
        m = s * 0.08         
        r = s - 2 * m        
        pen = QPen(c)

        def line_pen(width=1.8):
            lp = QPen(c)
            lp.setWidthF(width * s / 20)
            lp.setCapStyle(Qt.PenCapStyle.RoundCap)
            lp.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            return lp

        if name == "play":
            tri = QPainterPath()
            tri.moveTo(m + r * 0.18, m + r * 0.1)
            tri.lineTo(m + r * 0.92, m + r * 0.5)
            tri.lineTo(m + r * 0.18, m + r * 0.9)
            tri.closeSubpath()
            p.drawPath(tri)

        elif name == "download":
            p.setPen(Qt.PenStyle.NoPen)
            shaft_w = r * 0.22
            shaft_x = m + (r - shaft_w) / 2
            p.drawRoundedRect(
                shaft_x, m + r * 0.05,
                shaft_w, r * 0.52,
                shaft_w / 2, shaft_w / 2
            )
            head = QPainterPath()
            hcx = m + r / 2
            hy_top = m + r * 0.48
            hy_bot = m + r * 0.76
            head.moveTo(hcx - r * 0.38, hy_top)
            head.lineTo(hcx,            hy_bot)
            head.lineTo(hcx + r * 0.38, hy_top)
            head.closeSubpath()
            p.drawPath(head)
          
            p.setBrush(QBrush(c))
            bar_h = r * 0.1
            p.drawRoundedRect(
                m, m + r * 0.84,
                r, bar_h,
                bar_h / 2, bar_h / 2
            )

        elif name == "search":
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(2.0))
            p.drawEllipse(
                QPoint(int(m + r * 0.38), int(m + r * 0.38)),
                int(r * 0.34), int(r * 0.34)
            )
            p.drawLine(
                int(m + r * 0.64), int(m + r * 0.64),
                int(m + r * 0.92), int(m + r * 0.92)
            )

        elif name == "preview":
            
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(1.8))
           
            ep = QPainterPath()
            ep.moveTo(m + r * 0.05, m + r * 0.5)
            ep.quadTo(m + r * 0.5, m + r * 0.1, m + r * 0.95, m + r * 0.5)
            ep.quadTo(m + r * 0.5, m + r * 0.9, m + r * 0.05, m + r * 0.5)
            p.drawPath(ep)
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(
                QPoint(int(m + r / 2), int(m + r / 2)),
                int(r * 0.16), int(r * 0.16)
            )

        elif name == "add":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(2.2))
            cx, cy = m + r / 2, m + r / 2
            p.drawLine(int(cx), int(m + r * 0.15), int(cx), int(m + r * 0.85))
            p.drawLine(int(m + r * 0.15), int(cy), int(m + r * 0.85), int(cy))

        elif name == "close":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(2.0))
            p.drawLine(int(m + r * 0.18), int(m + r * 0.18),
                       int(m + r * 0.82), int(m + r * 0.82))
            p.drawLine(int(m + r * 0.82), int(m + r * 0.18),
                       int(m + r * 0.18), int(m + r * 0.82))

        elif name == "check":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(2.4))
            p.drawLine(int(m + r * 0.1),  int(m + r * 0.52),
                       int(m + r * 0.42), int(m + r * 0.82))
            p.drawLine(int(m + r * 0.42), int(m + r * 0.82),
                       int(m + r * 0.9),  int(m + r * 0.22))

        elif name == "sun":
            cx, cy = m + r / 2, m + r / 2
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPoint(int(cx), int(cy)), int(r * 0.22), int(r * 0.22))
            p.setPen(line_pen(1.6))
            import math
            for i in range(8):
                angle = math.radians(i * 45)
                x1 = cx + math.cos(angle) * r * 0.30
                y1 = cy + math.sin(angle) * r * 0.30
                x2 = cx + math.cos(angle) * r * 0.46
                y2 = cy + math.sin(angle) * r * 0.46
                p.drawLine(int(x1), int(y1), int(x2), int(y2))

        elif name == "moon":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addEllipse(m + r * 0.1, m + r * 0.05, r * 0.82, r * 0.9)
            cutout = QPainterPath()
            cutout.addEllipse(m + r * 0.34, m + r * 0.0, r * 0.72, r * 0.80)
            p.drawPath(path - cutout)

        elif name == "playlist":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(1.8))
            for frac in (0.28, 0.5, 0.72):
                p.drawLine(int(m + r * 0.1), int(m + r * frac),
                           int(m + r * 0.7), int(m + r * frac))
            # play icon
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            tri2 = QPainterPath()
            tri2.moveTo(m + r * 0.76, m + r * 0.38)
            tri2.lineTo(m + r * 0.96, m + r * 0.50)
            tri2.lineTo(m + r * 0.76, m + r * 0.62)
            tri2.closeSubpath()
            p.drawPath(tri2)

        elif name == "folder":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(m, m + r * 0.28, r, r * 0.65, r * 0.1, r * 0.1)
            p.drawPath(path)
            tab = QPainterPath()
            tab.addRoundedRect(m, m + r * 0.18, r * 0.4, r * 0.18, r * 0.06, r * 0.06)
            p.drawPath(tab)

        elif name == "video":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(m, m + r * 0.2, r * 0.68, r * 0.6, r * 0.1, r * 0.1)
            p.drawPath(path)
            tri3 = QPainterPath()
            tri3.moveTo(m + r * 0.72, m + r * 0.28)
            tri3.lineTo(m + r * 0.97, m + r * 0.50)
            tri3.lineTo(m + r * 0.72, m + r * 0.72)
            tri3.closeSubpath()
            p.drawPath(tri3)

        elif name == "music":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            # kms
            p.drawEllipse(QPoint(int(m + r * 0.28), int(m + r * 0.76)),
                          int(r * 0.22), int(r * 0.17))
            p.drawEllipse(QPoint(int(m + r * 0.72), int(m + r * 0.68)),
                          int(r * 0.22), int(r * 0.17))
            # ==
            p.setPen(line_pen(2.0))
            p.drawLine(int(m + r * 0.50), int(m + r * 0.76),
                       int(m + r * 0.50), int(m + r * 0.22))
            p.drawLine(int(m + r * 0.94), int(m + r * 0.68),
                       int(m + r * 0.94), int(m + r * 0.14))
            p.drawLine(int(m + r * 0.50), int(m + r * 0.22),
                       int(m + r * 0.94), int(m + r * 0.14))

        elif name == "reset":
            # ==
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(2.0))
            import math
            rect_f = (m + r * 0.1, m + r * 0.1, r * 0.8, r * 0.8)
            path = QPainterPath()
            path.arcMoveTo(*rect_f, 100)
            path.arcTo(*rect_f, 100, 250)
            p.drawPath(path)
            # ==
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            angle_rad = math.radians(100)
            ax = m + r * 0.5 + math.cos(angle_rad) * r * 0.4
            ay = m + r * 0.5 - math.sin(angle_rad) * r * 0.4
            arr = QPainterPath()
            arr.moveTo(ax - r * 0.14, ay - r * 0.06)
            arr.lineTo(ax + r * 0.08, ay + r * 0.14)
            arr.lineTo(ax + r * 0.14, ay - r * 0.14)
            arr.closeSubpath()
            p.drawPath(arr)

        elif name == "info":
            cx, cy = m + r / 2, m + r / 2
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(1.8))
            p.drawEllipse(QPoint(int(cx), int(cy)), int(r / 2), int(r / 2))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(c))
            p.drawEllipse(QPoint(int(cx), int(m + r * 0.32)), int(r * 0.08), int(r * 0.08))
            p.setPen(line_pen(1.8))
            p.drawLine(int(cx), int(m + r * 0.46), int(cx), int(m + r * 0.76))

        elif name == "clear":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(m + r * 0.12, m + r * 0.3, r * 0.76, r * 0.62, r * 0.08, r * 0.08)
            p.drawPath(path)
            # Lid
            p.setPen(line_pen(1.8))
            p.drawLine(int(m + r * 0.05), int(m + r * 0.26),
                       int(m + r * 0.95), int(m + r * 0.26))
            p.drawLine(int(m + r * 0.34), int(m + r * 0.26),
                       int(m + r * 0.38), int(m + r * 0.14))
            p.drawLine(int(m + r * 0.62), int(m + r * 0.26),
                       int(m + r * 0.66), int(m + r * 0.14))
            p.drawLine(int(m + r * 0.38), int(m + r * 0.14),
                       int(m + r * 0.62), int(m + r * 0.14))

        elif name == "dot_filled":
            cx, cy = m + r / 2, m + r / 2
            p.drawEllipse(QPoint(int(cx), int(cy)), int(r * 0.38), int(r * 0.38))

        elif name == "dot_empty":
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(line_pen(1.8))
            cx, cy = m + r / 2, m + r / 2
            p.drawEllipse(QPoint(int(cx), int(cy)), int(r * 0.36), int(r * 0.36))

        elif name == "save_image":
            p.setBrush(QBrush(c))
            p.setPen(Qt.PenStyle.NoPen)
            path = QPainterPath()
            path.addRoundedRect(m, m + r * 0.08, r, r * 0.72, r * 0.08, r * 0.08)
            p.drawPath(path)
            p.setPen(line_pen(1.8))
            p.drawLine(int(m + r * 0.15), int(m + r * 0.62),
                       int(m + r * 0.42), int(m + r * 0.35))
            p.drawLine(int(m + r * 0.42), int(m + r * 0.35),
                       int(m + r * 0.72), int(m + r * 0.62))
            p.setPen(Qt.PenStyle.NoPen)
            shaft_w = r * 0.18
            sx = m + (r - shaft_w) / 2
            p.drawRoundedRect(sx, m + r * 0.82, shaft_w, r * 0.1,
                              shaft_w / 2, shaft_w / 2)
            arr2 = QPainterPath()
            hcx2 = m + r / 2
            arr2.moveTo(hcx2 - r * 0.28, m + r * 0.80)
            arr2.lineTo(hcx2,             m + r * 0.96)
            arr2.lineTo(hcx2 + r * 0.28, m + r * 0.80)
            arr2.closeSubpath()
            p.drawPath(arr2)

        p.end()
        return QIcon(pm)


#=============ffmpeg===========================
FFMPEG_DIR = Path.home() / ".7d-yt" / "ffmpeg"

def find_ffmpeg():
    suffix = ".exe" if sys.platform == "win32" else ""
    bundled = FFMPEG_DIR / f"ffmpeg{suffix}"
    if bundled.exists():
        return str(bundled)
    return shutil.which("ffmpeg")

def ffmpeg_download_url():
    if sys.platform == "win32":
        return ("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/"
                "ffmpeg-master-latest-win64-gpl.zip", True)
    elif sys.platform == "darwin":
        return ("https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip", True)
    else:
        return ("https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz", False)

def extract_ffmpeg(archive: Path, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    suffix = ".exe" if sys.platform == "win32" else ""
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            for m in zf.namelist():
                if Path(m).name in (f"ffmpeg{suffix}", "ffmpeg.exe", "ffmpeg"):
                    out = dest / f"ffmpeg{suffix}"
                    out.write_bytes(zf.read(m))
                    if sys.platform != "win32": out.chmod(0o755)
                    return True
    else:
        with tarfile.open(archive) as tf:
            for m in tf.getmembers():
                if m.name.endswith("/ffmpeg") or m.name == "ffmpeg":
                    f = tf.extractfile(m)
                    if f:
                        out = dest / "ffmpeg"
                        out.write_bytes(f.read())
                        out.chmod(0o755)
                        return True
    return False

def which_ytdlp():
    for name in ("yt-dlp", "yt-dlp.exe"):
        r = subprocess.run(
            ["where" if sys.platform == "win32" else "which", name],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            return name
    return "yt-dlp"

YTDLP = which_ytdlp()


# ...

class FfmpegInstaller(QThread):
    progress  = Signal(float, str)   # !1
    log_line  = Signal(str)
    finished  = Signal(bool, str)    # !2

    def run(self):
        try:
            url, is_zip = ffmpeg_download_url()
            ext = ".zip" if is_zip else ".tar.xz"
            tmp = Path.home() / ".7d-yt" / f"ffmpeg_dl{ext}"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            self.log_line.emit(f"Source: {url}\n")

            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            ) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                done  = 0
                with open(tmp, "wb") as f:
                    while True:
                        buf = resp.read(65536)
                        if not buf: break
                        f.write(buf)
                        done += len(buf)
                        if total:
                            pct = done / total
                            mb_d = done / 1_048_576
                            mb_t = total / 1_048_576
                            self.progress.emit(pct, f"Downloading…  {mb_d:.1f} / {mb_t:.1f} MB")

            self.log_line.emit("Extracting binary…")
            self.progress.emit(0.97, "Extracting…")
            ok = extract_ffmpeg(tmp, FFMPEG_DIR)
            tmp.unlink(missing_ok=True)

            if ok:
                os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ.get("PATH", "")
                self.log_line.emit("✓  ffmpeg installed!")
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "Binary not found in archive.")
        except Exception as e:
            self.finished.emit(False, str(e))


class FetchWorker(QThread):
    done  = Signal(dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            r = subprocess.run(
                [YTDLP, "--dump-json", "--no-playlist", self.url],
                capture_output=True, text=True, timeout=30
            )
            if r.returncode != 0:
                self.error.emit(r.stderr[:400])
                return
            self.done.emit(json.loads(r.stdout))
        except Exception as e:
            self.error.emit(str(e))


class ThumbnailWorker(QThread):
    done  = Signal(QPixmap)
    error = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            from PIL import Image as PILImage
            req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = BytesIO(resp.read())
            img = PILImage.open(data).convert("RGB")
            img = img.resize((560, 315), PILImage.LANCZOS)
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            px = QPixmap()
            px.loadFromData(buf.read())
            self.done.emit(px)
        except Exception:
            self.error.emit()


class DownloadWorker(QThread):
    progress = Signal(float, str, str)   # !3
    log_line = Signal(str)
    done     = Signal()
    error    = Signal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            proc = subprocess.Popen(
                self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            pct_re   = re.compile(r"\[download\]\s+([\d.]+)%")
            speed_re = re.compile(r"at\s+([\d.]+\s*\w+/s)")
            eta_re   = re.compile(r"ETA\s+([\d:]+)")

            for line in proc.stdout:
                line = line.rstrip()
                if not line: continue
                self.log_line.emit(line)
                m = pct_re.search(line)
                if m:
                    ms = speed_re.search(line)
                    me = eta_re.search(line)
                    detail = "  ".join(filter(None, [
                        ms.group(1) if ms else "",
                        f"ETA {me.group(1)}" if me else ""
                    ]))
                    self.progress.emit(float(m.group(1)) / 100, m.group(1) + "%", detail)
            proc.wait()
            if proc.returncode == 0:
                self.done.emit()
            else:
                self.error.emit(f"yt-dlp exited with code {proc.returncode}")
        except FileNotFoundError:
            self.error.emit("yt-dlp not found.  Run:  pip install yt-dlp")
        except Exception as e:
            self.error.emit(str(e))



class PlaylistFetchWorker(QThread):
    
    item_ready = Signal(dict)   
    done       = Signal(int)    
    error      = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            r = subprocess.run(
                [YTDLP, "--dump-json", "--flat-playlist", self.url],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode != 0:
                self.error.emit(r.stderr[:400])
                return
            count = 0
            for line in r.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    self.item_ready.emit(json.loads(line))
                    count += 1
                except Exception:
                    pass
            self.done.emit(count)
        except Exception as e:
            self.error.emit(str(e))


class QueueDownloadWorker(QThread):
   
    item_started  = Signal(int, str)          
    item_progress = Signal(int, float, str, str)  
    item_log      = Signal(int, str)
    item_done     = Signal(int)
    item_error    = Signal(int, str)
    all_done      = Signal()

    def __init__(self, items, cmd_builder):
      
        super().__init__()
        self.items       = items
        self.cmd_builder = cmd_builder
        self._stop       = False

    def stop(self):
        self._stop = True

    def run(self):
        for idx, item in enumerate(self.items):
            if self._stop:
                break
            self.item_started.emit(idx, item.get("title", item["url"]))
            cmd = self.cmd_builder(item["url"], item["fmt"], item["res"], item["dest"])
            
            thumb_url = item.get("thumb_url", "")
            self.item_log.emit(idx, f"[CMD] {' '.join(cmd)}")
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1
                )
                pct_re   = re.compile(r"\[download\]\s+([\d.]+)%")
                speed_re = re.compile(r"at\s+([\d.]+\s*\w+/s)")
                eta_re   = re.compile(r"ETA\s+([\d:]+)")
                for line in proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    self.item_log.emit(idx, line)
                    m = pct_re.search(line)
                    if m:
                        ms = speed_re.search(line)
                        me = eta_re.search(line)
                        detail = "  ".join(filter(None, [
                            ms.group(1) if ms else "",
                            f"ETA {me.group(1)}" if me else ""
                        ]))
                        self.item_progress.emit(idx, float(m.group(1))/100, m.group(1)+"%", detail)
                proc.wait()
                if proc.returncode == 0:
                    self.item_done.emit(idx)
                else:
                    self.item_error.emit(idx, f"yt-dlp exited with code {proc.returncode}")
            except Exception as e:
                self.item_error.emit(idx, str(e))
        self.all_done.emit()


class ThumbnailSaveWorker(QThread):
   
    done  = Signal(str)   
    error = Signal(str)

    def __init__(self, thumb_url, dest_dir, title):
        super().__init__()
        self.thumb_url = thumb_url
        self.dest_dir  = dest_dir
        self.title     = title

    def run(self):
        try:
            from PIL import Image as PILImage
            req = urllib.request.Request(self.thumb_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = BytesIO(resp.read())
            img = PILImage.open(data).convert("RGB")
            safe = re.sub(r'[<>:"/\\|?*]', "_", self.title)[:80]
            out  = os.path.join(self.dest_dir, f"{safe}_thumbnail.jpg")
            img.save(out, "JPEG", quality=95)
            self.done.emit(out)
        except Exception as e:
            self.error.emit(str(e))



def _msg(parent, kind, title, text):

    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon({
        "info":  QMessageBox.Icon.Information,
        "warn":  QMessageBox.Icon.Warning,
        "crit":  QMessageBox.Icon.Critical,
    }.get(kind, QMessageBox.Icon.NoIcon))
    box.setStyleSheet("""
        QMessageBox {
            background: #1A1A1A;
        }
        QMessageBox QLabel {
            color: #FFFFFF;
            font-size: 13px;
            min-width: 280px;
        }
        QPushButton {
            background: #FF0000;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 20px;
            font-size: 13px;
            font-weight: 700;
            min-width: 80px;
        }
        QPushButton:hover { background: #CC0000; }
    """)
    box.exec()

# ───────────────────────────setup thingy──────────────────────────────────────────


class SetupPage(QWidget):
    complete = Signal()

    STEPS = ["Welcome", "Install ffmpeg", "Done"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._step = 0
        self._installer = None
        self._build()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

       
        self._step_bar = self._make_step_bar()
        root.addWidget(self._step_bar)

        # Content
        self._stack = QStackedWidget()
        self._stack.addWidget(self._make_welcome())
        self._stack.addWidget(self._make_install())
        self._stack.addWidget(self._make_done())
        root.addWidget(self._stack, 1)

        # Nav bar
        nav_card = QFrame()
        nav_card.setFixedHeight(72)
        nav_card.setStyleSheet(f"background: {C['surface']}; border-top: 1px solid {C['border']};")
        nav_layout = QHBoxLayout(nav_card)
        nav_layout.setContentsMargins(32, 0, 32, 0)

        self._back_btn = GhostButton("← Back")
        self._back_btn.setFixedWidth(110)
        self._back_btn.setEnabled(False)
        self._back_btn.clicked.connect(self._back)
        nav_layout.addWidget(self._back_btn)

        nav_layout.addStretch()

        self._skip_btn = QPushButton("Skip  (ffmpeg already installed)")
        self._skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['grey3']};
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{ color: {C['grey2']}; }}
        """)
        self._skip_btn.clicked.connect(self.complete.emit)
        nav_layout.addWidget(self._skip_btn)

        nav_layout.addStretch()

        self._next_btn = PrimaryButton("Install ffmpeg  →", height=44)
        self._next_btn.setFixedWidth(200)
        self._next_btn.clicked.connect(self._next)
        nav_layout.addWidget(self._next_btn)

        root.addWidget(nav_card)

    def _make_step_bar(self):
        bar = QFrame()
        bar.setFixedHeight(56)
        bar.setStyleSheet(f"background: {C['surface']}; border-bottom: 1px solid {C['border']};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(40, 0, 40, 0)
        lay.setSpacing(0)

        self._step_lbls = []
        for i, name in enumerate(self.STEPS):
            lbl = QLabel(f"{'●' if i==0 else '○'}  {name}")
            lbl.setStyleSheet(f"""
                font-size: 13px;
                font-weight: {'700' if i==0 else '400'};
                color: {C['red'] if i==0 else C['grey3']};
            """)
            self._step_lbls.append(lbl)
            lay.addWidget(lbl)
            if i < len(self.STEPS) - 1:
                sep = QLabel("  ──────  ")
                sep.setStyleSheet(f"color: {C['border2']}; font-size: 11px;")
                lay.addWidget(sep)
        lay.addStretch()
        return bar

    def _refresh_steps(self):
        for i, lbl in enumerate(self._step_lbls):
            if i < self._step:
                sym, color, weight = "✓", C['green'], "700"
            elif i == self._step:
                sym, color, weight = "●", C['red'], "700"
            else:
                sym, color, weight = "○", C['grey3'], "400"
            lbl.setText(f"{sym}  {self.STEPS[i]}")
            lbl.setStyleSheet(f"font-size: 13px; font-weight: {weight}; color: {color};")

    # ── Step pages ────────────────────────────────────────────────────────────
    def _make_welcome(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(80, 60, 80, 40)
        lay.setSpacing(0)

        title = QLabel("Welcome to 7D-YT")
        title.setStyleSheet(f"font-size: 30px; font-weight: 800; color: {C['white']}; margin-bottom: 20px;")
        lay.addWidget(title)

        body = QLabel(
            "This wizard will install <b>ffmpeg</b> — required to merge video &amp; audio tracks\n"
            "and convert files to MP3. It's free, open-source, and only installed for your user.\n"
        )
        body.setStyleSheet(f"font-size: 15px; color: {C['grey1']}; line-height: 1.6;")
        body.setWordWrap(True)
        lay.addWidget(body)

        lay.addSpacing(24)

        path_card = Card()
        path_card.setStyleSheet(f"""
            Card {{
                background: {C['surface2']};
                border: 1px solid {C['border2']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        pc_lay = QVBoxLayout(path_card)
        pc_lay.setSpacing(6)
        pc_lbl = QLabel("ffmpeg will be saved to:")
        pc_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        pc_lay.addWidget(pc_lbl)
        pc_path = QLabel(str(FFMPEG_DIR))
        pc_path.setStyleSheet(f"""
            font-family: 'Consolas', monospace;
            font-size: 13px;
            color: {C['red']};
        """)
        pc_lay.addWidget(pc_path)
        lay.addWidget(path_card)

        lay.addSpacing(24)

        plat = {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")
        plat_color = {"Windows": "#0078D4", "macOS": "#555", "Linux": "#E95420"}.get(plat, C['surface3'])
        badge = Badge(f"  Detected OS: {plat}  ", color=plat_color)
        badge.setFixedHeight(32)
        lay.addWidget(badge, alignment=Qt.AlignmentFlag.AlignLeft)

        lay.addSpacing(16)
        note = QLabel("No admin or sudo rights required.")
        note.setStyleSheet(f"font-size: 12px; color: {C['grey3']};")
        lay.addWidget(note)

        lay.addStretch()
        return w

    def _make_install(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(80, 60, 80, 40)
        lay.setSpacing(0)

        title = QLabel("⬇  Installing ffmpeg")
        title.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {C['white']}; margin-bottom: 16px;")
        lay.addWidget(title)

        self._inst_status = QLabel("Connecting…")
        self._inst_status.setStyleSheet(f"font-size: 14px; color: {C['grey1']}; margin-bottom: 12px;")
        lay.addWidget(self._inst_status)

        self._inst_bar = QProgressBar()
        self._inst_bar.setFixedHeight(8)
        self._inst_bar.setRange(0, 1000)
        self._inst_bar.setValue(0)
        self._inst_bar.setTextVisible(False)
        lay.addWidget(self._inst_bar)
        lay.addSpacing(20)

        self._inst_log = QTextEdit()
        self._inst_log.setReadOnly(True)
        self._inst_log.setFixedHeight(220)
        lay.addWidget(self._inst_log)

        lay.addStretch()
        return w

    def _make_done(self):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(80, 60, 80, 40)
        lay.setSpacing(0)

        title = QLabel("All set!")
        title.setStyleSheet(f"font-size: 30px; font-weight: 800; color: {C['green']}; margin-bottom: 20px;")
        lay.addWidget(title)

        body = QLabel(
            "ffmpeg is installed and ready to go.\n\n"
            "You can now download YouTube videos as MP4 or extract\n"
            "audio as high-quality MP3 files."
        )
        body.setStyleSheet(f"font-size: 15px; color: {C['grey1']}; line-height: 1.6;")
        lay.addWidget(body)

        lay.addSpacing(28)

        suffix = ".exe" if sys.platform == "win32" else ""
        path_lbl = QLabel(f"Installed at:  {FFMPEG_DIR / f'ffmpeg{suffix}'}")
        path_lbl.setStyleSheet(f"""
            font-family: 'Consolas', monospace;
            font-size: 12px;
            color: {C['grey3']};
        """)
        lay.addWidget(path_lbl)
        lay.addStretch()
        return w

    # ── nav ───────────────────────────────────────────────────────────────────
    def _next(self):
        if self._step == 0:
            self._step = 1
            self._stack.setCurrentIndex(1)
            self._refresh_steps()
            self._next_btn.setEnabled(False)
            self._back_btn.setEnabled(False)
            self._skip_btn.setEnabled(False)
            self._start_install()
        elif self._step == 1:
            # retry
            self._start_install()

    def _back(self):
        self._step = max(0, self._step - 1)
        self._stack.setCurrentIndex(self._step)
        self._refresh_steps()
        if self._step == 0:
            self._back_btn.setEnabled(False)
            self._next_btn.setText("Install ffmpeg  →")
            self._next_btn.setEnabled(True)
            self._skip_btn.setEnabled(True)

    def _start_install(self):
        self._inst_status.setStyleSheet(f"font-size: 14px; color: {C['grey1']};")
        self._inst_status.setText("Connecting…")
        self._inst_bar.setValue(0)
        self._inst_log.clear()
        self._next_btn.setText("Installing…")
        self._next_btn.setEnabled(False)

        self._installer = FfmpegInstaller()
        self._installer.progress.connect(self._on_inst_progress)
        self._installer.log_line.connect(self._on_inst_log)
        self._installer.finished.connect(self._on_inst_done)
        self._installer.start()

    def _on_inst_progress(self, pct, label):
        self._inst_bar.setValue(int(pct * 1000))
        self._inst_status.setText(label)

    def _on_inst_log(self, line):
        self._inst_log.append(line)

    def _on_inst_done(self, ok, msg):
        if ok:
            self._inst_bar.setValue(1000)
            self._inst_status.setText("✓  Installation complete!")
            self._inst_status.setStyleSheet(f"font-size: 14px; color: {C['green']};")
            self._step = 2
            self._stack.setCurrentIndex(2)
            self._refresh_steps()
            self._next_btn.setText("Open 7D-YT  →")
            self._next_btn.setEnabled(True)
            self._next_btn.clicked.disconnect()
            self._next_btn.clicked.connect(self.complete.emit)
            self._skip_btn.setEnabled(False)
        else:
            self._inst_status.setText(f"Failed: {msg}")
            self._inst_status.setStyleSheet(f"font-size: 14px; color: {C['red']};")
            self._inst_log.append(f"\n[ERROR] {msg}")
            self._next_btn.setText("Retry →")
            self._next_btn.setEnabled(True)
            self._back_btn.setEnabled(True)
            self._skip_btn.setEnabled(True)



# ============== Main downloader page ==================


class DownloaderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formats          = []
        self.save_dir         = str(Path.home() / "Downloads")
        self._fetch_worker    = None
        self._dl_worker       = None
        self._thumb_worker    = None
        self._thumb_save_w    = None
        self._queue_dl_worker = None
        self._queue           = []           
        self._last_thumb_url  = ""
        self._last_title      = ""
        self._last_thumb_px   = None        
        self._build()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

       
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        body = QWidget()
        self._body_widget = body
        body.setStyleSheet(f"background: {C['bg']};")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(32, 24, 32, 40)
        body_lay.setSpacing(16)

        body_lay.addWidget(self._make_url_card())
        body_lay.addWidget(self._make_info_card())
        body_lay.addWidget(self._make_settings_card())
        body_lay.addWidget(self._make_dir_card())
        body_lay.addWidget(self._make_progress_card())
        body_lay.addWidget(self._make_dl_button())
        body_lay.addWidget(self._make_queue_card())
        body_lay.addWidget(self._make_log_card())
        body_lay.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll, 1)

    def _make_header(self):
        self._header = QFrame()
        self._header.setFixedHeight(68)
        self._restyle_header(C)
        ThemeManager.register(self._restyle_header)

        lay = QHBoxLayout(self._header)
        lay.setContentsMargins(20, 0, 28, 0)

        # ── reset ────────────────────────────
        self._logo_btn = QPushButton()
        self._logo_btn.setFixedSize(44, 44)
        self._logo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._logo_btn.setToolTip("Click to reset the app")
        self._logo_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 22px;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255,0,0,0.12);
            }
            QPushButton:pressed {
                background: rgba(255,0,0,0.22);
            }
        """)

        # if icon not found
        logo_icon = self._make_logo_icon()
        self._logo_btn.setIcon(logo_icon)
        self._logo_btn.setIconSize(QSize(36, 36))
        self._logo_btn.clicked.connect(self._on_logo_click)
        lay.addWidget(self._logo_btn)
        lay.addSpacing(8)

        self._title_lbl = QLabel("7D-YT")
        self._title_lbl.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {C['text']}; letter-spacing: -0.5px;")
        ThemeManager.register(lambda p, w=self._title_lbl: w.setStyleSheet(
            f"font-size: 20px; font-weight: 800; color: {p['text']}; letter-spacing: -0.5px;"))
        lay.addWidget(self._title_lbl)

        lay.addStretch()

        # light // dark
        self._theme_btn = QPushButton("  Light mode")
        self._theme_btn.setIcon(Icons.get("sun", 16, C["grey1"]))
        self._theme_btn.setIconSize(QSize(16, 16))
        self._theme_btn.setFixedHeight(34)
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._restyle_theme_btn(C)
        ThemeManager.register(self._restyle_theme_btn)
        self._theme_btn.clicked.connect(self._toggle_theme)
        lay.addWidget(self._theme_btn)
        lay.addSpacing(12)

        # ffmpeg status
        ffmpeg_ok = find_ffmpeg() is not None
        badge_text = "ffmpeg ✓" if ffmpeg_ok else "ffmpeg missing"
        badge_color = C['surface3'] if ffmpeg_ok else "#5C1A1A"
        badge_fg = C['green'] if ffmpeg_ok else C['red']
        self._ffbadge = QLabel(f"  {badge_text}  ")
        self._ffbadge.setStyleSheet(f"""
            QLabel {{
                background: {badge_color};
                color: {badge_fg};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }}
        """)
        lay.addWidget(self._ffbadge)

        return self._header

    def _make_logo_icon(self) -> QIcon:
       
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search = [
            os.path.join(script_dir, "logo.png"),
            os.path.join(script_dir, "logo.ico"),
            os.path.join(script_dir, "logo.jpg"),
            os.path.join(script_dir, "youtube_logo.png"),
            os.path.join(script_dir, "youtube_logo.ico"),
            os.path.join(os.getcwd(), "logo.png"),
            os.path.join(os.getcwd(), "logo.ico"),
            os.path.join(os.getcwd(), "logo.jpg"),
        ]
        print("[icon] script_dir:", script_dir)
        print("[icon] files found:", [p for p in search if os.path.exists(p)])
        for full in search:
            if os.path.exists(full):
                px = QPixmap(full).scaled(
                    72, 72,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                if not px.isNull():
                    print("[icon] using:", full)
                    return QIcon(px)

        # ====== Draw if no icon =============
        size = 72
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        
        p.setBrush(QBrush(QColor("#FF0000")))
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(4, 14, size - 8, size - 28, 10, 10)
        p.drawPath(path)

        
        p.setBrush(QBrush(QColor("#FFFFFF")))
        tri = QPainterPath()
        cx, cy = size / 2, size / 2
        tri.moveTo(cx - 10, cy - 13)
        tri.lineTo(cx + 14, cy)
        tri.lineTo(cx - 10, cy + 13)
        tri.closeSubpath()
        p.drawPath(tri)
        p.end()

        return QIcon(px)

    def _on_logo_click(self):
        
        # an
        btn = self._logo_btn
        original_style = btn.styleSheet()
        btn.setStyleSheet(original_style + "QPushButton { background: rgba(255,0,0,0.25); }")

        def restore():
            btn.setStyleSheet(original_style)
        QTimer.singleShot(180, restore)
        w = self.parent()
        while w and not isinstance(w, QMainWindow):
            w = w.parent()
        if w and hasattr(w, "reset_app"):
            w.reset_app()

    def _restyle_header(self, p):
        self._header.setStyleSheet(f"""
            QFrame {{
                background: {p['surface']};
                border-bottom: 1px solid {p['border']};
            }}
        """)

    def _restyle_theme_btn(self, p):
        label = "  Dark mode" if not p.get("is_dark", True) else "  Light mode"
        icon_name = "moon" if not p.get("is_dark", True) else "sun"
        self._theme_btn.setText(label)
        self._theme_btn.setIcon(Icons.get(icon_name, 16, p["grey1"]))
        self._theme_btn.setIconSize(QSize(16, 16))
        self._theme_btn.setStyleSheet(f"""
            QPushButton {{
                background: {p['surface2']};
                color: {p['grey1']};
                border: 1px solid {p['border2']};
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background: {p['surface3']};
                color: {p['text']};
            }}
        """)

    def _toggle_theme(self):
        ThemeManager.toggle()
        # purr meoww nyaa meow
        self._body_widget.setStyleSheet(f"background: {C['bg']};")
        # nyaa purr nyaa
        self.status_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C['grey2']};")
        self.pct_lbl.setStyleSheet(f"font-size: 13px; color: {C['grey3']};")
        self.speed_lbl.setStyleSheet(f"font-size: 11px; color: {C['grey3']};")
        self.fmt_desc.setStyleSheet(f"font-size: 11px; color: {C['grey3']}; margin-top: 2px;")
        self.res_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        self.video_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {C['text']};")
        self.video_meta.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        self.thumb_lbl.setStyleSheet(f"background: {C['surface2']}; border-radius: 16px 16px 0 0;")

    def _make_url_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        top_row = QHBoxLayout()
        lbl = QLabel("YouTube URL  /  Playlist")
        lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {C['grey3']}; letter-spacing: 1px;")
        top_row.addWidget(lbl)
        top_row.addStretch()

        self.playlist_chk = QPushButton("  Playlist mode")
        self.playlist_chk.setIcon(Icons.get("playlist", 15, C["grey2"]))
        self.playlist_chk.setIconSize(QSize(15, 15))
        self.playlist_chk.setCheckable(True)
        self.playlist_chk.setFixedHeight(28)
        self.playlist_chk.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_playlist_btn(False)
        self.playlist_chk.toggled.connect(self._style_playlist_btn)
        top_row.addWidget(self.playlist_chk)
        lay.addLayout(top_row)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste a YouTube video or playlist link here…")
        self.url_input.setFixedHeight(48)
        self.url_input.returnPressed.connect(self._fetch)
        row.addWidget(self.url_input, 1)

        self.fetch_btn = GhostButton("Fetch Info", height=48)
        self.fetch_btn.setFixedWidth(120)
        self.fetch_btn.clicked.connect(self._fetch)
        row.addWidget(self.fetch_btn)

        self.add_queue_btn = GhostButton("  Queue", height=48)
        self.add_queue_btn.setIcon(Icons.get("add", 16, C["grey1"]))
        self.add_queue_btn.setIconSize(QSize(16, 16))
        self.add_queue_btn.setFixedWidth(90)
        self.add_queue_btn.setToolTip("Add fetched video(s) to the download queue")
        self.add_queue_btn.setEnabled(False)
        self.add_queue_btn.clicked.connect(self._add_to_queue)
        row.addWidget(self.add_queue_btn)

        self.preview_btn = PrimaryButton("  Preview", height=48)
        self.preview_btn.setIcon(Icons.get("preview", 18))
        self.preview_btn.setIconSize(QSize(18, 18))
        self.preview_btn.setFixedWidth(110)
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._preview)
        row.addWidget(self.preview_btn)

        lay.addLayout(row)
        return card

    def _style_playlist_btn(self, checked):
        if checked:
            self.playlist_chk.setStyleSheet(f"""
                QPushButton {{
                    background: {C['red_dim']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 0 10px;
                }}
            """)
        else:
            self.playlist_chk.setStyleSheet(f"""
                QPushButton {{
                    background: {C['surface3']};
                    color: {C['grey2']};
                    border: 1px solid {C['border']};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 0 10px;
                }}
                QPushButton:hover {{ color: {C['grey1']}; background: {C['border2']}; }}
            """)

    def _make_info_card(self):
        self.info_card = Card()
        lay = QVBoxLayout(self.info_card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # !1
        self.thumb_lbl = QLabel()
        self.thumb_lbl.setFixedHeight(0)
        self.thumb_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_lbl.setStyleSheet(f"background: {C['surface2']}; border-radius: 16px 16px 0 0;")
        self.thumb_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.thumb_lbl.setToolTip("Click to save thumbnail image")
        self.thumb_lbl.mousePressEvent = lambda e: self._save_thumbnail()

        # !2
        self._thumb_overlay = QLabel("  Save Thumbnail", self.thumb_lbl)
        self._thumb_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_overlay.setStyleSheet(f"""
            QLabel {{
                background: rgba(0,0,0,0.55);
                color: white;
                font-size: 15px;
                font-weight: 700;
                border-radius: 12px;
                padding: 8px 20px;
            }}
        """)
        self._thumb_overlay.hide()

        def _enter(e, lbl=self._thumb_overlay):
            lbl.setGeometry(
                self.thumb_lbl.width()//2 - 120,
                self.thumb_lbl.height()//2 - 24, 240, 48
            )
            lbl.show()
        def _leave(e, lbl=self._thumb_overlay):
            lbl.hide()

        self.thumb_lbl.enterEvent = _enter
        self.thumb_lbl.leaveEvent = _leave

        lay.addWidget(self.thumb_lbl)

        text_area = QWidget()
        text_area.setStyleSheet("background: transparent;")
        tl = QVBoxLayout(text_area)
        tl.setContentsMargins(24, 20, 24, 20)
        tl.setSpacing(6)

        self.video_title = QLabel("Enter a URL above and click Fetch Info")
        self.video_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {C['text']};")
        self.video_title.setWordWrap(True)
        tl.addWidget(self.video_title)

        self.video_meta = QLabel("")
        self.video_meta.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        tl.addWidget(self.video_meta)

        lay.addWidget(text_area)
        return self.info_card

    def _make_settings_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        hdr = QLabel("DOWNLOAD SETTINGS")
        hdr.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {C['grey3']}; letter-spacing: 1px;")
        lay.addWidget(hdr)

        lay.addWidget(Divider())

        row = QHBoxLayout()
        row.setSpacing(32)

        # Format
        fmt_col = QVBoxLayout()
        fmt_col.setSpacing(10)
        fmt_lbl = QLabel("Format")
        fmt_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        fmt_col.addWidget(fmt_lbl)

        # Format dropdown
        self.fmt_combo = QComboBox()
        self.fmt_combo.setFixedWidth(210)
        self.fmt_combo.addItem(Icons.get("video", 16, C["grey1"]), "  MP4   — video",   "mp4")
        self.fmt_combo.addItem(Icons.get("video", 16, C["grey1"]), "  MKV   — video",   "mkv")
        self.fmt_combo.addItem(Icons.get("video", 16, C["grey1"]), "  WEBM  — video",   "webm")
        self.fmt_combo.insertSeparator(3)
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  MP3   — audio",   "mp3")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  WAV   — audio",   "wav")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  FLAC  — audio",   "flac")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  AAC   — audio",   "aac")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  OPUS  — audio",   "opus")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  M4A   — audio",   "m4a")
        self.fmt_combo.addItem(Icons.get("music", 16, C["grey1"]), "  OGG   — audio",   "vorbis")
        self.fmt_combo.currentIndexChanged.connect(self._on_format)
        fmt_col.addWidget(self.fmt_combo)

        self.fmt_desc = QLabel("")
        self.fmt_desc.setStyleSheet(f"font-size: 11px; color: {C['grey3']}; margin-top: 2px;")
        fmt_col.addWidget(self.fmt_desc)
        row.addLayout(fmt_col, 1)

        # Res / Quality
        res_col = QVBoxLayout()
        res_col.setSpacing(10)
        self.res_lbl = QLabel("Resolution")
        self.res_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey2']};")
        res_col.addWidget(self.res_lbl)
        self.res_combo = QComboBox()
        self.res_combo.addItem("Best available")
        self.res_combo.setFixedWidth(210)
        res_col.addWidget(self.res_combo)
        res_col.addStretch()
        row.addLayout(res_col)

        lay.addLayout(row)
        self._on_format()   
        return card

    def _make_dir_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        hdr = QLabel("SAVE LOCATION")
        hdr.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {C['grey3']}; letter-spacing: 1px;")
        lay.addWidget(hdr)
        lay.addWidget(Divider())

        row = QHBoxLayout()
        row.setSpacing(10)
        self.dir_input = QLineEdit(self.save_dir)
        self.dir_input.setFixedHeight(44)
        row.addWidget(self.dir_input, 1)
        browse = GhostButton("  Browse", height=44)
        browse.setIcon(Icons.get("folder", 16, C["grey1"]))
        browse.setIconSize(QSize(16, 16))
        browse.setFixedWidth(120)
        browse.clicked.connect(self._browse)
        row.addWidget(browse)
        lay.addLayout(row)
        return card

    def _make_progress_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        top = QHBoxLayout()
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C['grey2']};")
        top.addWidget(self.status_lbl)
        top.addStretch()
        self.pct_lbl = QLabel("")
        self.pct_lbl.setStyleSheet(f"font-size: 13px; color: {C['grey3']};")
        top.addWidget(self.pct_lbl)
        lay.addLayout(top)

        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(6)
        self.prog_bar.setRange(0, 1000)
        self.prog_bar.setValue(0)
        self.prog_bar.setTextVisible(False)
        lay.addWidget(self.prog_bar)

        self.speed_lbl = QLabel("")
        self.speed_lbl.setStyleSheet(f"font-size: 11px; color: {C['grey3']};")
        lay.addWidget(self.speed_lbl)
        return card

    def _make_dl_button(self):
        self.dl_btn = PrimaryButton("   Download", height=56)
        self.dl_btn.setIcon(Icons.get("download", 22))
        self.dl_btn.setIconSize(QSize(22, 22))
        self.dl_btn.setEnabled(False)
        self.dl_btn.setStyleSheet(self.dl_btn.styleSheet() + """
            PrimaryButton {
                font-size: 16px;
                border-radius: 14px;
                letter-spacing: 0.5px;
            }
        """)
        self.dl_btn.clicked.connect(self._download)
        shadow(self.dl_btn, radius=32, color="#FF0000", opacity=60, offset=(0, 6))
        return self.dl_btn

    def _make_queue_card(self):
        self._queue_card = Card()
        lay = QVBoxLayout(self._queue_card)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        lbl = QLabel("DOWNLOAD QUEUE")
        lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {C['grey3']}; letter-spacing: 1px;")
        hdr.addWidget(lbl)

        self._queue_count_lbl = QLabel("0 items")
        self._queue_count_lbl.setStyleSheet(f"font-size: 11px; color: {C['grey3']};")
        hdr.addWidget(self._queue_count_lbl)
        hdr.addStretch()

        clr_q = QPushButton("Clear all")
        clr_q.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_q.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {C['grey3']};
                border: none; font-size: 11px; }}
            QPushButton:hover {{ color: {C['grey2']}; }}
        """)
        clr_q.setIcon(Icons.get("clear", 14, C["grey3"]))
        clr_q.setIconSize(QSize(14, 14))
        clr_q.clicked.connect(self._clear_queue)
        hdr.addWidget(clr_q)
        lay.addLayout(hdr)

        lay.addWidget(Divider())

        # Scrollable list of queue rows
        self._queue_scroll = QScrollArea()
        self._queue_scroll.setWidgetResizable(True)
        self._queue_scroll.setFixedHeight(180)
        self._queue_scroll.setStyleSheet("background: transparent; border: none;")
        self._queue_inner = QWidget()
        self._queue_inner.setStyleSheet("background: transparent;")
        self._queue_layout = QVBoxLayout(self._queue_inner)
        self._queue_layout.setContentsMargins(0, 0, 0, 0)
        self._queue_layout.setSpacing(4)
        self._queue_layout.addStretch()
        self._queue_scroll.setWidget(self._queue_inner)
        lay.addWidget(self._queue_scroll)

        self._queue_empty_lbl = QLabel("No items in queue. Fetch a video and click + Queue.")
        self._queue_empty_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey3']}; padding: 16px 0;")
        self._queue_empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._queue_empty_lbl)

        # Start queue button
        self._start_queue_btn = PrimaryButton("  Download All  (0)", height=46)
        self._start_queue_btn.setIcon(Icons.get("download", 18))
        self._start_queue_btn.setIconSize(QSize(18, 18))
        self._start_queue_btn.setEnabled(False)
        self._start_queue_btn.clicked.connect(self._start_queue)
        lay.addWidget(self._start_queue_btn)

        # lot of item progress bar meow
        self._queue_prog = QProgressBar()
        self._queue_prog.setFixedHeight(6)
        self._queue_prog.setRange(0, 1000)
        self._queue_prog.setValue(0)
        self._queue_prog.setTextVisible(False)
        self._queue_prog.hide()
        lay.addWidget(self._queue_prog)

        self._queue_status_lbl = QLabel("")
        self._queue_status_lbl.setStyleSheet(f"font-size: 11px; color: {C['grey2']};")
        self._queue_status_lbl.hide()
        lay.addWidget(self._queue_status_lbl)

        return self._queue_card

    def _make_log_card(self):
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 16, 24, 16)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        lbl = QLabel("LOG")
        lbl.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {C['grey3']}; letter-spacing: 1px;")
        hdr.addWidget(lbl)
        hdr.addStretch()
        clr = QPushButton("Clear")
        clr.setCursor(Qt.CursorShape.PointingHandCursor)
        clr.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C['grey3']};
                border: none;
                font-size: 11px;
            }}
            QPushButton:hover {{ color: {C['grey2']}; }}
        """)
        clr.clicked.connect(lambda: self.log_box.clear())
        hdr.addWidget(clr)
        lay.addLayout(hdr)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFixedHeight(130)
        lay.addWidget(self.log_box)
        return card

   
    def _log(self, msg):
        self.log_box.append(msg)

    def _set_status(self, text, color=None):
        color = color or C['grey2']
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {color};")

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, "Save to", self.save_dir)
        if path:
            self.save_dir = path
            self.dir_input.setText(path)

    def _preview(self):
        url = self.url_input.text().strip()
        if url:
            webbrowser.open(url)

    # ── Format metadata ───────────────────────────────────────────────────────
    _AUDIO_FMTS = {"mp3", "wav", "flac", "aac", "opus", "m4a", "vorbis"}

    _FMT_DESC = {
        "mp4":    "H.264/AAC · widely compatible",
        "mkv":    "Matroska · any codec, lossless container",
        "webm":   "VP9/Opus · open format, smaller files",
        "mp3":    "Lossy · universal compatibility",
        "wav":    "Lossless PCM · large files, no quality loss",
        "flac":   "Lossless compressed · best quality/size balance",
        "aac":    "Lossy · better quality than MP3 at same bitrate",
        "opus":   "Lossy · excellent quality at low bitrates",
        "m4a":    "AAC in MPEG-4 container · Apple ecosystem",
        "vorbis": "Lossy OGG · open source alternative to MP3",
    }

    _AUDIO_QUALITY = {
        "mp3":    ["Best (320kbps)", "256kbps", "192kbps", "128kbps", "96kbps"],
        "wav":    ["Best (lossless)"],
        "flac":   ["Best (lossless)"],
        "aac":    ["Best (256kbps)", "192kbps", "128kbps", "96kbps"],
        "opus":   ["Best (160kbps)", "128kbps", "96kbps", "64kbps"],
        "m4a":    ["Best (256kbps)", "192kbps", "128kbps"],
        "vorbis": ["Best (320kbps)", "256kbps", "192kbps", "128kbps"],
    }

    def _current_fmt(self):
       
        return self.fmt_combo.currentData() or "mp4"

    def _on_format(self):
        fmt = self._current_fmt()
        self.fmt_desc.setText(self._FMT_DESC.get(fmt, ""))

        if fmt in self._AUDIO_FMTS:
            self.res_lbl.setText("Quality")
            self.res_combo.clear()
            for q in self._AUDIO_QUALITY.get(fmt, ["Best"]):
                self.res_combo.addItem(q)
        else:
            self.res_lbl.setText("Resolution")
            self._populate_res()

    def _populate_res(self):
        self.res_combo.clear()
        self.res_combo.addItem("Best available")
        if not self.formats:
            return
        heights = sorted(
            {f["height"] for f in self.formats
             if f.get("height") and f.get("vcodec", "none") != "none"},
            reverse=True
        )
        for h in heights:
            self.res_combo.addItem(f"{h}p")

    # paranoia pa paranoiaiaia
    def _fetch(self):
        url = self.url_input.text().strip()
        if not url:
            _msg(self, "warn", "No URL", "Please paste a YouTube URL first.")
            return
        if self._fetch_worker and self._fetch_worker.isRunning():
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching…")
        self.preview_btn.setEnabled(False)
        self.add_queue_btn.setEnabled(False)
        self.dl_btn.setEnabled(False)
        self.prog_bar.setValue(0)
        self.pct_lbl.setText("")
        self.speed_lbl.setText("")

        if self.playlist_chk.isChecked():
            self._set_status("Fetching playlist…", C['amber'])
            self._playlist_items = []
            self._fetch_worker = PlaylistFetchWorker(url)
            self._fetch_worker.item_ready.connect(self._on_playlist_item)
            self._fetch_worker.done.connect(self._on_playlist_done)
            self._fetch_worker.error.connect(self._on_fetch_error)
            self._fetch_worker.start()
        else:
            self._set_status("Fetching video info…", C['amber'])
            self._fetch_worker = FetchWorker(url)
            self._fetch_worker.done.connect(self._on_fetch_done)
            self._fetch_worker.error.connect(self._on_fetch_error)
            self._fetch_worker.start()

    def _on_playlist_item(self, item):
        self._playlist_items.append(item)
        count = len(self._playlist_items)
        self._set_status(f"Fetched {count} items…", C['amber'])

    def _on_playlist_done(self, count):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Info")
        self.add_queue_btn.setEnabled(True)
        if count == 0:
            self._set_status("No items found", C['red'])
            return
        # -
        first = self._playlist_items[0]
        self.video_title.setText(f"Playlist: {count} videos")
        self.video_meta.setText(f"First: {first.get('title', '')[:80]}")
        self.dl_btn.setEnabled(True)
        self._set_status(f"Playlist ready — {count} videos", C['green'])
        self._log(f"[INFO] Playlist fetched: {count} items")

    def _on_fetch_error(self, msg):
        self._set_status("Error fetching info", C['red'])
        self._log(f"[ERROR] {msg}")
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Info")

    def _on_fetch_done(self, info):
        self.formats = info.get("formats", [])
        title    = info.get("title", "Unknown")
        channel  = info.get("uploader", "")
        duration = info.get("duration", 0)
        views    = info.get("view_count", 0)
        mins, secs = divmod(int(duration), 60)
        hrs, mins  = divmod(mins, 60)
        dur_str   = f"{hrs}:{mins:02d}:{secs:02d}" if hrs else f"{mins}:{secs:02d}"
        views_str = f"{views:,}" if views else "N/A"

        self.video_title.setText(title[:100] + ("…" if len(title) > 100 else ""))
        self.video_meta.setText(f"{channel}  ·  {dur_str}  ·  {views_str} views")

        self._on_format()   # refresh res
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch Info")
        self.preview_btn.setEnabled(True)
        self.dl_btn.setEnabled(True)
        self._set_status(f"Ready", C['green'])
        self._log(f"[INFO] Fetched: {title}")

        # Thumbnail
        thumb_url = None
        for t in reversed(info.get("thumbnails") or []):
            u = t.get("url", "")
            if u.startswith("http"):
                thumb_url = u
                break
        if not thumb_url:
            thumb_url = info.get("thumbnail", "")
        self._last_thumb_url = thumb_url
        self._last_title     = title
        if thumb_url:
            self.thumb_lbl.setText("Loading thumbnail…")
            self.thumb_lbl.setFixedHeight(60)
            self._thumb_worker = ThumbnailWorker(thumb_url)
            self._thumb_worker.done.connect(self._on_thumb)
            self._thumb_worker.error.connect(lambda: self.thumb_lbl.setText(""))
            self._thumb_worker.start()
        self.add_queue_btn.setEnabled(True)

    def _on_thumb(self, px):
        self._last_thumb_px = px
        self.thumb_lbl.setPixmap(
            px.scaled(self.info_card.width(), 315,
                      Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                      Qt.TransformationMode.SmoothTransformation)
        )
        self.thumb_lbl.setFixedHeight(280)
        self.thumb_lbl.setText("")

    def _save_thumbnail(self):
        if not self._last_thumb_url:
            return
        dest = self.dir_input.text().strip() or self.save_dir
        self._thumb_save_w = ThumbnailSaveWorker(self._last_thumb_url, dest, self._last_title)
        self._thumb_save_w.done.connect(lambda path: _msg(self, "info", "Thumbnail Saved", f"Saved to:\n{path}"))
        self._thumb_save_w.error.connect(lambda e: _msg(self, "crit", "Error", f"Could not save thumbnail:\n{e}"))
        self._thumb_save_w.start()

    # ── Download ──────────────────────────────────────────────────────────────
    def _download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if self._dl_worker and self._dl_worker.isRunning():
            _msg(self, "info", "In Progress", "A download is already running.")
            return

        fmt  = self._current_fmt()
        res  = self.res_combo.currentText()
        dest = self.dir_input.text().strip() or self.save_dir

        cmd = self._build_cmd(url, fmt, res, dest)
        self._log(f"[CMD] {' '.join(cmd)}")

        self.dl_btn.setEnabled(False)
        self.prog_bar.setValue(0)
        self.pct_lbl.setText("0%")
        self.speed_lbl.setText("")
        self._set_status("Starting download…", C['amber'])

        self._dl_worker = DownloadWorker(cmd)
        self._dl_worker.progress.connect(self._on_dl_progress)
        self._dl_worker.log_line.connect(self._log)
        self._dl_worker.done.connect(self._on_dl_done)
        self._dl_worker.error.connect(self._on_dl_error)
        self._dl_worker.start()

    def _build_cmd(self, url, fmt, res, dest):
        out = os.path.join(dest, "%(title)s.%(ext)s")
        cmd = [YTDLP, "--newline", "-o", out, "--no-playlist"]
        fp = find_ffmpeg()
        if fp:
            cmd += ["--ffmpeg-location", str(Path(fp).parent)]

        if fmt in self._AUDIO_FMTS:
            # Audio-only extraction
            cmd += ["-x", "--audio-format", fmt if fmt != "vorbis" else "vorbis"]

            
            if "lossless" in res.lower():
                pass  
            elif "kbps" in res.lower():
                kbps = re.search(r"(\d+)kbps", res)
                if kbps:
                    cmd += ["--audio-quality", kbps.group(1) + "k"]
            else:
                cmd += ["--audio-quality", "0"]  # best

           
            if fmt == "vorbis":
                cmd += ["--audio-format", "vorbis",
                        "--postprocessor-args", "ffmpeg:-c:a libvorbis"]

           
            cmd += ["--convert-thumbnails", "jpg"]

            if fmt in {"mp3", "m4a", "flac", "aac"}:
                cmd += [
                    "--embed-thumbnail",
                    "--add-metadata",
        
                    "--ppa", "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf scale='min(1000,iw)':-2",
                ]
            elif fmt == "opus":
               
                cmd += [
                    "--embed-thumbnail",
                    "--add-metadata",
                    "--ppa", "EmbedThumbnail+ffmpeg_o:-c:v mjpeg -vf scale='min(1000,iw)':-2",
                ]
            else:
               
                cmd += ["--write-thumbnail"]

        else:
            # Video formats
            if res == "Best available":
                if fmt == "webm":
                    cmd += ["-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best"]
                else:
                    cmd += ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"]
            else:
                h = res.replace("p", "")
                if fmt == "webm":
                    cmd += ["-f",
                            f"bestvideo[height<={h}][ext=webm]+bestaudio[ext=webm]"
                            f"/best[height<={h}][ext=webm]/best[height<={h}]"]
                else:
                    cmd += ["-f",
                            f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]"
                            f"/best[height<={h}][ext=mp4]/best[height<={h}]"]
            cmd += ["--merge-output-format", fmt]

        cmd.append(url)
        return cmd

    # ── Queue management ─────────────────────────────────────────────────────
    def _add_to_queue(self):
        fmt  = self._current_fmt()
        res  = self.res_combo.currentText()
        dest = self.dir_input.text().strip() or self.save_dir

        items_to_add = []

        if self.playlist_chk.isChecked() and hasattr(self, "_playlist_items"):
            for item in self._playlist_items:
                url  = item.get("url") or item.get("webpage_url", "")
                if not url:
                    continue
               
                if not url.startswith("http"):
                    url = f"https://www.youtube.com/watch?v={url}"
                items_to_add.append({
                    "url":       url,
                    "title":     item.get("title", url),
                    "fmt":       fmt,
                    "res":       res,
                    "dest":      dest,
                    "thumb_url": item.get("thumbnail", ""),
                })
        else:
            url = self.url_input.text().strip()
            if not url:
                return
            items_to_add.append({
                "url":       url,
                "title":     self._last_title or url,
                "fmt":       fmt,
                "res":       res,
                "dest":      dest,
                "thumb_url": self._last_thumb_url,
            })

        for item in items_to_add:
            self._queue.append(item)
            self._add_queue_row(item)

        self._refresh_queue_ui()

    def _add_queue_row(self, item):
        # Remove empty-state label
        self._queue_empty_lbl.hide()
        self._queue_scroll.show()

        row_w = QWidget()
        row_w.setStyleSheet(f"""
            QWidget {{
                background: {C['surface2']};
                border-radius: 8px;
            }}
        """)
        row_w.setFixedHeight(44)
        rl = QHBoxLayout(row_w)
        rl.setContentsMargins(12, 0, 12, 0)
        rl.setSpacing(10)

        # Status dot
        dot = QLabel()
        dot.setFixedSize(14, 14)
        dot.setPixmap(Icons.px("dot_filled", 10, C["grey3"]))
        rl.addWidget(dot)

        # Title
        title_lbl = QLabel(item["title"][:60] + ("…" if len(item["title"]) > 60 else ""))
        title_lbl.setStyleSheet(f"font-size: 12px; color: {C['grey1']};")
        rl.addWidget(title_lbl, 1)

        # Format badge
        fmt_lbl = QLabel(item["fmt"].upper())
        fmt_lbl.setStyleSheet(f"""
            QLabel {{
                background: {C['surface3']};
                color: {C['grey2']};
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: 700;
            }}
        """)
        rl.addWidget(fmt_lbl)

        # Remove button
        rm = QPushButton("")
        rm.setIcon(Icons.get("close", 14, C["grey3"]))
        rm.setIconSize(QSize(14, 14))
        rm.setFixedSize(24, 24)
        rm.setCursor(Qt.CursorShape.PointingHandCursor)
        rm.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {C['grey3']};
                border: none; font-size: 12px; }}
            QPushButton:hover {{ color: {C['red']}; }}
        """)
        idx = len(self._queue) - 1

        def _remove(checked=False, i=idx, w=row_w):
            if i < len(self._queue):
                self._queue.pop(i)
            w.setParent(None)
            self._refresh_queue_ui()

        rm.clicked.connect(_remove)
        rl.addWidget(rm)

        # Insert before the stretch
        self._queue_layout.insertWidget(self._queue_layout.count() - 1, row_w)

    def _clear_queue(self):
        self._queue.clear()
        while self._queue_layout.count() > 1:
            item = self._queue_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._refresh_queue_ui()

    def _refresh_queue_ui(self):
        n = len(self._queue)
        self._queue_count_lbl.setText(f"{n} item{'s' if n != 1 else ''}")
        self._start_queue_btn.setText(f"  Download All  ({n})")
        self._start_queue_btn.setEnabled(n > 0)
        if n == 0:
            self._queue_empty_lbl.show()
            self._queue_scroll.hide()
        else:
            self._queue_empty_lbl.hide()
            self._queue_scroll.show()

    def _start_queue(self):
        if not self._queue:
            return
        if self._queue_dl_worker and self._queue_dl_worker.isRunning():
            _msg(self, "info", "Running", "Queue is already downloading.")
            return

        self._start_queue_btn.setEnabled(False)
        self._queue_prog.setValue(0)
        self._queue_prog.show()
        self._queue_status_lbl.show()
        self.dl_btn.setEnabled(False)

        items = list(self._queue)
        self._queue_dl_worker = QueueDownloadWorker(items, self._build_cmd)
        self._queue_dl_worker.item_started.connect(self._on_qitem_started)
        self._queue_dl_worker.item_progress.connect(self._on_qitem_progress)
        self._queue_dl_worker.item_log.connect(lambda i, line: self._log(f"[{i+1}] {line}"))
        self._queue_dl_worker.item_done.connect(self._on_qitem_done)
        self._queue_dl_worker.item_error.connect(self._on_qitem_error)
        self._queue_dl_worker.all_done.connect(self._on_queue_all_done)
        self._queue_dl_worker.start()

    def _on_qitem_started(self, idx, title):
        self._queue_status_lbl.setText(f"[{idx+1}/{len(self._queue)}]  {title[:60]}")
        self._queue_prog.setValue(0)
        self._set_status(f"Queue: {idx+1}/{len(self._queue)}", C['amber'])

    def _on_qitem_progress(self, idx, pct, pct_str, detail):
        self._queue_prog.setValue(int(pct * 1000))
        self._queue_status_lbl.setText(
            f"[{idx+1}/{len(self._queue)}]  {pct_str}  {detail}"
        )

    def _on_qitem_done(self, idx):
        self._log(f"[DONE] Item {idx+1} complete.")

    def _on_qitem_error(self, idx, msg):
        self._log(f"[ERROR] Item {idx+1}: {msg}")

    def _on_queue_all_done(self):
        self._queue_prog.setValue(1000)
        self._queue_status_lbl.setText("✓  All items downloaded!")
        self._set_status("✓  Queue complete!", C['green'])
        self._start_queue_btn.setEnabled(True)
        self.dl_btn.setEnabled(True)
        _msg(self, "info", "Queue Done", f"All {len(self._queue)} items downloaded!\nSaved to: {self.save_dir}")

    def _on_dl_progress(self, pct, pct_str, detail):
        self.prog_bar.setValue(int(pct * 1000))
        self.pct_lbl.setText(pct_str)
        self.speed_lbl.setText(detail)
        self._set_status("Downloading…", C['amber'])

    def _on_dl_done(self):
        self.prog_bar.setValue(1000)
        self.pct_lbl.setText("100%")
        self.speed_lbl.setText("")
        self._set_status("✓  Download complete!", C['green'])
        self._log("[DONE] Download finished successfully.")
        self.dl_btn.setEnabled(True)
        _msg(self, "info", "Done", f"Download complete!\nSaved to:\n{self.save_dir}")

    def _on_dl_error(self, msg):
        self._set_status("Download failed", C['red'])
        self._log(f"[ERROR] {msg}")
        self.dl_btn.setEnabled(True)
        _msg(self, "crit", "Error", msg)


# ─────────────────────────────────────────────────────────────────────────────
#  Main window
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("7D-YT")
        self.resize(860, 800)
        self.setMinimumSize(720, 640)

        # icon or draw
        self.setWindowIcon(self._make_window_icon())

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        self._root_lay = QVBoxLayout(central)
        self._root_lay.setContentsMargins(0, 0, 0, 0)
        self._root_lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._root_lay.addWidget(self._stack)

        if find_ffmpeg() is None:
            self._setup = SetupPage()
            self._setup.complete.connect(self._launch_main)
            self._stack.addWidget(self._setup)
            self._stack.setCurrentWidget(self._setup)
        else:
            os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ.get("PATH", "")
            self._launch_main()

    def _make_window_icon(self) -> QIcon:
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search = [
            os.path.join(script_dir, "logo.ico"),
            os.path.join(script_dir, "logo.png"),
            os.path.join(script_dir, "logo.jpg"),
            os.path.join(script_dir, "youtube_logo.ico"),
            os.path.join(script_dir, "youtube_logo.png"),
            os.path.join(os.getcwd(), "logo.ico"),
            os.path.join(os.getcwd(), "logo.png"),
            os.path.join(os.getcwd(), "logo.jpg"),
        ]
        print("[window icon] script_dir:", script_dir)
        print("[window icon] files found:", [p for p in search if os.path.exists(p)])
        for full in search:
            if os.path.exists(full):
                icon = QIcon(full)
                if not icon.isNull():
                    print("[window icon] using:", full)
                    return icon

        # Draw
        size = 128
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

       
        p.setBrush(QBrush(QColor("#FF0000")))
        p.setPen(Qt.PenStyle.NoPen)
        path = QPainterPath()
        path.addRoundedRect(6, 22, size - 12, size - 44, 18, 18)
        p.drawPath(path)

       
        p.setBrush(QBrush(QColor("#FFFFFF")))
        tri = QPainterPath()
        cx, cy = size / 2, size / 2
        tri.moveTo(cx - 16, cy - 20)
        tri.lineTo(cx + 22, cy)
        tri.lineTo(cx - 16, cy + 20)
        tri.closeSubpath()
        p.drawPath(tri)
        p.end()

        return QIcon(px)

    def _launch_main(self):
        self._dl_page = DownloaderPage()
        self._stack.addWidget(self._dl_page)
        self._stack.setCurrentWidget(self._dl_page)

    def reset_app(self):
       
        # Stop 
        old = getattr(self, "_dl_page", None)
        if old:
            for attr in ("_fetch_worker", "_dl_worker", "_thumb_worker",
                         "_thumb_save_w", "_queue_dl_worker"):
                w = getattr(old, attr, None)
                if w and hasattr(w, "isRunning") and w.isRunning():
                    if hasattr(w, "stop"):
                        w.stop()
                    w.quit()
                    w.wait(800)

       
        ThemeManager._listeners = [
            fn for fn in ThemeManager._listeners
            if not (hasattr(fn, "__self__") and isinstance(
                getattr(fn, "__self__", None),
                (DownloaderPage,)
            ))
        ]

     
        if old:
            self._stack.removeWidget(old)
            old.deleteLater()

       
        self._launch_main()

        
        self.setWindowTitle("7D-YT — Reset ✓")
        QTimer.singleShot(1200, lambda: self.setWindowTitle("7D-YT"))


# ────────────────────────────────xytfjhfh─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    app.setApplicationName("7D-YT")

    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
#sdfsdfdf
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
