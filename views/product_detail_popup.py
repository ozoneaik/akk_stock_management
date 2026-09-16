# -*- coding: utf-8 -*-
"""
views/product_detail_popup.py
Popup แสดงรายละเอียดสินค้าแบบเต็ม (ราคาทุกช่องทาง, หมวดหมู่, หมายเหตุ, รูปภาพ)
มีปุ่มแก้ไขและลบสินค้าให้ในหน้านี้ด้วย
"""

import tkinter as tk
from tkinter import messagebox

from controllers import product_controller, stock_controller
from views import ui_helpers
from views.stock_adjust_popup import StockAdjustPopup
import config


class ProductDetailPopup(tk.Toplevel):
    def __init__(self, parent, current_user, product_id, on_changed):
        super().__init__(parent)
        self.current_user = current_user
        self.product_id = product_id
        self.on_changed = on_changed  # เรียกกลับเมื่อมีการแก้ไข/ลบ เพื่อให้หน้ารายการ refresh

        self.title("รายละเอียดสินค้า")
        self.resizable(False, False)
        self.grab_set()
        ui_helpers.center_window(self, 480, 560)

        self._build_ui()

    def _build_ui(self):
        product = product_controller.get_product(self.product_id)
        if product is None:
            tk.Label(self, text="ไม่พบสินค้านี้ในระบบแล้ว", font=ui_helpers.get_ui_font()).pack(pady=30)
            return

        # ปุ่มด้านล่างตรึงตำแหน่งไว้นอกพื้นที่เลื่อน pack ก่อนเพื่อจองพื้นที่จาก side="bottom"
        button_area = tk.Frame(self)
        button_area.pack(fill="x", side="bottom")

        tk.Button(
            button_area, text="ปรับสต็อกสินค้า", font=ui_helpers.get_ui_font(bold=True), fg="white", bg="#2e7d32",
            command=lambda: self._on_adjust_stock_click(product), cursor="hand2",
        ).pack(fill="x", padx=20, pady=(10, 15), ipady=6)

        button_row = tk.Frame(button_area)
        button_row.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(
            button_row, text="แก้ไขสินค้า", font=ui_helpers.get_ui_font(bold=True),
            command=lambda: self._on_edit_click(product), cursor="hand2",
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(0, 5))
        tk.Button(
            button_row, text="ลบสินค้า", font=ui_helpers.get_ui_font(bold=True), fg="white", bg="#c0392b",
            command=lambda: self._on_delete_click(product), cursor="hand2",
        ).pack(side="left", expand=True, fill="x", ipady=6, padx=(5, 0))

        # พื้นที่เนื้อหาแบบเลื่อนได้ ใช้ Canvas + Scrollbar เพราะ tkinter ไม่มี scroll ในตัว
        scroll_area = tk.Frame(self)
        scroll_area.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_area, highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        container = tk.Frame(canvas, padx=20, pady=20)
        container_id = canvas.create_window((0, 0), window=container, anchor="nw")

        def _on_container_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(container_id, width=event.width)

        container.bind("<Configure>", _on_container_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(_event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        photo = ui_helpers.load_photo_image(product["image_url"], size=(150, 150))
        image_label = tk.Label(container, image=photo)
        image_label.image = photo
        image_label.pack(pady=(0, 15))
        

        tk.Label(
            container, text=product["name"], font=ui_helpers.get_ui_font(size=config.UI_FONT_SIZE_HEADER, bold=True),
            wraplength=420,
        ).pack()
        tk.Label(
            container, text=f'รหัสสินค้า: {product["sku"] or "-"}', font=ui_helpers.get_ui_font(size=9), fg="#666666",
        ).pack(pady=(0, 10))

        self._add_info_row(container, "หมวดหมู่", product["category_name"])
        if product["pack_unit"]:
            self._add_info_row(
                container, "หน่วยบรรจุ", f'1 {product["pack_unit"]} = {product["units_per_pack"]} {product["base_unit"]}'
            )
        self._add_info_row(container, "จำนวนคงเหลือ", f'{product["current_stock"]} {product["base_unit"]}')
        self._add_info_row(container, "แจ้งเตือนเมื่อเหลือน้อยกว่า", str(product["min_stock_alert"]))

        tk.Label(container, text="ราคาขาย", font=ui_helpers.get_ui_font(bold=True), anchor="w").pack(
            fill="x", pady=(12, 4)
        )
        if product["prices"]:
            for channel, price_info in product["prices"].items():
                price_text = ui_helpers.format_currency(price_info["price"])
                if price_info["discount"]:
                    price_text += f'  (ส่วนลด {ui_helpers.format_currency(price_info["discount"])})'
                self._add_info_row(container, channel, price_text)
        else:
            tk.Label(container, text="ยังไม่ได้ตั้งราคา", font=ui_helpers.get_ui_font(size=9), fg="#999999").pack(
                anchor="w"
            )

        if product.get("description"):
            tk.Label(container, text="หมายเหตุ", font=ui_helpers.get_ui_font(bold=True), anchor="w").pack(
                fill="x", pady=(12, 4)
            )
            tk.Label(container, text=product["description"], font=ui_helpers.get_ui_font(size=9), wraplength=420, justify="left").pack(
                anchor="w"
            )

    def _add_info_row(self, parent, label_text, value_text):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"{label_text}:", font=ui_helpers.get_ui_font(size=9), fg="#666666", width=22, anchor="w").pack(
            side="left"
        )
        tk.Label(row, text=value_text, font=ui_helpers.get_ui_font(size=9), anchor="w", wraplength=250, justify="left").pack(
            side="left", fill="x", expand=True
        )

    def _refresh(self):
        """สร้างเนื้อหาใหม่ทั้งหมดโดยดึงข้อมูลสินค้าล่าสุดจากฐานข้อมูล ใช้หลังปรับสต็อกสำเร็จ"""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()

    def _on_adjust_stock_click(self, product):
        def handle_confirm(direction, unit_mode, amount, reason):
            base_amount = amount * product["units_per_pack"] if unit_mode == "pack" else amount
            base_amount = round(base_amount)
            change_amount = base_amount if direction == "in" else -base_amount
            unit_label = product["pack_unit"] if unit_mode == "pack" else product["base_unit"]
            try:
                new_quantity = stock_controller.adjust_stock(
                    product["id"], change_amount, reason, self.current_user,
                    unit_label=unit_label, input_quantity=amount,
                )
            except ValueError as e:
                messagebox.showwarning("ไม่สามารถบันทึกได้", str(e), parent=self)
                return False

            messagebox.showinfo(
                "สำเร็จ", f'ปรับสต็อกเรียบร้อยแล้ว คงเหลือใหม่: {new_quantity} {product["base_unit"]}', parent=self,
            )
            self._refresh()
            if self.on_changed:
                self.on_changed()
            return True

        StockAdjustPopup(self, product, on_confirm=handle_confirm)

    def _on_edit_click(self, product):
        from views.product_form_popup import ProductFormPopup

        self.destroy()
        ProductFormPopup(self.master, self.current_user, on_saved=self.on_changed, product_data=product)

    def _on_delete_click(self, product):
        confirmed = messagebox.askyesno(
            "ยืนยันการลบสินค้า",
            f'ต้องการลบสินค้า "{product["name"]}" (รหัส {product["sku"] or "-"}) ใช่หรือไม่?\nการลบไม่สามารถกู้คืนได้',
            parent=self,
        )
        if not confirmed:
            return
        try:
            product_controller.delete_product(product["id"], self.current_user)
        except ValueError as e:
            messagebox.showwarning("ไม่สามารถลบได้", str(e), parent=self)
            return

        messagebox.showinfo("สำเร็จ", "ลบสินค้าเรียบร้อยแล้ว", parent=self)
        self.destroy()
        if self.on_changed:
            self.on_changed()
