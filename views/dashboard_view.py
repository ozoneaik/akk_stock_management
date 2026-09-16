# -*- coding: utf-8 -*-
"""
views/dashboard_view.py
หน้า Dashboard: แสดงจำนวนสินค้าทั้งหมด, ยอดรวมสต็อก, และรายการสินค้าที่เหลือน้อยกว่าค่าขั้นต่ำ
"""

import tkinter as tk
from tkinter import ttk

from controllers import product_controller
from views import ui_helpers
from views.product_detail_popup import ProductDetailPopup
import config


class DashboardView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._product_by_row = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Label(
            self, text="ภาพรวมสต็อกสินค้า", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        # --- การ์ดสรุปตัวเลข ---
        cards_frame = tk.Frame(self, bg="white")
        cards_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.total_products_card = self._create_summary_card(cards_frame, "จำนวนสินค้าทั้งหมด", "0 รายการ")
        self.total_products_card.pack(side="left", expand=True, fill="both", padx=(0, 10))

        self.total_quantity_card = self._create_summary_card(cards_frame, "จำนวนสต็อกรวมทั้งหมด", "0 ชิ้น")
        self.total_quantity_card.pack(side="left", expand=True, fill="both", padx=(10, 10))

        self.low_stock_card = self._create_summary_card(cards_frame, "รายการที่สต็อกใกล้หมด", "0 รายการ", highlight=True)
        self.low_stock_card.pack(side="left", expand=True, fill="both", padx=(10, 0))

        # --- ตารางสินค้าที่สต็อกใกล้หมด ---
        low_stock_label = tk.Label(
            self, text=f"สินค้าที่มีจำนวนคงเหลือน้อยกว่าเกณฑ์ (ค่าเริ่มต้น {config.LOW_STOCK_DEFAULT_THRESHOLD})",
            font=ui_helpers.get_ui_font(bold=True), bg="white", anchor="w",
        )
        low_stock_label.pack(fill="x", padx=20)

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        ui_helpers.configure_treeview_style()
        columns = ("code", "name", "category", "quantity", "unit", "threshold")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        headings = {
            "code": "รหัสสินค้า", "name": "ชื่อสินค้า", "category": "หมวดหมู่",
            "quantity": "คงเหลือ", "unit": "หน่วย", "threshold": "เกณฑ์แจ้งเตือน",
        }
        widths = {"code": 100, "name": 260, "category": 150, "quantity": 80, "unit": 80, "threshold": 110}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._open_selected_detail())
        self.tree.tag_configure("critical", background="#ffe5e5")

    def _create_summary_card(self, parent, title, value_text, highlight=False):
        card = tk.Frame(parent, bg="#fafafa", highlightbackground="#dddddd", highlightthickness=1)
        title_label = tk.Label(card, text=title, font=ui_helpers.get_ui_font(size=10), bg="#fafafa", fg="#666666")
        title_label.pack(pady=(15, 5))
        value_label = tk.Label(
            card, text=value_text, font=ui_helpers.get_ui_font(size=20, bold=True),
            bg="#fafafa", fg="#c0392b" if highlight else "#222222",
        )
        value_label.pack(pady=(0, 15))
        card.value_label = value_label
        return card

    def refresh(self):
        """เรียกทุกครั้งที่กลับมาที่หน้านี้ เพื่อให้ข้อมูลเป็นปัจจุบันเสมอ"""
        loading = ui_helpers.show_loading(self)
        try:
            data = product_controller.get_dashboard_data()

            self.total_products_card.value_label.config(text=f"{data['total_products']:,} รายการ")
            self.total_quantity_card.value_label.config(text=f"{data['total_quantity']:,} ชิ้น")
            self.low_stock_card.value_label.config(text=f"{data['low_stock_count']:,} รายการ")

            for row in self.tree.get_children():
                self.tree.delete(row)

            self._product_by_row = {}
            for product in data["low_stock_items"]:
                tag = "critical" if product["current_stock"] <= product["min_stock_alert"] / 2 else ""
                row_id = self.tree.insert(
                    "", "end",
                    values=(
                        product["sku"] or "-", product["name"], product["category_name"],
                        product["current_stock"], product["base_unit"], product["min_stock_alert"],
                    ),
                    tags=(tag,) if tag else (),
                )
                self._product_by_row[row_id] = product["id"]
        finally:
            loading.destroy()

    def _open_selected_detail(self):
        selection = self.tree.selection()
        if not selection:
            return
        product_id = self._product_by_row.get(selection[0])
        if product_id is None:
            return
        ProductDetailPopup(self, self.current_user, product_id, on_changed=self.refresh)
