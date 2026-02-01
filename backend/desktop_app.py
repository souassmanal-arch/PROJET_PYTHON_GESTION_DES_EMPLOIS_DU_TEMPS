import sys
import os
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QStackedWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QListWidget, QListWidgetItem,
                             QScrollArea, QGraphicsDropShadowEffect, QMessageBox,
                             QGridLayout, QComboBox, QDateEdit, QTimeEdit, QToolButton)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QLinearGradient, QBrush

# Backend Imports
from app import create_app, db
from models.user import User
from models.schedule import Schedule, Group
from models.room import Room
from models.notification import Notification
from models.reservation import Reservation
from werkzeug.security import check_password_hash

# -------------------------------------------------------------
# PROFESSIONAL NAVY & GRAY THEME
# -------------------------------------------------------------
STYLE = {
    "navy": "#0F172A",        # Slate 900
    "blue": "#2563EB",        # Blue 600
    "gray_bg": "#F8FAFC",     # Slate 50 Background
    "gray_text": "#475569",   # Slate 600 Text
    "white": "#FFFFFF",
    "border": "#E2E8F0",
    "success": "#10B981",
    "danger": "#EF4444"
}

QSS = f"""
QMainWindow {{
    background-color: {STYLE['gray_bg']};
}}

#SidePanel {{
    background-color: {STYLE['navy']};
    border-right: none;
}}

#SideButton {{
    background-color: transparent;
    color: #94A3B8;
    text-align: left;
    padding: 16px 25px;
    border-radius: 0;
    font-size: 14px;
    font-weight: 500;
    border: none;
}}

#SideButton:hover {{
    background-color: rgba(255,255,255,0.05);
    color: white;
}}

#SideButton[active="true"] {{
    background-color: {STYLE['blue']};
    color: white;
    font-weight: bold;
}}

#Card {{
    background-color: {STYLE['white']};
    border: 1px solid {STYLE['border']};
    border-radius: 12px;
}}

#Title {{
    color: {STYLE['navy']};
    font-size: 24px;
    font-weight: 800;
}}

QLineEdit, QComboBox, QDateEdit, QTimeEdit {{
    padding: 12px;
    border: 1px solid {STYLE['border']};
    border-radius: 8px;
    background: white;
    color: {STYLE['navy']};
    font-size: 14px;
}}

#PrimaryBtn {{
    background-color: {STYLE['blue']};
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    border: none;
}}

#PrimaryBtn:hover {{
    background-color: #1D4ED8;
}}

QTableWidget {{
    background-color: white;
    border: 1px solid {STYLE['border']};
    border-radius: 8px;
    gridline-color: #F1F5F9;
}}

QHeaderView::section {{
    background-color: #F8FAFC;
    padding: 12px;
    border: none;
    border-bottom: 2px solid {STYLE['border']};
    font-weight: bold;
    color: {STYLE['navy']};
}}
"""

