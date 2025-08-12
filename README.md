# PDF Processing Tool | برنامج معالجة ملفات PDF

A Python tool for processing PDF files with an easy-to-use graphical interface.

برنامج Python لمعالجة ملفات PDF مع واجهة رسومية سهلة الاستخدام.

---

## Features | المميزات

- **Extract Pages | استخراج صفحات**: Extract specific pages from a PDF file
- **Delete Pages | حذف صفحات**: Delete specific pages from a PDF file
- **Merge Pages | دمج صفحات**: Merge pages from multiple PDF files into one file
- **Page Preview | معاينة الصفحات**: Preview pages before processing
- **Graphical Interface | واجهة رسومية**: Easy-to-use interface in Arabic

---

## Requirements | متطلبات التشغيل

```bash
pip install -r requirements.txt
```

### Required Libraries | المكتبات المطلوبة:
- `pypdf` - For PDF processing | لمعالجة ملفات PDF
- `PyMuPDF` - For PDF to image conversion | لتحويل PDF إلى صور
- `Pillow` - For image processing | لمعالجة الصور

---

## How to Run | كيفية التشغيل

### Graphical Version (Recommended) | النسخة الرسومية (الموصى بها):
```bash
python pdf_tool_gui.py
```

### Text Version | النسخة النصية:
```bash
python pdf_tool.py
```

---

## How to Use | كيفية الاستخدام

### Graphical Version | النسخة الرسومية:
1. Run the program | شغل البرنامج
2. Select a PDF file | اختر ملف PDF
3. Choose the required operation (extract/delete/merge) | اختر العملية المطلوبة (استخراج/حذف/دمج)
4. Select the required pages | حدد الصفحات المطلوبة
5. Choose where to save the new file | اختر مكان حفظ الملف الجديد

### Text Version | النسخة النصية:
1. Run the program | شغل البرنامج
2. Follow the instructions in Terminal | اتبع التعليمات في Terminal
3. Enter file paths and page numbers | أدخل مسارات الملفات وأرقام الصفحات

---

## Creating Executable | إنشاء ملف تنفيذي

To create an executable file using PyInstaller:

لإنشاء ملف تنفيذي باستخدام PyInstaller:

```bash
pyinstaller pdf_tool_gui.spec
```

---

## Included Files | الملفات المرفقة

- `pdf_tool_gui.py` - Main program with graphical interface | البرنامج الرئيسي بواجهة رسومية
- `pdf_tool.py` - Text version of the program | النسخة النصية من البرنامج
- `requirements.txt` - List of required libraries | قائمة المكتبات المطلوبة
- `*.spec` - PyInstaller configuration files | ملفات تكوين PyInstaller

---

## License | الترخيص

This program is free and open source.

هذا البرنامج مجاني ومفتوح المصدر.

---

## Support | الدعم

For help or to report issues, please create an Issue on GitHub.

للمساعدة أو الإبلاغ عن مشاكل، يرجى إنشاء Issue في GitHub.
