# -*- coding: utf-8 -*-
"""
views/stock_adjust_popup.py
Popup เล็กๆ สำหรับกำหนดรูปแบบ(เพิ่ม/ลด)+หน่วย+จำนวน+เหตุผล ของสินค้า 1 รายการ
ไม่ได้บันทึกลงฐานข้อมูลเอง แค่ตรวจสอบว่าจำนวนที่กรอกถูกต้อง แล้วส่งค่ากลับผ่าน on_confirm
เพื่อให้ผู้เรียกใช้ (caller) ตัดสินใจเองว่าจะบันทึกทันที หรือแค่เก็บพักไว้ก่อน (เช่น รายการปรับสต็อกหลายรายการ)

on_confirm(direction, unit_mode, amount, reason) ต้องคืนค่า True ถ้าต้องการให้ปิด popup นี้
หรือ False ถ้าต้องการให้ค้าง popup ไว้ (เช่น เพิ่ม/ลดแล้วเกิด error จากฐานข้อมูล)
- direction: "in" หรือ "out"
- unit_mode: "base" (หน่วยย่อย เช่น ขวด) หรือ "pack" (หน่วยบรรจุ เช่น ลัง)
- amount: จำนวนตามหน่วยที่เลือก (ยังไม่แปลงเป็นหน่วยย่อย ผู้เรียกใช้เป็นคนแปลงเอง)
"""

import tkinter as tk
from tkinter import messagebox

from views import ui_helpers


class StockAdjustPopup(tk.Toplevel):
    def __init__(
        self, parent, product, on_confirm,
        initial_direction="in", initial_unit_mode="base", initial_amount="", initial_reason="",
        title="ปรับสต็อกสินค้า",
    ):
        super().__init__(parent)
        self.product = product
        self.on_confirm = on_confirm

        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        ui_helpers.center_window(self, 380, 360)

        self._build_ui(initial_direction, initial_unit_mode, initial_amount, initial_reason)

    def _build_ui(self, initial_direction, initial_unit_mode, initial_amount, initial_reason):
        form = tk.Frame(self, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(
            form, text=f'{self.product["name"]} (รหัส {self.product["sku"] or "-"})',
            font=ui_helpers.get_ui_font(bold=True), wraplength=320, justify="left",
        ).pack(anchor="w")
        tk.Label(
            form, text=f'คงเหลือปัจจุบัน: {self.product["current_stock"]} {self.product["base_unit"]}',
            font=ui_helpers.get_ui_font(size=9), fg="#666666",
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(form, text="รูปแบบ:", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.direction_var = tk.StringVar(value=initial_direction)
        direction_row = tk.Frame(form)
        direction_row.pack(fill="x", pady=(2, 10))
        tk.Radiobutton(
            direction_row, text="เพิ่มสต็อกเข้า (รับของ)", variable=self.direction_var, value="in",
            font=ui_helpers.get_ui_font(),
        ).pack(anchor="w")
        tk.Radiobutton(
            direction_row, text="ลดสต็อกออก (ขาย/ชำรุด)", variable=self.direction_var, value="out",
            font=ui_helpers.get_ui_font(),
        ).pack(anchor="w")

        amount_row = tk.Frame(form)
        amount_row.pack(fill="x", pady=(2, 10))
        tk.Label(form, text="จำนวน:", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.amount_entry = tk.Entry(amount_row, font=ui_helpers.get_ui_font())
        self.amount_entry.pack(side="left", fill="x", expand=True)
        if initial_amount:
            self.amount_entry.insert(0, str(initial_amount))

        self.unit_mode_var = tk.StringVar(value=initial_unit_mode)
        if self.product.get("pack_unit"):
            unit_options = {
                "base": self.product["base_unit"],
                "pack": f'{self.product["pack_unit"]} ({self.product["units_per_pack"]} {self.product["base_unit"]})',
            }
            unit_menu = tk.OptionMenu(amount_row, self.unit_mode_var, *unit_options.keys())
            unit_menu.config(font=ui_helpers.get_ui_font(size=9))
            # แสดงชื่อหน่วยเป็นข้อความอ่านง่าย แทนค่าภายใน "base"/"pack"
            menu = unit_menu["menu"]
            menu.delete(0, "end")
            for value, label in unit_options.items():
                menu.add_command(label=label, command=lambda v=value: self.unit_mode_var.set(v))
            self._unit_menu_button = unit_menu
            self._refresh_unit_menu_label(unit_options)
            self.unit_mode_var.trace_add("write", lambda *_: self._refresh_unit_menu_label(unit_options))
            unit_menu.pack(side="left", padx=(8, 0))
        else:
            tk.Label(amount_row, text=self.product["base_unit"], font=ui_helpers.get_ui_font()).pack(
                side="left", padx=(8, 0)
            )

        tk.Label(form, text="เหตุผล/หมายเหตุ:", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.reason_entry = tk.Entry(form, font=ui_helpers.get_ui_font())
        self.reason_entry.pack(fill="x", pady=(2, 15))
        if initial_reason:
            self.reason_entry.insert(0, initial_reason)

        button_row = tk.Frame(form)
        button_row.pack(fill="x")
        tk.Button(
            button_row, text="บันทึก", font=ui_helpers.get_ui_font(bold=True),
            bg="#2e7d32", fg="white", cursor="hand2", command=self._on_confirm_click,
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(0, 5))
        tk.Button(
            button_row, text="ยกเลิก", font=ui_helpers.get_ui_font(), command=self.destroy, cursor="hand2",
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(5, 0))

        self.amount_entry.focus_set()
        self.bind("<Return>", lambda e: self._on_confirm_click())

    def _refresh_unit_menu_label(self, unit_options):
        self._unit_menu_button.config(text=unit_options[self.unit_mode_var.get()])

    def _on_confirm_click(self):
        amount_text = self.amount_entry.get().strip()
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("จำนวนไม่ถูกต้อง", "กรุณากรอกจำนวนเป็นตัวเลขมากกว่า 0", parent=self)
            return

        direction = self.direction_var.get()
        unit_mode = self.unit_mode_var.get()
        reason = self.reason_entry.get().strip()

        if self.on_confirm(direction, unit_mode, amount, reason):
            self.destroy()