class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.flask_app = create_app()
        self.current_user = None
        
        self.setWindowTitle("University Schedule Manager - Professional Edition")
        self.resize(1280, 850)
        self.setStyleSheet(QSS)
        
        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)
        
        self.init_login_ui()
        self.init_dashboard_ui()
        
    def init_login_ui(self):
        self.login_page = QWidget()
        layout = QHBoxLayout(self.login_page)
        layout.setContentsMargins(0,0,0,0)
        
        # Background Part
        bg_lbl = QLabel()
        img_path = "C:/Users/PROBOOK/.gemini/antigravity/brain/914ad66c-fe36-4dbc-8010-e2835c1f250b/university_background_pro_1769940033305.png"
        if os.path.exists(img_path):
            pix = QPixmap(img_path).scaled(1280, 850, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            bg_lbl.setPixmap(pix)
        else:
            bg_lbl.setStyleSheet(f"background-color: {STYLE['navy']};")
        bg_lbl.setScaledContents(True)

        # Login Form Overlay
        self.overlay = QFrame(bg_lbl)
        self.overlay.setFixedSize(480, 650) # Increased height
        self.overlay.move(400, 100)
        self.overlay.setStyleSheet("background-color: white; border-radius: 20px;")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(60)
        shadow.setXOffset(0)
        shadow.setYOffset(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.overlay.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(self.overlay)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(12)

        title = QLabel("Portail Universitaire")
        title.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {STYLE['navy']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("Système de Gestion Centralisé")
        subtitle.setStyleSheet(f"color: {STYLE['gray_text']}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email professionnel")
        self.email_input.setText("admin@univ.ma") 
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Mot de passe")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setText("admin123")
        self.pass_input.returnPressed.connect(self.do_login) # Login on Enter

        # Main Entry Button
        self.submit_btn = QPushButton("ACCÉDER AU TABLEAU DE BORD")
        self.submit_btn.setMinimumHeight(55)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {STYLE['blue']};
                color: white;
                border-radius: 12px;
                font-weight: 900;
                font-size: 14px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: #1D4ED8;
            }}
        """)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self.do_login)

        # Quick Links
        sep = QLabel("OU CONNEXION RAPIDE")
        sep.setStyleSheet("color: #94A3B8; font-size: 10px; font-weight: bold; margin-top: 10px;")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btns_layout = QHBoxLayout()
        for label, email, pwd in [("ADMINISTRATEUR", "admin@univ.ma", "admin123"), ("ENSEIGNANT", "chraibi@univ.ma", "pass123")]:
            btn = QPushButton(label)
            btn.setMinimumHeight(45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #F8FAFC;
                    color: {STYLE['navy']};
                    border: 1px solid {STYLE['border']};
                    border-radius: 8px;
                    font-weight: 700;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {STYLE['blue']};
                    color: white;
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, e=email, p=pwd: self.do_quick_login(e, p))
            btns_layout.addWidget(btn)
        
        form_layout.addWidget(title)
        form_layout.addWidget(subtitle)
        form_layout.addSpacing(20)
        form_layout.addWidget(QLabel("<b>E-mail</b>"))
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(QLabel("<b>Mot de passe</b>"))
        form_layout.addWidget(self.pass_input)
        form_layout.addSpacing(15)
        form_layout.addWidget(self.submit_btn)
        form_layout.addWidget(sep)
        form_layout.addLayout(btns_layout)
        form_layout.addStretch()

        layout.addWidget(bg_lbl)
        self.main_stack.addWidget(self.login_page)


    def do_quick_login(self, email, password):
        self.email_input.setText(email)
        self.pass_input.setText(password)
        self.do_login()


    def do_login(self):
        email = self.email_input.text()
        password = self.pass_input.text()
        with self.flask_app.app_context():
            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                self.current_user = {"id": user.id, "username": user.username, "role": user.role, "group_id": user.group_id}
                self.setup_sidebar()
                self.main_stack.setCurrentIndex(1)
            else:
                QMessageBox.critical(self, "Erreur", "Identifiants invalides.")

    def init_dashboard_ui(self):
        dashboard_page = QWidget()
        hbox = QHBoxLayout(dashboard_page)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # Sidebar
        self.side_panel = QFrame()
        self.side_panel.setObjectName("SidePanel")
        self.side_panel.setFixedWidth(260)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(0, 40, 0, 40)

        self.user_info = QLabel("User")
        self.user_info.setStyleSheet("color: white; font-weight: 800; font-size: 16px; padding-left: 25px;")
        self.role_tag = QLabel("ROLE")
        self.role_tag.setStyleSheet(f"color: {STYLE['blue']}; font-weight: bold; font-size: 11px; padding-left: 25px; text-transform: uppercase;")

        self.side_layout.addWidget(self.user_info)
        self.side_layout.addWidget(self.role_tag)
        self.side_layout.addSpacing(40)

        self.nav_container = QVBoxLayout()
        self.nav_container.setSpacing(0)
        self.side_layout.addLayout(self.nav_container)
        self.side_layout.addStretch()

        logout = QPushButton("🚪 Déconnexion")
        logout.setObjectName("SideButton")
        logout.clicked.connect(self.logout)
        self.side_layout.addWidget(logout)

        # Content
        self.content_stack = QStackedWidget()
        
        hbox.addWidget(self.side_panel)
        hbox.addWidget(self.content_stack)
        
        self.main_stack.addWidget(dashboard_page)

    def logout(self):
        self.email_input.clear()
        self.pass_input.clear()
        self.main_stack.setCurrentIndex(0)

    def setup_sidebar(self):
        # Clear existing
        while self.nav_container.count():
            item = self.nav_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        while self.content_stack.count():
            w = self.content_stack.widget(0)
            self.content_stack.removeWidget(w)
            w.deleteLater()

        role = self.current_user['role']
        self.user_info.setText(self.current_user['username'])
        self.role_tag.setText(role)

        menu_items = [("📊 Overview", self.ui_overview())]

        if role == 'admin':
            menu_items += [
                ("📅 Manage Schedules", self.ui_manage_schedules()),
                ("🏢 Rooms & Labs", self.ui_manage_rooms()),
                ("👨‍🏫 Teachers", self.ui_manage_teachers()),
                ("👥 Groups", self.ui_manage_groups()),
                ("📝 Reservations", self.ui_manage_reservations()),
                ("⚙️ Settings", self.ui_settings())
            ]
        elif role == 'teacher':
            menu_items += [
                ("📅 My Schedule", self.ui_view_schedule()),
                ("🔑 Reserve Room", self.ui_reserve_room()),
                ("🔍 Find Vacant Room", self.ui_find_room()),
                ("📜 History", self.ui_history())
            ]
        elif role == 'student':
            menu_items += [
                ("📅 My Schedule", self.ui_view_schedule()),
                ("🔔 Notifications", self.ui_notifications()),
                ("📖 Find Study Room", self.ui_find_room())
            ]

        self.nav_buttons = []
        for i, (txt, page) in enumerate(menu_items):
            btn = QPushButton(txt)
            btn.setObjectName("SideButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            self.nav_container.addWidget(btn)
            self.nav_buttons.append(btn)
            self.content_stack.addWidget(page)

        self.switch_tab(0)

    def switch_tab(self, idx):
        self.content_stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", i == idx)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # -------------------------------------------------------------
    # UI PAGES
    # -------------------------------------------------------------
    def ui_overview(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Dashboard Overview", objectName="Title"))
        
        grid = QGridLayout()
        grid.addWidget(self.stat_card("Total Rooms", "14", "🏢"), 0, 0)
        grid.addWidget(self.stat_card("Total Teachers", "10", "👨‍🏫"), 0, 1)
        grid.addWidget(self.stat_card("Total Groups", "5", "👥"), 0, 2)
        l.addLayout(grid)
        l.addSpacing(40)
        l.addWidget(QLabel("Notifications Récentes"))
        l.addWidget(QTableWidget(5, 3, horizontalHeaderLabels=["Time", "Event", "Status"]))
        return page

    def stat_card(self, title, val, icon):
        card = QFrame(); card.setObjectName("Card")
        l = QVBoxLayout(card)
        l.addWidget(QLabel(f"{icon} {title}"))
        v = QLabel(val); v.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {STYLE['blue']};")
        l.addWidget(v)
        return card

    def ui_manage_schedules(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Manage Schedules", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Day", "Time", "Course", "Group", "Room"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = Schedule.query.all()
            table.setRowCount(len(data))
            for i, s in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(s.day_of_week))
                table.setItem(i, 1, QTableWidgetItem(f"{s.start_time.strftime('%H:%M')}"))
                table.setItem(i, 2, QTableWidgetItem(s.course_name))
                table.setItem(i, 3, QTableWidgetItem(str(s.group_id)))
                table.setItem(i, 4, QTableWidgetItem(str(s.room_id)))
        l.addWidget(table)
        return page

    def ui_manage_rooms(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Rooms & Labs Management", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "Type", "Capacity", "Equipment"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = Room.query.all()
            table.setRowCount(len(data))
            for i, r in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(r.name))
                table.setItem(i, 1, QTableWidgetItem(r.type))
                table.setItem(i, 2, QTableWidgetItem(str(r.capacity)))
                table.setItem(i, 3, QTableWidgetItem(r.equipment))
        l.addWidget(table)
        return page

    def ui_manage_teachers(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Teachers Management", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Name", "Email"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = User.query.filter_by(role='teacher').all()
            table.setRowCount(len(data))
            for i, t in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(t.username))
                table.setItem(i, 1, QTableWidgetItem(t.email))
        l.addWidget(table)
        return page

    def ui_manage_groups(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Groups Management", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Group Name", "Student Count"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = Group.query.all()
            table.setRowCount(len(data))
            for i, g in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(g.name))
                table.setItem(i, 1, QTableWidgetItem(str(g.students_count)))
        l.addWidget(table)
        return page

    def ui_manage_reservations(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Global Reservations", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Teacher", "Room", "Date", "Reason", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = Reservation.query.all()
            table.setRowCount(len(data))
            for i, r in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(str(r.teacher_id)))
                table.setItem(i, 1, QTableWidgetItem(str(r.room_id)))
                table.setItem(i, 2, QTableWidgetItem(str(r.date)))
                table.setItem(i, 3, QTableWidgetItem(r.motif))
                table.setItem(i, 4, QTableWidgetItem(r.status))
        l.addWidget(table)
        return page

    def ui_settings(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("System Settings", objectName="Title"))
        l.addWidget(QLabel("Database URI: " + self.flask_app.config['SQLALCHEMY_DATABASE_URI']))
        l.addWidget(QPushButton("Backup Database"))
        l.addStretch()
        return page

    def ui_view_schedule(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("My Schedule", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Day", "Time", "Course", "Room"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            if self.current_user['role'] == 'student':
                data = Schedule.query.filter_by(group_id=self.current_user['group_id']).all()
            else:
                data = Schedule.query.filter_by(teacher_id=self.current_user['id']).all()
            table.setRowCount(len(data))
            for i, s in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(s.day_of_week))
                table.setItem(i, 1, QTableWidgetItem(f"{s.start_time.strftime('%H:%M')}"))
                table.setItem(i, 2, QTableWidgetItem(s.course_name))
                table.setItem(i, 3, QTableWidgetItem(f"Room {s.room_id}"))
        l.addWidget(table)
        return page

    def ui_reserve_room(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(100, 40, 100, 40)
        l.addWidget(QLabel("Reserve Room", objectName="Title"))
        form = QFrame(); form.setObjectName("Card"); fl = QVBoxLayout(form)
        fl.addWidget(QLabel("Room"))
        cb = QComboBox()
        with self.flask_app.app_context():
            rooms = Room.query.all()
            for r in rooms: cb.addItem(r.name, r.id)
        fl.addWidget(cb)
        fl.addWidget(QLabel("Date"))
        fl.addWidget(QDateEdit(datetime.now()))
        fl.addWidget(QLabel("Reason"))
        fl.addWidget(QLineEdit())
        btn = QPushButton("Submit Request"); btn.setObjectName("PrimaryBtn")
        fl.addWidget(btn)
        l.addWidget(form); l.addStretch()
        return page

    def ui_find_room(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Find Vacant Room", objectName="Title"))
        l.addWidget(QLabel("Available rooms for now:"))
        table = QTableWidget(3, 2, horizontalHeaderLabels=["Room", "Capacity"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l.addWidget(table)
        return page

    def ui_history(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Reservation History", objectName="Title"))
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Room", "Reason", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        with self.flask_app.app_context():
            data = Reservation.query.filter_by(teacher_id=self.current_user['id']).all()
            table.setRowCount(len(data))
            for i, r in enumerate(data):
                table.setItem(i, 0, QTableWidgetItem(str(r.date)))
                table.setItem(i, 1, QTableWidgetItem(str(r.room_id)))
                table.setItem(i, 2, QTableWidgetItem(r.motif))
                table.setItem(i, 3, QTableWidgetItem(r.status))
        l.addWidget(table)
        return page

    def ui_notifications(self):
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(40, 40, 40, 40)
        l.addWidget(QLabel("Notifications", objectName="Title"))
        list_notif = QListWidget()
        with self.flask_app.app_context():
            notifs = Notification.query.filter_by(user_id=self.current_user['id']).all()
            for n in notifs: list_notif.addItem(f"🔔 {n.title}: {n.message}")
        l.addWidget(list_notif)
        return page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())
