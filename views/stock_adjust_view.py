# -*- coding: utf-8 -*-
"""
views/stock_adjust_view.py
หน้า "เพิ่ม/ลดสต็อกสินค้า" รองรับการปรับสต็อกทีละหลายรายการในครั้งเดียว
ขั้นตอน:
1. ค้นหาสินค้าด้วยรหัสหรือชื่อ -> เลือกได้หลายรายการ (กด Ctrl/Shift ค้างไว้) -> เพิ่มเข้ารายการปรับสต็อก
2. ดับเบิลคลิกแต่ละรายการในรายการปรับสต็อก เพื่อกำหนดรูปแบบ(เพิ่ม/ลด) + หน่วย + จำนวน + เหตุผลของสินค้านั้น
3. กด "บันทึกการปรับสต็อกทั้งหมด" เพื่อบันทึกทุกรายการที่กำหนดจำนวนไว้แล้วในครั้งเดียว
"""

import tkinter as tk
from tkinter import ttk, messagebox

from controllers import stock_controller
from views import ui_helpers
from views.stock_adjust_popup import StockAdjustPopup
import config

DIRECTION_LABELS = {"in": "เพิ่มเข้า", "out": "ลดออก"}


class StockAdjustView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._result_by_row = {}
        # product_id -> {"product": dict, "direction": "in"/"out", "unit_mode": "base"/"pack",
        #                "amount": float|None, "reason": str}
        self._pending = {}
        self._build_ui()

    def _build_ui(self):
        header = tk.Label(
            self, text="เพิ่ม/ลดสต็อกสินค้า", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        # --- ขั้นที่ 1: ค้นหาสินค้า ---
        search_frame = tk.LabelFrame(
            self, text="ขั้นที่ 1: ค้นหาสินค้า (เลือกได้หลายรายการด้วยการกด Ctrl หรือ Shift ค้างไว้)",
            bg="white", font=ui_helpers.get_ui_font(),
        )
        search_frame.pack(fill="x", padx=20, pady=(0, 10))

        search_row = tk.Frame(search_frame, bg="white")
        search_row.pack(fill="x", padx=10, pady=10)
        self.search_entry = tk.Entry(search_row, font=ui_helpers.get_ui_font())
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda e: self._on_search())
        tk.Button(search_row, text="ค้นหา", font=ui_helpers.get_ui_font(), command=self._on_search).pack(
            side="left", padx=(10, 0)
        )

        ui_helpers.configure_treeview_style()
        columns = ("code", "name", "quantity", "unit")
        self.result_tree = ttk.Treeview(search_frame, columns=columns, show="headings", height=6)
        for col, text, width in [
            ("code", "รหัสสินค้า", 100), ("name", "ชื่อสินค้า", 300), ("quantity", "คงเหลือ", 90), ("unit", "หน่วย", 80),
        ]:
            self.result_tree.heading(col, text=text)
            self.result_tree.column(col, width=width, anchor="center" if col != "name" else "w")
        self.result_tree.pack(fill="x", padx=10)
        self.result_tree.bind("<Double-1>", lambda e: self._on_add_selected_click())

        tk.Button(
            search_frame, text="เพิ่มรายการที่เลือกเข้ารายการปรับสต็อก", font=ui_helpers.get_ui_font(bold=True),
            cursor="hand2", command=self._on_add_selected_click,
        ).pack(anchor="w", padx=10, pady=10)

        # --- ขั้นที่ 2: รายการที่จะปรับสต็อก ---
        pending_frame = tk.LabelFrame(
            self, text="ขั้นที่ 2: รายการที่จะปรับสต็อก (ดับเบิลคลิกแถวเพื่อกำหนดรูปแบบ/หน่วย/จำนวน/เหตุผล)",
            bg="white", font=ui_helpers.get_ui_font(),
        )
        pending_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        pending_columns = ("code", "name", "current_quantity", "direction", "amount", "reason")
        self.pending_tree = ttk.Treeview(pending_frame, columns=pending_columns, show="headings", height=8)
        pending_headings = {
            "code": "รหัสสินค้า", "name": "ชื่อสินค้า", "current_quantity": "คงเหลือปัจจุบัน",
            "direction": "รูปแบบ", "amount": "จำนวน", "reason": "เหตุผล",
        }
        pending_widths = {
            "code": 100, "name": 240, "current_quantity": 130, "direction": 90, "amount": 110, "reason": 160,
        }
        for col in pending_columns:
            self.pending_tree.heading(col, text=pending_headings[col])
            self.pending_tree.column(
                col, width=pending_widths[col], anchor="w" if col in ("name", "reason") else "center"
            )
        self.pending_tree.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.pending_tree.bind("<Double-1>", lambda e: self._on_edit_pending_click())

        pending_button_row = tk.Frame(pending_frame, bg="white")
        pending_button_row.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(
            pending_button_row, text="ลบออกจากรายการ", font=ui_helpers.get_ui_font(),
            cursor="hand2", command=self._on_remove_pending_click,
        ).pack(side="left")

        tk.Button(
            self, text="บันทึกการปรับสต็อกทั้งหมด", font=ui_helpers.get_ui_font(bold=True),
            bg="#2e7d32", fg="white", cursor="hand2", command=self._on_save_all_click,
        ).pack(fill="x", padx=20, pady=(0, 20), ipady=8)

    def refresh(self):
        """เรียกทุกครั้งที่กลับมาที่หน้านี้ ล้างผลค้นหาเก่า (คงรายการปรับสต็อกที่ค้างไว้ไม่ต้องล้าง)"""
        self._on_search()

    # ------------------------------------------------------- ขั้นที่ 1

    def _on_search(self):
        keyword = self.search_entry.get().strip()
        for row in self.result_tree.get_children():
            self.result_tree.delete(row)
        self._result_by_row = {}

        if not keyword:
            return

        products = stock_controller.search_products(keyword)
        for product in products:
            row_id = self.result_tree.insert(
                "", "end", values=(product["sku"] or "-", product["name"], product["currentStock"], product["baseUnit"])
            )
            self._result_by_row[row_id] = product

    def _on_add_selected_click(self):
        selection = self.result_tree.selection()
        if not selection:
            messagebox.showwarning(
                "ยังไม่ได้เลือกสินค้า",
                "กรุณาเลือกสินค้าจากผลการค้นหาก่อน (เลือกได้หลายรายการด้วยการกด Ctrl หรือ Shift ค้างไว้)",
                parent=self,
            )
            return

        products = [self._result_by_row[row_id] for row_id in selection if row_id in self._result_by_row]
        added = 0
        for product in products:
            if product["id"] not in self._pending:
                self._pending[product["id"]] = {
                    "product": product, "direction": "in", "unit_mode": "base", "amount": None, "reason": "",
                }
                added += 1
        self._refresh_pending_tree()

        if added == 0:
            messagebox.showinfo("รายการซ้ำ", "สินค้าที่เลือกอยู่ในรายการปรับสต็อกอยู่แล้วทั้งหมด", parent=self)

    # ------------------------------------------------------- ขั้นที่ 2

    def _refresh_pending_tree(self):
        for row in self.pending_tree.get_children():
            self.pending_tree.delete(row)
        for product_id, entry in self._pending.items():
            product = entry["product"]
            direction_label = DIRECTION_LABELS.get(entry["direction"], "-")
            if entry["amount"]:
                unit_label = product["packUnit"] if entry["unit_mode"] == "pack" else product["baseUnit"]
                amount_label = f'{entry["amount"]:g} {unit_label}'
            else:
                amount_label = "(ยังไม่ได้กำหนด)"
            self.pending_tree.insert(
                "", "end", iid=str(product_id),
                values=(
                    product["sku"] or "-", product["name"], f'{product["currentStock"]} {product["baseUnit"]}',
                    direction_label, amount_label, entry["reason"] or "",
                ),
            )

    def _on_edit_pending_click(self):
        selection = self.pending_tree.selection()
        if not selection:
            return
        product_id = selection[0]
        entry = self._pending.get(product_id)
        if entry is None:
            return

        def handle_confirm(direction, unit_mode, amount, reason):
            entry["direction"] = direction
            entry["unit_mode"] = unit_mode
            entry["amount"] = amount
            entry["reason"] = reason
            self._refresh_pending_tree()
            return True

        StockAdjustPopup(
            self, entry["product"], on_confirm=handle_confirm,
            initial_direction=entry["direction"], initial_unit_mode=entry["unit_mode"],
            initial_amount=entry["amount"] or "", initial_reason=entry["reason"],
        )

    def _on_remove_pending_click(self):
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning(
                "ยังไม่ได้เลือกรายการ", "กรุณาเลือกรายการที่ต้องการลบออกจากรายการปรับสต็อกก่อน", parent=self,
            )
            return
        for row_id in selection:
            self._pending.pop(row_id, None)
        self._refresh_pending_tree()

    # ------------------------------------------------------- ขั้นที่ 3: บันทึก

    def _on_save_all_click(self):
        if not self._pending:
            messagebox.showwarning("ยังไม่มีรายการ", "กรุณาเพิ่มสินค้าเข้ารายการปรับสต็อกก่อน", parent=self)
            return

        ready = {pid: entry for pid, entry in self._pending.items() if entry["amount"]}
        if not ready:
            messagebox.showwarning(
                "ยังไม่ได้กำหนดจำนวน",
                "กรุณาดับเบิลคลิกแต่ละรายการเพื่อกำหนดรูปแบบและจำนวนที่ต้องการปรับก่อนบันทึก",
                parent=self,
            )
            return

        success_count = 0
        errors = []
        for product_id, entry in ready.items():
            product = entry["product"]
            base_amount = entry["amount"] * product["unitsPerPack"] if entry["unit_mode"] == "pack" else entry["amount"]
            base_amount = round(base_amount)
            change_amount = base_amount if entry["direction"] == "in" else -base_amount
            unit_label = product["packUnit"] if entry["unit_mode"] == "pack" else product["baseUnit"]
            try:
                stock_controller.adjust_stock(
                    product_id, change_amount, entry["reason"], self.current_user,
                    unit_label=unit_label, input_quantity=entry["amount"],
                )
                success_count += 1
                del self._pending[product_id]
            except ValueError as e:
                errors.append(f'{product["name"]}: {e}')

        self._refresh_pending_tree()
        self._on_search()  # รีเฟรชผลค้นหาให้เห็นจำนวนคงเหลือใหม่

        summary = f"ปรับสต็อกสำเร็จ {success_count} รายการ"
        if errors:
            summary += "\n\nรายการที่ไม่สำเร็จ (ยังค้างอยู่ในรายการให้แก้ไข):\n" + "\n".join(errors)
            messagebox.showwarning("บันทึกเสร็จบางส่วน", summary, parent=self)
        else:
            messagebox.showinfo("สำเร็จ", summary, parent=self)
