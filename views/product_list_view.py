# -*- coding: utf-8 -*-
"""
views/product_list_view.py
หน้ารายการสินค้า: แสดงตาราง (รหัส, ชื่อ, จำนวน, รูปภาพย่อ) ค้นหาได้
และเปิดดูรายละเอียดสินค้าแบบ popup เมื่อกดปุ่ม "ดูรายละเอียด" หรือดับเบิลคลิก
"""

import tkinter as tk
from tkinter import ttk

from controllers import product_controller
from views import ui_helpers
from views.product_detail_popup import ProductDetailPopup
import config


class ProductListView(tk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent, bg="white")
        self.current_user = current_user
        self._thumbnail_cache = []  # กัน PhotoImage โดน garbage collect
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = tk.Label(
            self, text="รายการสินค้าทั้งหมด", font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            bg="white", anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        search_row = tk.Frame(self, bg="white")
        search_row.pack(fill="x", padx=20)
        tk.Label(search_row, text="ค้นหา (รหัสสินค้า/ชื่อสินค้า):", font=ui_helpers.get_ui_font(), bg="white").pack(
            side="left"
        )
        self.search_entry = tk.Entry(search_row, font=ui_helpers.get_ui_font())
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.search_entry.bind("<Return>", lambda e: self.refresh())
        tk.Button(search_row, text="ค้นหา", font=ui_helpers.get_ui_font(), command=self.refresh).pack(side="left")
        tk.Button(search_row, text="ล้างค้นหา", font=ui_helpers.get_ui_font(), command=self._clear_search).pack(
            side="left", padx=(5, 0)
        )

        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        ui_helpers.configure_treeview_style()
        columns = ("code", "name", "category", "quantity", "unit")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        headings = {"code": "รหัสสินค้า", "name": "ชื่อสินค้า", "category": "หมวดหมู่", "quantity": "คงเหลือ", "unit": "หน่วย"}
        widths = {"code": 100, "name": 300, "category": 160, "quantity": 90, "unit": 80}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._open_selected_detail())
        self.tree.tag_configure("low", background="#fff3cd")

        bottom_row = tk.Frame(self, bg="white")
        bottom_row.pack(fill="x", padx=20, pady=(0, 20))
        tk.Button(
            bottom_row, text="ดูรายละเอียดสินค้าที่เลือก", font=ui_helpers.get_ui_font(bold=True),
            command=self._open_selected_detail, cursor="hand2",
        ).pack(side="left")
        tk.Label(
            bottom_row, text="เคล็ดลับ: ดับเบิลคลิกที่แถวสินค้าเพื่อดูรายละเอียดได้เช่นกัน",
            font=ui_helpers.get_ui_font(size=8), fg="#888888", bg="white",
        ).pack(side="left", padx=15)

    def _clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh()

    def refresh(self):
        loading = ui_helpers.show_loading(self)
        try:
            keyword = self.search_entry.get().strip()
            products = product_controller.list_products(keyword or None)

            for row in self.tree.get_children():
                self.tree.delete(row)

            self._product_by_row = {}
            for product in products:
                tag = "low" if product["currentStock"] < product["minStockAlert"] else ""
                row_id = self.tree.insert(
                    "", "end",
                    values=(product["sku"] or "-", product["name"], product["category_name"], product["currentStock"], product["baseUnit"]),
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
