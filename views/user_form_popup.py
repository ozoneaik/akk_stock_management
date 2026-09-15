# -*- coding: utf-8 -*-
"""
views/user_form_popup.py
Popup ฟอร์มสำหรับ "เพิ่มผู้ใช้งานใหม่" และ "แก้ไขผู้ใช้งาน" ใช้ฟอร์มเดียวกัน
ถ้าส่ง user_data เข้ามา = โหมดแก้ไข, ถ้าไม่ส่ง = โหมดเพิ่มใหม่
"""

import tkinter as tk
from tkinter import messagebox

from controllers import user_controller
from views import ui_helpers
import config


class UserFormPopup(tk.Toplevel):
    def __init__(self, parent, current_user, on_saved, user_data=None):
        super().__init__(parent)
        self.current_user = current_user
        self.on_saved = on_saved
        self.user_data = user_data
        self.is_edit_mode = user_data is not None
        self.is_editing_self = self.is_edit_mode and user_data["id"] == current_user["id"]

        self.title("แก้ไขผู้ใช้งาน" if self.is_edit_mode else "เพิ่มผู้ใช้งานใหม่")
        self.resizable(False, False)
        self.grab_set()
        ui_helpers.center_window(self, 380, 430)

        self._build_ui()
        if self.is_edit_mode:
            self._load_existing_data()

    def _build_ui(self):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        self.username_entry = self._add_labeled_entry(form, "ชื่อผู้ใช้ (username) *")
        self.name_entry = self._add_labeled_entry(form, "ชื่อที่แสดง *")

        tk.Label(form, text="บทบาท *", font=ui_helpers.get_ui_font()).pack(anchor="w", pady=(8, 2))
        self.role_var = tk.StringVar(value=config.ROLE_OWNER)
        role_row = tk.Frame(form)
        role_row.pack(fill="x")
        self.admin_radio = tk.Radiobutton(
            role_row, text="แอดมิน", variable=self.role_var, value=config.ROLE_ADMIN,
            font=ui_helpers.get_ui_font(),
        )
        self.admin_radio.pack(side="left")
        self.owner_radio = tk.Radiobutton(
            role_row, text="เจ้าของร้าน", variable=self.role_var, value=config.ROLE_OWNER,
            font=ui_helpers.get_ui_font(),
        )
        self.owner_radio.pack(side="left", padx=(15, 0))

        if self.is_editing_self:
            self.admin_radio.config(state="disabled")
            self.owner_radio.config(state="disabled")
            tk.Label(
                form, text="(ไม่สามารถเปลี่ยนบทบาทของบัญชีตัวเองได้)",
                font=ui_helpers.get_ui_font(size=8), fg="#888888",
            ).pack(anchor="w")

        pin_label = "PIN ใหม่ 4 หลัก (เว้นว่างไว้ถ้าไม่ต้องการเปลี่ยน)" if self.is_edit_mode else "PIN 4 หลัก *"
        self.pin_entry = self._add_labeled_entry(form, pin_label, show="*")

        button_row = tk.Frame(form)
        button_row.pack(fill="x", pady=(20, 0))
        tk.Button(
            button_row, text="บันทึก", font=ui_helpers.get_ui_font(bold=True),
            command=self._on_save_click, bg="#2e7d32", fg="white", cursor="hand2",
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(0, 5))
        tk.Button(
            button_row, text="ยกเลิก", font=ui_helpers.get_ui_font(),
            command=self.destroy, cursor="hand2",
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(5, 0))

    def _add_labeled_entry(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, font=ui_helpers.get_ui_font()).pack(anchor="w", pady=(8, 2))
        entry = tk.Entry(parent, font=ui_helpers.get_ui_font(), show=show)
        entry.pack(fill="x")
        return entry

    def _load_existing_data(self):
        data = self.user_data
        self.username_entry.insert(0, data["username"])
        self.username_entry.config(state="disabled")  # ไม่ให้แก้ username เพื่อป้องกันข้อมูลชนกัน
        self.name_entry.insert(0, data["name"])
        self.role_var.set(data["role"])

    def _on_save_click(self):
        data = {
            "username": self.username_entry.get().strip(),
            "display_name": self.name_entry.get().strip(),
            "role": self.role_var.get(),
            "pin": self.pin_entry.get().strip(),
        }

        try:
            if self.is_edit_mode:
                user_controller.update_user(self.user_data["id"], data, self.current_user)
                messagebox.showinfo("สำเร็จ", "แก้ไขข้อมูลผู้ใช้งานเรียบร้อยแล้ว", parent=self)
            else:
                user_controller.create_user(data, self.current_user)
                messagebox.showinfo("สำเร็จ", "เพิ่มผู้ใช้งานใหม่เรียบร้อยแล้ว", parent=self)
        except ValueError as e:
            messagebox.showwarning("ไม่สามารถบันทึกได้", str(e), parent=self)
            return
        except Exception as e:  # เผื่อ username ซ้ำ (UNIQUE constraint) หรือข้อผิดพลาดอื่นๆ จากฐานข้อมูล
            messagebox.showerror(
                "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลได้: {e}\n(ชื่อผู้ใช้นี้อาจถูกใช้ไปแล้ว)", parent=self,
            )
            return

        if self.on_saved:
            self.on_saved()
        self.destroy()
