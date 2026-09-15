# -*- coding: utf-8 -*-
"""
views/user_management_view.py
หน้า "จัดการผู้ใช้งาน" (เห็นเฉพาะ admin เท่านั้น): เพิ่ม/แก้ไข/ลบบัญชีผู้ใช้
"""

import tkinter as tk
from tkinter import ttk, messagebox

from controllers import user_controller
from views import ui_helpers
from views.user_form_popup import UserFormPopup
import config


class UserManagementView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._user_by_row = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Label(
            self, text="จัดการผู้ใช้งาน", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        button_row = tk.Frame(self, bg="white")
        button_row.pack(fill="x", padx=20)
        tk.Button(
            button_row, text="+ เพิ่มผู้ใช้งานใหม่", font=ui_helpers.get_ui_font(bold=True),
            bg="#2e7d32", fg="white", cursor="hand2", command=self._open_add_popup,
        ).pack(side="left")

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        ui_helpers.configure_treeview_style()
        columns = ("username", "display_name", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        headings = {"username": "ชื่อผู้ใช้ (username)", "display_name": "ชื่อที่แสดง", "role": "บทบาท"}
        widths = {"username": 160, "display_name": 260, "role": 140}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._open_edit_popup())

        bottom_row = tk.Frame(self, bg="white")
        bottom_row.pack(fill="x", padx=20, pady=(0, 20))
        tk.Button(
            bottom_row, text="แก้ไขผู้ใช้ที่เลือก", font=ui_helpers.get_ui_font(bold=True),
            cursor="hand2", command=self._open_edit_popup,
        ).pack(side="left")
        tk.Button(
            bottom_row, text="ลบผู้ใช้ที่เลือก", font=ui_helpers.get_ui_font(bold=True),
            fg="white", bg="#c0392b", cursor="hand2", command=self._on_delete_click,
        ).pack(side="left", padx=(10, 0))

    def refresh(self):
        loading = ui_helpers.show_loading(self)
        try:
            users = user_controller.list_users()
            for row in self.tree.get_children():
                self.tree.delete(row)
            self._user_by_row = {}
            for u in users:
                row_id = self.tree.insert("", "end", values=(u["username"], u["name"], u["role_label"]))
                self._user_by_row[row_id] = u
        finally:
            loading.destroy()

    def _get_selected_user(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return self._user_by_row.get(selection[0])

    def _open_add_popup(self):
        UserFormPopup(self, self.current_user, on_saved=self.refresh)

    def _open_edit_popup(self):
        user = self._get_selected_user()
        if user is None:
            messagebox.showwarning("ยังไม่ได้เลือกผู้ใช้", "กรุณาเลือกผู้ใช้งานที่ต้องการแก้ไขก่อน", parent=self)
            return
        UserFormPopup(self, self.current_user, on_saved=self.refresh, user_data=user)

    def _on_delete_click(self):
        user = self._get_selected_user()
        if user is None:
            messagebox.showwarning("ยังไม่ได้เลือกผู้ใช้", "กรุณาเลือกผู้ใช้งานที่ต้องการลบก่อน", parent=self)
            return

        confirmed = messagebox.askyesno(
            "ยืนยันการลบผู้ใช้งาน",
            f'ต้องการลบผู้ใช้งาน "{user["name"]}" ({user["username"]}) ใช่หรือไม่?\nการลบไม่สามารถกู้คืนได้',
            parent=self,
        )
        if not confirmed:
            return

        try:
            user_controller.delete_user(user["id"], self.current_user)
        except ValueError as e:
            messagebox.showwarning("ไม่สามารถลบได้", str(e), parent=self)
            return

        messagebox.showinfo("สำเร็จ", "ลบผู้ใช้งานเรียบร้อยแล้ว", parent=self)
        self.refresh()
