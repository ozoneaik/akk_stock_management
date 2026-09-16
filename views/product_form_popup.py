# -*- coding: utf-8 -*-
"""
views/product_form_popup.py
Popup ฟอร์มสำหรับ "เพิ่มสินค้าใหม่" และ "แก้ไขสินค้า" ใช้ฟอร์มเดียวกัน
ถ้าส่ง product_data เข้ามา = โหมดแก้ไข, ถ้าไม่ส่ง = โหมดเพิ่มใหม่

หมายเหตุ: รูปภาพสินค้าเลือกจากไฟล์ในเครื่องแล้วอัปโหลดขึ้น Cloudflare R2 ตอนกดบันทึก
เก็บ URL เต็มไว้ในฐานข้อมูล (image_url) เพราะฐานข้อมูลใช้ร่วมกับเว็บแอปที่รันอยู่บนเซิร์ฟเวอร์อื่น
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from PIL import Image, ImageTk

from controllers import product_controller, storage_controller
from views import ui_helpers
import config


class ProductFormPopup(tk.Toplevel):
    def __init__(self, parent, current_user, on_saved, product_data=None):
        super().__init__(parent)
        self.current_user = current_user
        self.on_saved = on_saved
        self.product_data = product_data
        self.is_edit_mode = product_data is not None

        self.title("แก้ไขสินค้า" if self.is_edit_mode else "เพิ่มสินค้าใหม่")
        self.resizable(False, False)
        self.grab_set()  # ทำให้เป็น modal ไม่ให้กดหน้าต่างหลักได้จนกว่าจะปิด popup นี้
        ui_helpers.center_window(self, 560, 700)

        self.price_entries = {}  # channel -> {"price": Entry, "discount": Entry}
        self.current_image_url = None  # URL รูปที่บันทึกอยู่ในฐานข้อมูลปัจจุบัน (โหมดแก้ไข)
        self.selected_local_image_path = None  # path ไฟล์รูปใหม่ที่เพิ่งเลือก ยังไม่ได้อัปโหลดจนกว่าจะกดบันทึก

        self._build_ui()
        if self.is_edit_mode:
            self._load_existing_data()
        self._refresh_image_preview()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        canvas_container = tk.Frame(self)
        canvas_container.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=540)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # เลื่อนด้วยล้อเมาส์/trackpad ได้ทั้งหน้าต่างป็อปอัพ (ไม่ใช่แค่ตอนชี้ตรงพื้นที่ canvas เปล่าๆ)
        # เพราะ event จะไต่ระดับ bindtags ขึ้นมาถึง Toplevel (self) เสมอถ้าวิดเจ็ตที่ชี้อยู่ไม่ได้ผูก event นี้ไว้เอง
        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
        self.bind("<Button-4>", _on_mousewheel)  # Linux เลื่อนขึ้น
        self.bind("<Button-5>", _on_mousewheel)  # Linux เลื่อนลง

        form = tk.Frame(scroll_frame, padx=20, pady=20)
        form.pack(fill="both", expand=True)

        # --- ข้อมูลพื้นฐาน ---
        self.code_entry = self._add_labeled_entry(form, "รหัสสินค้า *")
        self.name_entry = self._add_labeled_entry(form, "ชื่อสินค้า *")

        tk.Label(form, text="หมวดหมู่ *", font=ui_helpers.get_ui_font()).pack(anchor="w", pady=(8, 2))
        categories = product_controller.get_categories()
        category_names = [c["name"] for c in categories]
        self.category_combo = ttk.Combobox(form, values=category_names, font=ui_helpers.get_ui_font())
        self.category_combo.pack(fill="x")
        tk.Label(
            form, text="(พิมพ์ชื่อหมวดหมู่ใหม่ได้เลยถ้ายังไม่มีในลิสต์)",
            font=ui_helpers.get_ui_font(size=8), fg="#888888",
        ).pack(anchor="w")

        unit_frame = tk.Frame(form)
        unit_frame.pack(fill="x", pady=(8, 0))
        unit_col1 = tk.Frame(unit_frame)
        unit_col1.pack(side="left", expand=True, fill="x", padx=(0, 5))
        unit_col2 = tk.Frame(unit_frame)
        unit_col2.pack(side="left", expand=True, fill="x", padx=(5, 5))
        unit_col3 = tk.Frame(unit_frame)
        unit_col3.pack(side="left", expand=True, fill="x", padx=(5, 0))

        tk.Label(unit_col1, text="หน่วยนับย่อย * (เช่น ขวด, ซอง)", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.base_unit_entry = tk.Entry(unit_col1, font=ui_helpers.get_ui_font())
        self.base_unit_entry.pack(fill="x")

        tk.Label(unit_col2, text="หน่วยบรรจุ (เช่น ลัง)", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.pack_unit_entry = tk.Entry(unit_col2, font=ui_helpers.get_ui_font())
        self.pack_unit_entry.pack(fill="x")

        tk.Label(unit_col3, text="จำนวน/แพ็ค", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.units_per_pack_entry = tk.Entry(unit_col3, font=ui_helpers.get_ui_font())
        self.units_per_pack_entry.pack(fill="x")
        self.units_per_pack_entry.insert(0, "1")

        qty_frame = tk.Frame(form)
        qty_frame.pack(fill="x", pady=(8, 0))
        qty_col1 = tk.Frame(qty_frame)
        qty_col1.pack(side="left", expand=True, fill="x", padx=(0, 5))
        qty_col2 = tk.Frame(qty_frame)
        qty_col2.pack(side="left", expand=True, fill="x", padx=(5, 0))

        tk.Label(qty_col1, text="จำนวนคงเหลือเริ่มต้น *", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.quantity_entry = tk.Entry(qty_col1, font=ui_helpers.get_ui_font())
        self.quantity_entry.pack(fill="x")
        self.quantity_entry.insert(0, "0")
        if self.is_edit_mode:
            self.quantity_entry.config(state="disabled")
            tk.Label(
                qty_col1, text="(แก้ไขจำนวนสต็อกได้ที่หน้า 'ปรับสต็อกสินค้า' เท่านั้น)",
                font=ui_helpers.get_ui_font(size=8), fg="#888888", wraplength=250, justify="left",
            ).pack(anchor="w")

        tk.Label(qty_col2, text="แจ้งเตือนเมื่อเหลือน้อยกว่า *", font=ui_helpers.get_ui_font()).pack(anchor="w")
        self.threshold_entry = tk.Entry(qty_col2, font=ui_helpers.get_ui_font())
        self.threshold_entry.pack(fill="x")
        self.threshold_entry.insert(0, str(config.LOW_STOCK_DEFAULT_THRESHOLD))

        # --- รูปภาพสินค้า ---
        image_frame = tk.Frame(form)
        image_frame.pack(fill="x", pady=(15, 0))
        tk.Label(
            image_frame, text="รูปภาพสินค้า (เว้นว่างไว้จะใช้รูป default)",
            font=ui_helpers.get_ui_font(),
        ).pack(anchor="w")

        image_row = tk.Frame(image_frame)
        image_row.pack(fill="x", pady=(4, 0))
        self.image_preview_label = tk.Label(image_row)
        self.image_preview_label.pack(side="left", padx=(0, 10))

        image_col = tk.Frame(image_row)
        image_col.pack(side="left", fill="x", expand=True)
        self.image_status_label = tk.Label(
            image_col, text="ยังไม่ได้เลือกรูป", font=ui_helpers.get_ui_font(size=9), fg="#666666",
            anchor="w", justify="left", wraplength=300,
        )
        self.image_status_label.pack(fill="x", anchor="w")
        tk.Button(
            image_col, text="เลือกรูปภาพ...", command=self._on_choose_image_click, font=ui_helpers.get_ui_font(size=9),
        ).pack(anchor="w", pady=(5, 0))

        # --- ราคาต่อช่องทางขาย ---
        tk.Label(
            form, text="ราคาขายแต่ละช่องทาง (ใส่เฉพาะช่องทางที่ขายจริง)",
            font=ui_helpers.get_ui_font(bold=True),
        ).pack(anchor="w", pady=(18, 5))

        price_table = tk.Frame(form)
        price_table.pack(fill="x")
        tk.Label(price_table, text="ช่องทาง", font=ui_helpers.get_ui_font(size=9, bold=True), width=12).grid(row=0, column=0)
        tk.Label(price_table, text="ราคา (บาท)", font=ui_helpers.get_ui_font(size=9, bold=True), width=14).grid(row=0, column=1)
        tk.Label(price_table, text="ส่วนลด (บาท)", font=ui_helpers.get_ui_font(size=9, bold=True), width=14).grid(row=0, column=2)

        for i, channel in enumerate(config.SALES_CHANNELS, start=1):
            tk.Label(
                price_table, text=config.CHANNEL_LABELS.get(channel, channel), font=ui_helpers.get_ui_font(),
                width=12, anchor="w",
            ).grid(row=i, column=0, sticky="w", pady=3)
            price_entry = tk.Entry(price_table, font=ui_helpers.get_ui_font(), width=14)
            price_entry.grid(row=i, column=1, padx=5)
            discount_entry = tk.Entry(price_table, font=ui_helpers.get_ui_font(), width=14)
            discount_entry.grid(row=i, column=2, padx=5)
            self.price_entries[channel] = {"price": price_entry, "discount": discount_entry}

        # --- หมายเหตุ ---
        tk.Label(form, text="หมายเหตุ (ถ้ามี)", font=ui_helpers.get_ui_font()).pack(anchor="w", pady=(15, 2))
        self.note_entry = tk.Entry(form, font=ui_helpers.get_ui_font())
        self.note_entry.pack(fill="x")

        # --- ปุ่ม ---
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

    def _add_labeled_entry(self, parent, label_text):
        tk.Label(parent, text=label_text, font=ui_helpers.get_ui_font()).pack(anchor="w", pady=(8, 2))
        entry = tk.Entry(parent, font=ui_helpers.get_ui_font())
        entry.pack(fill="x")
        return entry

    def _on_choose_image_click(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="เลือกรูปภาพสินค้า",
            filetypes=[("รูปภาพ", "*.jpg *.jpeg *.png *.gif *.webp *.bmp"), ("ทุกไฟล์", "*.*")],
        )
        if not file_path:
            return
        self.selected_local_image_path = file_path
        self.image_status_label.config(text=os.path.basename(file_path))
        self._refresh_image_preview()

    def _refresh_image_preview(self):
        if self.selected_local_image_path:
            try:
                img = Image.open(self.selected_local_image_path).convert("RGB")
                img.thumbnail((90, 90))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                photo = ui_helpers.load_photo_image(None, size=(90, 90))
        else:
            photo = ui_helpers.load_photo_image(self.current_image_url, size=(90, 90))
        self.image_preview_label.config(image=photo)
        self.image_preview_label.image = photo  # เก็บ reference กัน garbage collect

    # ------------------------------------------------------------- ข้อมูล

    def _load_existing_data(self):
        data = self.product_data
        self.code_entry.insert(0, data["sku"] or "")
        self.code_entry.config(state="disabled")  # ไม่ให้แก้รหัสสินค้าเพื่อป้องกันข้อมูลชนกัน
        self.name_entry.insert(0, data["name"])
        self.category_combo.set(data.get("category_name", ""))
        self.base_unit_entry.insert(0, data["base_unit"])
        self.pack_unit_entry.insert(0, data["pack_unit"] or "")
        self.units_per_pack_entry.delete(0, tk.END)
        self.units_per_pack_entry.insert(0, str(data["units_per_pack"]))

        self.quantity_entry.config(state="normal")
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, str(data["current_stock"]))
        self.quantity_entry.config(state="disabled")

        self.threshold_entry.delete(0, tk.END)
        self.threshold_entry.insert(0, str(data["min_stock_alert"]))
        self.current_image_url = data.get("image_url") or None
        if self.current_image_url:
            self.image_status_label.config(text=self.current_image_url)
        self.note_entry.insert(0, data.get("description") or "")

        for channel, price_info in data.get("prices", {}).items():
            if channel in self.price_entries:
                self.price_entries[channel]["price"].insert(0, str(price_info["price"]))
                self.price_entries[channel]["discount"].insert(0, str(price_info["discount"]))

    def _collect_prices(self):
        prices = {}
        for channel, entries in self.price_entries.items():
            price_text = entries["price"].get().strip()
            discount_text = entries["discount"].get().strip()
            if price_text:
                prices[channel] = {
                    "price": float(price_text),
                    "discount": float(discount_text) if discount_text else 0,
                }
        return prices

    def _on_save_click(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        category_name = self.category_combo.get().strip()
        base_unit = self.base_unit_entry.get().strip()
        pack_unit = self.pack_unit_entry.get().strip()

        if not category_name:
            messagebox.showwarning("ข้อมูลไม่ครบถ้วน", "กรุณาเลือกหรือพิมพ์หมวดหมู่สินค้า", parent=self)
            return

        try:
            prices = self._collect_prices()
        except ValueError:
            messagebox.showwarning("ข้อมูลราคาไม่ถูกต้อง", "ราคาและส่วนลดต้องเป็นตัวเลขเท่านั้น", parent=self)
            return

        # ถ้าผู้ใช้เลือกรูปใหม่ อัปโหลดขึ้น R2 ก่อนตั้งแต่ตอนนี้ เพื่อให้ได้ URL เต็มไปเก็บลงฐานข้อมูล
        new_image_url = self.current_image_url
        uploaded_new_image = False
        if self.selected_local_image_path:
            try:
                new_image_url = storage_controller.upload_product_image(self.selected_local_image_path, code)
                uploaded_new_image = True
            except Exception as e:
                messagebox.showerror("อัปโหลดรูปภาพไม่สำเร็จ", f"ไม่สามารถอัปโหลดรูปภาพขึ้น cloud ได้: {e}", parent=self)
                return

        data = {
            "code": code,
            "name": name,
            "category_id": None,
            "packaging_unit": base_unit,
            "pack_unit": pack_unit,
            "units_per_pack": self.units_per_pack_entry.get().strip(),
            "quantity": self.product_data["current_stock"] if self.is_edit_mode else self.quantity_entry.get().strip(),
            "low_stock_threshold": self.threshold_entry.get().strip(),
            "image_path": new_image_url,
            "note": self.note_entry.get().strip(),
            "prices": prices,
        }

        error = product_controller.validate_product_data(data)
        if error:
            messagebox.showwarning("ข้อมูลไม่ครบถ้วน", error, parent=self)
            if uploaded_new_image:
                storage_controller.delete_product_image(new_image_url)
            return

        data["category_id"] = product_controller.get_or_create_category(category_name)

        old_image_url = self.product_data.get("image_url") if self.is_edit_mode else None

        try:
            if self.is_edit_mode:
                product_controller.update_product(self.product_data["id"], data, self.current_user)
                messagebox.showinfo("สำเร็จ", "แก้ไขข้อมูลสินค้าเรียบร้อยแล้ว", parent=self)
            else:
                product_controller.create_product(data, self.current_user)
                messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าใหม่เรียบร้อยแล้ว", parent=self)
        except ValueError as e:
            messagebox.showwarning("ไม่สามารถบันทึกได้", str(e), parent=self)
            if uploaded_new_image:
                storage_controller.delete_product_image(new_image_url)
            return
        except Exception as e:  # เผื่อ code ซ้ำ (UNIQUE constraint) หรือข้อผิดพลาดอื่นๆ จากฐานข้อมูล
            messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลได้: {e}", parent=self)
            if uploaded_new_image:
                storage_controller.delete_product_image(new_image_url)
            return

        # บันทึกสำเร็จแล้วค่อยลบรูปเก่าทิ้ง เพื่อประหยัดพื้นที่ cloud โดยไม่เสี่ยงเหลือสินค้าไม่มีรูปถ้าขั้นตอนก่อนหน้าล้มเหลว
        if uploaded_new_image and old_image_url:
            storage_controller.delete_product_image(old_image_url)

        if self.on_saved:
            self.on_saved()
        self.destroy()
