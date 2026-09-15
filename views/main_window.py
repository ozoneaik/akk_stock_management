# -*- coding: utf-8 -*-
"""
views/main_window.py
หน้าต่างหลักของโปรแกรม ประกอบด้วย:
- Navbar ด้านบนแถบเดียว: โลโก้/ชื่อระบบ, เมนูนำทางไปหน้าต่างๆ ทั้งหมด (แทนที่ sidebar เดิม),
  ปุ่มเพิ่มสินค้า (popup), ข้อมูลผู้ใช้ + ปุ่ม logout
- พื้นที่แสดงเนื้อหาด้านล่าง: สลับ view ตามเมนูที่เลือก

เมนูที่เห็นเฉพาะ admin: จัดการผู้ใช้, บันทึกกิจกรรม, สำรอง/กู้คืนข้อมูล
ข้อกำหนดสำคัญ: บทบาท "owner" (พ่อ) มีสิทธิ์เหมือน admin ทุกอย่าง ยกเว้น 3 เมนูดังกล่าว
"""

import tkinter as tk

from views import ui_helpers
from views.dashboard_view import DashboardView
from views.product_list_view import ProductListView
from views.stock_adjust_view import StockAdjustView
from views.activity_log_view import ActivityLogView
from views.user_management_view import UserManagementView
from views.backup_view import BackupView
from views.product_form_popup import ProductFormPopup
import config


class MainWindow(tk.Tk):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.is_admin = current_user["role"] == config.ROLE_ADMIN

        self.title(config.APP_TITLE)
        self.minsize(config.APP_MIN_WIDTH, config.APP_MIN_HEIGHT)
        ui_helpers.center_window(self, config.APP_MIN_WIDTH, config.APP_MIN_HEIGHT)
        ui_helpers.apply_global_font(self)

        self.frames = {}
        self.nav_buttons = {}
        self.current_frame_name = None

        self._build_navbar()
        self._build_body()

        self.show_frame("dashboard")

    # ------------------------------------------------------------ Navbar

    def _menu_items(self):
        items = [
            ("dashboard", "ภาพรวม"),
            ("product_list", "รายการสินค้า"),
            ("stock_adjust", "เพิ่ม/ลดสต็อก"),
        ]
        # เมนูเฉพาะ admin ตามข้อกำหนด (owner เห็นทุกอย่างยกเว้นเมนูเหล่านี้)
        if self.is_admin:
            items.append(("user_management", "จัดการผู้ใช้"))
            items.append(("activity_log", "บันทึกกิจกรรม"))
            items.append(("backup", "สำรอง/กู้คืนข้อมูล"))
        return items

    def _build_navbar(self):
        navbar = tk.Frame(self, bg="#2e7d32", height=55)
        navbar.pack(fill="x", side="top")
        navbar.pack_propagate(False)

        title_label = tk.Label(
            navbar, text="ออฟกิจเกษตร", font=ui_helpers.get_ui_font(size=13, bold=True), bg="#2e7d32", fg="white",
        )
        title_label.pack(side="left", padx=(20, 10))

        # เมนูนำทางทั้งหมด (เดิมอยู่ที่ sidebar ด้านซ้าย ย้ายมารวมไว้ในแถบ navbar นี้แทน)
        for name, label in self._menu_items():
            btn = tk.Button(
                navbar, text=label, font=ui_helpers.get_ui_font(), relief="flat", bd=0,
                bg="#2e7d32", fg="white", activebackground="#1b5e20", activeforeground="white",
                cursor="hand2", command=lambda n=name: self.show_frame(n),
            )
            btn.pack(side="left", padx=2, ipady=10, ipadx=8)
            self.nav_buttons[name] = btn

        logout_button = tk.Button(
            navbar, text="ออกจากระบบ", font=ui_helpers.get_ui_font(), command=self._on_logout_click, cursor="hand2",
        )
        logout_button.pack(side="right", padx=20)

        role_text = "แอดมิน" if self.is_admin else "เจ้าของร้าน"
        user_label = tk.Label(
            navbar, text=f'{self.current_user["name"]} ({role_text})',
            font=ui_helpers.get_ui_font(size=9), bg="#2e7d32", fg="white",
        )
        user_label.pack(side="right", padx=10)

        add_product_button = tk.Button(
            navbar, text="+ เพิ่มสินค้าใหม่", font=ui_helpers.get_ui_font(bold=True),
            command=self._open_add_product_popup, cursor="hand2",
        )
        add_product_button.pack(side="right", padx=10)

    # ------------------------------------------------------------- Body

    def _build_body(self):
        self.content_area = tk.Frame(self, bg="white")
        self.content_area.pack(fill="both", expand=True)

        # สร้างทุกหน้าไว้ล่วงหน้าใน content_area แล้วสลับด้วย tkraise (เร็วกว่าสร้างใหม่ทุกครั้ง)
        self.frames["dashboard"] = DashboardView(self.content_area, self.current_user)
        self.frames["product_list"] = ProductListView(self.content_area, self.current_user)
        self.frames["stock_adjust"] = StockAdjustView(self.content_area, self.current_user)
        if self.is_admin:
            self.frames["user_management"] = UserManagementView(self.content_area, self.current_user)
            self.frames["activity_log"] = ActivityLogView(self.content_area, self.current_user)
            self.frames["backup"] = BackupView(self.content_area, self.current_user)

        for frame in self.frames.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_frame(self, name: str):
        if name not in self.frames:
            return
        frame = self.frames[name]
        frame.tkraise()
        # รีเฟรชข้อมูลทุกครั้งที่เข้าหน้านั้นๆ เพื่อให้เห็นข้อมูลล่าสุดเสมอ
        if hasattr(frame, "refresh"):
            frame.refresh()
        self.current_frame_name = name
        self._highlight_active_button(name)

    def _highlight_active_button(self, active_name):
        for name, btn in self.nav_buttons.items():
            btn.config(bg="#1b5e20" if name == active_name else "#2e7d32")

    # ---------------------------------------------------------- Actions

    def _open_add_product_popup(self):
        def on_saved():
            if self.current_frame_name == "product_list":
                self.frames["product_list"].refresh()
            if self.current_frame_name == "dashboard":
                self.frames["dashboard"].refresh()

        ProductFormPopup(self, self.current_user, on_saved=on_saved)

    def restart_to_login(self):
        """ปิดหน้าต่างหลักแล้วกลับไปหน้าเข้าสู่ระบบ ใช้ทั้งตอน logout และหลังกู้คืนข้อมูลสำเร็จ"""
        self.destroy()
        from views.login_view import LoginWindow

        LoginWindow().mainloop()

    def _on_logout_click(self):
        self.restart_to_login()
