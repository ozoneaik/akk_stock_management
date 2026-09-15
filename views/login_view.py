# -*- coding: utf-8 -*-
"""
views/login_view.py
หน้าจอเข้าสู่ระบบ (username + PIN 4 หลัก — ตรงกับ schema ที่ใช้ร่วมกับเว็บแอป)
เมื่อเข้าสู่ระบบสำเร็จ จะปิดหน้าต่างนี้แล้วเปิดหน้าต่างหลัก (MainWindow) ต่อ
"""

import tkinter as tk

from controllers import auth_controller
from views import ui_helpers
import config


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.resizable(False, False)
        ui_helpers.center_window(self, 420, 340)
        self.configure(bg="white")
        ui_helpers.apply_global_font(self)

        self._build_ui()
        self.bind("<Return>", lambda event: self._on_login_click())
        self.username_entry.focus_set()

    def _build_ui(self):
        container = tk.Frame(self, bg="white")
        container.pack(expand=True, fill="both", padx=40, pady=30)

        title_label = tk.Label(
            container,
            text="ออฟกิจเกษตร",
            font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_TITLE, bold=True),
            bg="white",
        )
        title_label.pack(pady=(10, 0))

        subtitle_label = tk.Label(
            container,
            text="ระบบจัดการสต็อกสินค้า",
            font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_NORMAL),
            bg="white",
            fg="#555555",
        )
        subtitle_label.pack(pady=(0, 25))

        tk.Label(container, text="ชื่อผู้ใช้", font=ui_helpers.get_ui_font(), bg="white", anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(container, font=ui_helpers.get_ui_font())
        self.username_entry.pack(fill="x", pady=(2, 15), ipady=4)

        tk.Label(container, text="รหัส PIN (4 หลัก)", font=ui_helpers.get_ui_font(), bg="white", anchor="w").pack(fill="x")
        self.pin_entry = tk.Entry(container, font=ui_helpers.get_ui_font(), show="*")
        self.pin_entry.pack(fill="x", pady=(2, 5), ipady=4)

        self.error_label = tk.Label(container, text="", font=ui_helpers.get_ui_font(size=9), bg="white", fg="red")
        self.error_label.pack(fill="x", pady=(0, 10))

        login_button = tk.Button(
            container,
            text="เข้าสู่ระบบ",
            font=ui_helpers.get_ui_font(bold=True),
            command=self._on_login_click,
            cursor="hand2",
        )
        login_button.pack(fill="x", ipady=6)

    def _on_login_click(self):
        username = self.username_entry.get()
        pin = self.pin_entry.get()

        user, error = auth_controller.login(username, pin)
        if error:
            self.error_label.config(text=error)
            return

        self.destroy()
        # import ในนี้เพื่อเลี่ยงปัญหา circular import ระหว่าง login_view กับ main_window
        from views.main_window import MainWindow

        app = MainWindow(user)
        app.mainloop()


def run():
    login_window = LoginWindow()
    login_window.mainloop()
