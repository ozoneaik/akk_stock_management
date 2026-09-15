# -*- coding: utf-8 -*-
"""
views/activity_log_view.py
หน้าบันทึกการทำงานของระบบ (เพิ่ม/แก้ไข/ลบสินค้า, ปรับสต็อก)
ตามข้อกำหนด: หน้านี้ให้เห็นเฉพาะผู้ใช้ role 'admin' เท่านั้น
(การซ่อนเมนูทำที่ main_window.py ส่วนไฟล์นี้โฟกัสแค่การแสดงข้อมูล)
"""

import tkinter as tk
from tkinter import ttk

from controllers import log_controller
from views import ui_helpers
import config


class ActivityLogView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Label(
            self, text="บันทึกการทำงานของระบบ", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        tk.Button(self, text="รีเฟรช", font=ui_helpers.get_ui_font(), command=self.refresh).pack(
            anchor="w", padx=20, pady=(0, 10)
        )

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ui_helpers.configure_treeview_style()
        columns = ("time", "user", "action", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        headings = {"time": "วันเวลา", "user": "ผู้ใช้งาน", "action": "การกระทำ", "description": "รายละเอียด"}
        widths = {"time": 140, "user": 140, "action": 100, "description": 480}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        loading = ui_helpers.show_loading(self)
        try:
            logs = log_controller.get_logs()
            for row in self.tree.get_children():
                self.tree.delete(row)
            for entry in logs:
                created_at_text = entry["createdAt"].strftime("%d/%m/%Y %H:%M:%S")
                self.tree.insert(
                    "", "end",
                    values=(created_at_text, entry["user_display_name"], entry["action_label"], entry["description"]),
                )
        finally:
            loading.destroy()
