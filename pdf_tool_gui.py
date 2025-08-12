import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
import io
try:
    resample_filter = Image.Resampling.LANCZOS
except AttributeError:
    try:
        resample_filter = Image.LANCZOS
    except AttributeError:
        resample_filter = Image.BICUBIC

# دالة استخراج الصفحات
def extract_pages(pdf_path, selected_pages, output_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page_num in selected_pages:
        if 0 <= page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    with open(output_path, 'wb') as f:
        writer.write(f)

# دالة حذف الصفحات
def delete_pages(pdf_path, pages_to_delete, output_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    pages_to_delete = set(pages_to_delete)
    for i in range(total_pages):
        if i not in pages_to_delete:
            writer.add_page(reader.pages[i])
    with open(output_path, 'wb') as f:
        writer.write(f)

# دالة دمج صفحات من عدة ملفات
def merge_pdfs(pdfs_with_pages, output_path):
    writer = PdfWriter()
    for pdf_path, page_indices in pdfs_with_pages:
        reader = PdfReader(pdf_path)
        for page_num in page_indices:
            if 0 <= page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
    with open(output_path, 'wb') as f:
        writer.write(f)

# دالة تحويل PDF إلى صور باستخدام PyMuPDF (أسرع)
def convert_pdf_to_images(pdf_path, size=None):
    """تحويل PDF إلى صور باستخدام PyMuPDF - أسرع بكثير"""
    try:
        doc = fitz.open(pdf_path)
        images = []
        
        # تحديد حجم الصور المصغرة
        if size:
            scale_x = size[0] / 595  # عرض A4
            scale_y = size[1] / 842  # ارتفاع A4
            scale = min(scale_x, scale_y)
            matrix = fitz.Matrix(scale, scale)
        else:
            matrix = fitz.Matrix(1, 1)  # الحجم الكامل
        
        for page in doc:
            pix = page.get_pixmap(matrix=matrix)
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        
        doc.close()
        return images
    except Exception as e:
        raise Exception(f"خطأ في تحويل PDF: {str(e)}")

# دالة معاينة محسنة للاستخراج والحذف
def show_full_preview_lazy_simple(pdf_path, page_idx):
    """تحميل وعرض صفحة كاملة عند الحاجة"""
    try:
        full_images = convert_pdf_to_images(pdf_path)
        show_full_preview(full_images[page_idx])
    except Exception as e:
        messagebox.showerror("خطأ", "لا يمكن تحميل الصورة الكاملة")

# دالة عرض معاينة كاملة للصورة
def show_full_preview(img):
    win = tk.Toplevel()
    win.title("معاينة الصفحة كاملة")
    # تكبير الصورة للعرض الكامل (أو حسب حجم الشاشة)
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    # تصغير إذا كانت الصورة أكبر من الشاشة
    max_w, max_h = screen_w - 100, screen_h - 100
    w, h = img.size
    scale = min(max_w / w, max_h / h, 1)
    new_size = (int(w * scale), int(h * scale))
    img_resized = img.resize(new_size, resample_filter)
    img_tk = ImageTk.PhotoImage(img_resized)
    lbl = tk.Label(win, image=img_tk)
    lbl.image = img_tk
    lbl.pack()
    win.focus_set()
    win.grab_set()
    win.transient()
    win.mainloop()

class PDFToolGUI:
    def __init__(self, root):
        self.root = root
        root.title("أداة دمج وتحرير PDF")
        root.geometry("500x700")
        root.resizable(False, False)
        self._thumbnails_refs = []  # للاحتفاظ بمراجع الصور المصغرة

        self.label = tk.Label(root, text="اختر الصفحات من عدة ملفات PDF ورتبها كما تريد ثم اضغط دمج", font=("Arial", 13))
        self.label.pack(pady=10)

        self.btn_merge = tk.Button(root, text="دمج صفحات من عدة ملفات (اختيار وتحرير)", width=40, command=self.merge_pages_ui)
        self.btn_merge.pack(pady=20)

    def extract_pages_ui(self):
        pdf_path = filedialog.askopenfilename(title="اختر ملف PDF", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_path:
            return
        try:
            images = convert_pdf_to_images(pdf_path, size=(120, 160))
        except Exception as e:
            messagebox.showerror("خطأ في تحويل PDF إلى صور", str(e))
            return
        self.show_page_selector(images, None, pdf_path, mode='extract')

    def delete_pages_ui(self):
        pdf_path = filedialog.askopenfilename(title="اختر ملف PDF", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_path:
            return
        try:
            images = convert_pdf_to_images(pdf_path, size=(120, 160))
        except Exception as e:
            messagebox.showerror("خطأ في تحويل PDF إلى صور", str(e))
            return
        self.show_page_selector(images, None, pdf_path, mode='delete')

    def show_page_selector(self, images, full_images, pdf_path, mode='extract'):
        # إذا كانت full_images هي None، نستخدم التحميل المحسن
        use_lazy_loading = full_images is None
        win = tk.Toplevel(self.root)
        if mode == 'extract':
            win.title("اختر الصفحات التي تريد استخراجها")
        else:
            win.title("اختر الصفحات التي تريد حذفها")
        win.geometry("400x600")
        container = tk.Frame(win)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        page_vars = []
        thumbnails = []
        for idx, img in enumerate(images):
            thumb = ImageTk.PhotoImage(img)
            thumbnails.append(thumb)
            frame = ttk.Frame(scrollable_frame, relief="ridge", borderwidth=2)
            frame.pack(fill="x", padx=10, pady=5)
            lbl = ttk.Label(frame, image=thumb)
            lbl.pack(side="left", padx=5)
            if use_lazy_loading:
                lbl.bind("<Button-1>", lambda e, i=idx: show_full_preview_lazy_simple(pdf_path, i))
            else:
                lbl.bind("<Button-1>", lambda e, i=idx: show_full_preview(full_images[i]))
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(frame, text=f"صفحة {idx+1}", variable=var)
            chk.pack(side="left", padx=10)
            page_vars.append(var)
        self._thumbnails_refs.append(thumbnails)

        def select_all():
            for v in page_vars:
                v.set(True)
        def deselect_all():
            for v in page_vars:
                v.set(False)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=5, side="bottom")
        btn_select_all = tk.Button(btn_frame, text="تحديد الكل", command=select_all)
        btn_select_all.pack(side="left", padx=5)
        btn_deselect_all = tk.Button(btn_frame, text="إلغاء التحديد", command=deselect_all)
        btn_deselect_all.pack(side="left", padx=5)

        def on_action():
            selected = [i for i, v in enumerate(page_vars) if v.get()]
            if not selected:
                messagebox.showwarning("تنبيه", "يرجى اختيار صفحة واحدة على الأقل!")
                return
            output_path = filedialog.asksaveasfilename(title="حفظ الملف الناتج", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if not output_path:
                return
            try:
                if mode == 'extract':
                    extract_pages(pdf_path, selected, output_path)
                    messagebox.showinfo("نجاح", f"تم استخراج الصفحات إلى: {output_path}")
                else:
                    delete_pages(pdf_path, selected, output_path)
                    messagebox.showinfo("نجاح", f"تم حذف الصفحات وحفظ الملف في: {output_path}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("خطأ", str(e))

        btn_text = "استخراج الصفحات المحددة" if mode == 'extract' else "حذف الصفحات المحددة"
        btn_action = tk.Button(btn_frame, text=btn_text, font=("Arial", 12), command=on_action)
        btn_action.pack(side="left", padx=5)

    def merge_pages_ui(self):
        pdf_paths = filedialog.askopenfilenames(title="اختر ملفات PDF للدمج", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_paths:
            return
        # بناء قائمة كائنات لكل صفحة
        class PageItem:
            def __init__(self, thumb, full_img, file_path, file_name, page_idx):
                self.thumb = thumb
                self.full_img = full_img
                self.file_path = file_path
                self.file_name = file_name
                self.page_idx = page_idx
                self.var = tk.BooleanVar(value=False)
        page_items = []
        all_pdf_paths = list(pdf_paths)  # قائمة قابلة للتعديل تحتوي على جميع الملفات
        
        # إضافة شريط التقدم
        progress_window = tk.Toplevel(self.root)
        progress_window.title("جاري تحميل الملفات...")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(progress_window, text="جاري تحميل الملفات...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, mode='determinate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        
        total_files = len(pdf_paths)
        progress_bar['maximum'] = total_files
        
        for file_idx, pdf_path in enumerate(pdf_paths):
            try:
                # تحديث شريط التقدم
                progress_label.config(text=f"جاري تحميل: {os.path.basename(pdf_path)}")
                progress_bar['value'] = file_idx + 1
                progress_window.update()
                
                # تحسين: تحويل الصور المصغرة فقط (بدون الصور الكاملة)
                images = convert_pdf_to_images(pdf_path, size=(60, 80))  # تقليل أكثر
                
                # تحسين: عدم تحميل الصور الكاملة إلا عند الحاجة
                full_images = None  # سيتم تحميلها عند النقر فقط
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("خطأ في تحويل PDF إلى صور", str(e))
                return
            for i, img in enumerate(images):
                thumb = ImageTk.PhotoImage(img)
                page_items.append(PageItem(thumb, None, pdf_path, os.path.basename(pdf_path), i))
        
        # إغلاق نافذة التقدم
        progress_window.destroy()
        
        self._thumbnails_refs.append([p.thumb for p in page_items])
        win = tk.Toplevel(self.root)
        win.title("اختر ورتب الصفحات من جميع الملفات للدمج (اسحب وأفلت)")
        win.geometry("500x700")
        container = tk.Frame(win)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # دالة معاينة محسنة (تحميل عند الحاجة)
        def show_full_preview_lazy(page_item):
            if page_item.full_img is None:
                # تحميل الصورة الكاملة عند الحاجة فقط
                try:
                    full_images = convert_pdf_to_images(page_item.file_path)
                    page_item.full_img = full_images[page_item.page_idx]
                except Exception as e:
                    messagebox.showerror("خطأ", "لا يمكن تحميل الصورة الكاملة")
                    return
            show_full_preview(page_item.full_img)

        # دالة تكرار الصفحة
        def duplicate_page(page_idx):
            if 0 <= page_idx < len(page_items):
                original_item = page_items[page_idx]
                # إنشاء نسخة جديدة من الصفحة
                new_item = PageItem(
                    original_item.thumb,
                    original_item.full_img,
                    original_item.file_path,
                    original_item.file_name,
                    original_item.page_idx
                )
                # إدراج النسخة بعد الصفحة الأصلية
                page_items.insert(page_idx + 1, new_item)
                # إضافة الصورة المصغرة للقائمة المرجعية
                self._thumbnails_refs[-1].append(new_item.thumb)
                # إعادة رسم سريع
                draw_page_items()

        # دالة حذف الصفحة
        def delete_page(page_idx):
            if 0 <= page_idx < len(page_items):
                # إزالة الصورة المصغرة من القائمة المرجعية
                if page_items[page_idx].thumb in self._thumbnails_refs[-1]:
                    self._thumbnails_refs[-1].remove(page_items[page_idx].thumb)
                # حذف الصفحة من القائمة
                page_items.pop(page_idx)
                draw_page_items()

        # رسم العناصر
        def draw_page_items():
            # حذف العناصر الموجودة
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            # إنشاء العناصر الجديدة
            for idx, item in enumerate(page_items):
                frame = ttk.Frame(scrollable_frame, relief="ridge", borderwidth=2)
                frame.pack(fill="x", padx=10, pady=5)
                
                # الصورة المصغرة
                lbl = ttk.Label(frame, image=item.thumb)
                lbl.pack(side="left", padx=5)
                lbl.bind("<Button-1>", lambda e, i=idx: show_full_preview_lazy(page_items[i]))
                
                # إطار للنص والأزرار
                text_frame = tk.Frame(frame)
                text_frame.pack(side="left", fill="x", expand=True, padx=5)
                
                # النص
                chk = ttk.Checkbutton(text_frame, text=f"{item.file_name} - صفحة {item.page_idx+1}", variable=item.var)
                chk.pack(side="top", anchor="w")
                
                # إطار للأزرار
                btn_frame_inner = tk.Frame(text_frame)
                btn_frame_inner.pack(side="top", pady=2)
                
                # زر التكرار
                btn_duplicate = tk.Button(btn_frame_inner, text="تكرار", width=8, bg="lightblue",
                                        command=lambda i=idx: duplicate_page(i))
                btn_duplicate.pack(side="left", padx=2)
                
                # زر الحذف
                btn_delete = tk.Button(btn_frame_inner, text="حذف", width=8, bg="lightcoral",
                                     command=lambda i=idx: delete_page(i))
                btn_delete.pack(side="left", padx=2)
                
                # ربط السحب والإفلات
                frame.bind("<ButtonPress-1>", lambda e, i=idx: on_drag_start(e, i))
                frame.bind("<B1-Motion>", on_drag_motion)
                frame.bind("<ButtonRelease-1>", lambda e, i=idx: on_drag_release(e, i))
                
                # إضافة مؤشر بصري للسحب
                frame.bind("<Enter>", lambda e: frame.configure(cursor="hand2"))
                frame.bind("<Leave>", lambda e: frame.configure(cursor=""))
                
                # منع تضارب الأحداث مع النقر على الصورة
                lbl.bind("<ButtonPress-1>", lambda e: e.widget.focus_set())
                lbl.bind("<Button-1>", lambda e, i=idx: show_full_preview_lazy(page_items[i]))
                
                # منع تضارب الأحداث مع الأزرار
                btn_duplicate.bind("<ButtonPress-1>", lambda e: e.widget.focus_set())
                btn_delete.bind("<ButtonPress-1>", lambda e: e.widget.focus_set())
        # --- السحب والإفلات المحسن ---
        drag_data = {"start_idx": None, "dragged": None, "original_y": None, "is_dragging": False, "drag_threshold": 30}
        
        def on_drag_start(event, idx):
            try:
                drag_data["start_idx"] = idx
                drag_data["dragged"] = event.widget
                drag_data["original_y"] = event.y_root
                drag_data["is_dragging"] = False
                # تغيير مظهر العنصر المسحوب
                event.widget.configure(relief="sunken", borderwidth=3)
                # منع انتشار الحدث
                return "break"
            except Exception as e:
                print(f"خطأ في بداية السحب: {e}")
                return "break"
            
        def on_drag_motion(event):
            try:
                if drag_data["dragged"]:
                    # حساب المسافة المقطوعة
                    current_y = event.y_root
                    original_y = drag_data["original_y"]
                    distance = abs(current_y - original_y)
                    
                    # تحديد أن السحب بدأ إذا تجاوز العتبة
                    if distance > drag_data["drag_threshold"] and not drag_data["is_dragging"]:
                        drag_data["is_dragging"] = True
                    
                    # إظهار مؤشر السحب
                    try:
                        drag_data["dragged"].configure(cursor="fleur")
                    except:
                        pass  # تجاهل الخطأ إذا تم حذف العنصر
                    # منع انتشار الحدث
                    return "break"
            except Exception as e:
                print(f"خطأ في حركة السحب: {e}")
                return "break"
                
        def on_drag_release(event, idx):
            try:
                if drag_data["start_idx"] is not None and drag_data["is_dragging"]:
                    # حساب الموقع الجديد بدقة أكبر
                    current_y = event.y_root
                    original_y = drag_data["original_y"]
                    
                    # حساب المسافة المقطوعة
                    distance = current_y - original_y
                    
                    # تحديد الاتجاه بناءً على المسافة
                    if abs(distance) < 30:  # مسافة صغيرة جداً - لا تغيير
                        target_idx = drag_data["start_idx"]
                    elif distance < -30:  # سحب لأعلى
                        target_idx = max(0, drag_data["start_idx"] - 1)
                    else:  # سحب لأسفل
                        target_idx = min(len(page_items) - 1, drag_data["start_idx"] + 1)
                    
                    # إعادة ترتيب العناصر فقط إذا تغير الموقع
                    if target_idx != drag_data["start_idx"]:
                        item = page_items.pop(drag_data["start_idx"])
                        page_items.insert(target_idx, item)
                        # إعادة رسم كامل للعناصر
                        draw_page_items()
                        # رسالة تأكيد
                        print(f"تم نقل العنصر من الموقع {drag_data['start_idx']} إلى الموقع {target_idx}")
                    
                    # إعادة مظهر العنصر (إذا كان لا يزال موجوداً)
                    try:
                        event.widget.configure(relief="ridge", borderwidth=2, cursor="")
                    except:
                        pass  # تجاهل الخطأ إذا تم حذف العنصر
                    
            except Exception as e:
                print(f"خطأ في السحب والإفلات: {e}")
            finally:
                drag_data["start_idx"] = None
                drag_data["dragged"] = None
                drag_data["original_y"] = None
                drag_data["is_dragging"] = False
                # منع انتشار الحدث
                return "break"
            
        def reorder_page_items():
            """إعادة ترتيب العناصر بدون إعادة إنشائها - محسن للسرعة"""
            widgets = scrollable_frame.winfo_children()
            for i, (widget, item) in enumerate(zip(widgets, page_items)):
                # تحديث النص فقط
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):  # text_frame
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ttk.Checkbutton):
                                grandchild.configure(text=f"{item.file_name} - صفحة {item.page_idx+1}")
                                break
                        break
            # تحديث الواجهة فوراً
            scrollable_frame.update_idletasks()
        
        # --- نهاية السحب والإفلات المحسن ---
        draw_page_items()

        def select_all():
            for item in page_items:
                item.var.set(True)
        def deselect_all():
            for item in page_items:
                item.var.set(False)
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=5, side="bottom")
        btn_select_all = tk.Button(btn_frame, text="تحديد الكل", command=select_all)
        btn_select_all.pack(side="left", padx=5)
        btn_deselect_all = tk.Button(btn_frame, text="إلغاء التحديد", command=deselect_all)
        btn_deselect_all.pack(side="left", padx=5)
        def on_merge():
            selected = [(item.file_path, item.page_idx) for item in page_items if item.var.get()]
            if not selected:
                messagebox.showwarning("تنبيه", "يرجى اختيار صفحة واحدة على الأقل!")
                return
            pdfs_with_pages = {}
            for pdf_path, page_num in selected:
                if pdf_path not in pdfs_with_pages:
                    pdfs_with_pages[pdf_path] = []
                pdfs_with_pages[pdf_path].append(page_num)
            
            # استخدام قائمة all_pdf_paths الموجودة
            ordered = []
            for pdf_path in all_pdf_paths:
                if pdf_path in pdfs_with_pages:
                    ordered.append((pdf_path, pdfs_with_pages[pdf_path]))
            
            output_path = filedialog.asksaveasfilename(title="حفظ الملف الناتج", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if not output_path:
                return
            try:
                merge_pdfs(ordered, output_path)
                messagebox.showinfo("نجاح", f"تم إنشاء الملف: {output_path}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("خطأ", str(e))
        btn_merge = tk.Button(btn_frame, text="دمج الصفحات المحددة", font=("Arial", 12), command=on_merge)
        btn_merge.pack(side="left", padx=5)

        def add_more_files():
            new_paths = filedialog.askopenfilenames(title="اختر ملفات PDF لإضافتها", filetypes=[("PDF Files", "*.pdf")])
            if not new_paths:
                return
            
            # إضافة شريط التقدم للملفات الجديدة
            progress_window = tk.Toplevel(win)
            progress_window.title("جاري إضافة الملفات...")
            progress_window.geometry("300x100")
            progress_window.transient(win)
            progress_window.grab_set()
            
            progress_label = tk.Label(progress_window, text="جاري إضافة الملفات...")
            progress_label.pack(pady=10)
            
            progress_bar = ttk.Progressbar(progress_window, mode='determinate')
            progress_bar.pack(pady=10, padx=20, fill='x')
            
            total_files = len(new_paths)
            progress_bar['maximum'] = total_files
            
            for file_idx, pdf_path in enumerate(new_paths):
                try:
                    # تحديث شريط التقدم
                    progress_label.config(text=f"جاري إضافة: {os.path.basename(pdf_path)}")
                    progress_bar['value'] = file_idx + 1
                    progress_window.update()
                    
                    images = convert_pdf_to_images(pdf_path, size=(60, 80))  # تقليل أكثر
                    full_images = None  # تحميل عند الحاجة فقط
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("خطأ في تحويل PDF إلى صور", str(e))
                    continue
                # إضافة الملف الجديد لقائمة all_pdf_paths
                if pdf_path not in all_pdf_paths:
                    all_pdf_paths.append(pdf_path)
                for i, img in enumerate(images):
                    thumb = ImageTk.PhotoImage(img)
                    page_items.append(PageItem(thumb, None, pdf_path, os.path.basename(pdf_path), i))
            
            # إغلاق نافذة التقدم
            progress_window.destroy()
            
            self._thumbnails_refs.append([p.thumb for p in page_items])
            draw_page_items()

        btn_add_files = tk.Button(btn_frame, text="إضافة ملفات PDF أخرى", command=add_more_files)
        btn_add_files.pack(side="left", padx=5)

        # دعم عجلة التمرير (Mouse Wheel)
        def _on_mousewheel(event):
            if event.num == 5 or event.delta == -120:
                canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta == 120:
                canvas.yview_scroll(-1, "units")
        # دعم ويندوز وماك/لينكس
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind_all("<Button-4>", _on_mousewheel)
        scrollable_frame.bind_all("<Button-5>", _on_mousewheel)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolGUI(root)
    root.mainloop() 