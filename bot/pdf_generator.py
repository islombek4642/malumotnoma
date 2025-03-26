from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import os

# Papkalarni yaratish
if not os.path.exists("data"):
    os.makedirs("data")

# Fonts papkasini yaratish
if not os.path.exists("fonts"):
    os.makedirs("fonts")

# Images papkasini yaratish
if not os.path.exists("images"):
    os.makedirs("images")

# Agar fonts papkasida DejaVuSans.ttf mavjud bo'lmasa, uni o'rnatish haqida xabar berish
FONT_PATH = "fonts/DejaVuSans.ttf"
FONT_BOLD_PATH = "fonts/DejaVuSans-Bold.ttf"

# Shriftlarni tekshirish va ro'yxatdan o'tkazish
fonts_available = True

if not os.path.exists(FONT_PATH):
    print(f"OGOHLANTIRISH: {FONT_PATH} shrifti topilmadi.")
    fonts_available = False

if not os.path.exists(FONT_BOLD_PATH):
    print(f"OGOHLANTIRISH: {FONT_BOLD_PATH} shrifti topilmadi.")
    fonts_available = False

if fonts_available:
    # Shriftlarni ro'yxatdan o'tkazish
    pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', FONT_BOLD_PATH))

def generate_pdf(student):
    try:
        # Fayl nomini yaratish uchun pasport ID dan foydalanish
        file_path = os.path.join("data", f"{student[8]}_malumotnoma.pdf")
        c = canvas.Canvas(file_path, pagesize=A4)

        # A4 sahifasining o'lchamlari
        page_width, page_height = A4

        # Logo fayl yo'li
        logo_path = "images/kiut_logo.jpg"

        # 640x640 rasmni A4 sahifasiga moslashtirish
        if os.path.exists(logo_path):
            # A4 sahifasining kengligi 595 piksel atrofida, shuning uchun
            # rasmni kichikroq qilish kerak
            scale_factor = 0.25  # Rasmni 25% ga kichiklashtirish
            logo_width = 640 * scale_factor
            logo_height = 640 * scale_factor

            # Rasmni sahifaning yuqori qismiga, markazga joylashtirish
            logo_x = (page_width - logo_width) / 2
            logo_y = page_height - logo_height - 30  # Yuqoridan 30 piksel pastda

            # Logoni chizish
            c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)

            # Universitet nomini logoning pastiga joylashtirish
            univ_y = logo_y - 30
        else:
            # Logo mavjud bo'lmasa, universitet nomini yuqorida qoldirish
            univ_y = page_height - 100

        # Universitet nomini yozish
        if fonts_available:
            c.setFont("DejaVuSans-Bold", 14)
        else:
            c.setFont("Helvetica-Bold", 14)

        # Universitet nomini markazga joylashtirish
        univ_text = "KIMYO INTERNATIONAL UNIVERSITY IN TASHKENT BRANCH NAMANGAN"
        univ_width = c.stringWidth(univ_text, "DejaVuSans-Bold" if fonts_available else "Helvetica-Bold", 14)
        univ_x = (page_width - univ_width) / 2
        c.drawString(univ_x, univ_y, univ_text)

        # Sarlavhani universitet nomining pastiga joylashtirish
        title_y = univ_y - 40

        # Agar DejaVuSans mavjud bo'lsa, undan foydalanish, aks holda Helvetica
        if fonts_available:
            c.setFont("DejaVuSans-Bold", 16)
        else:
            c.setFont("Helvetica-Bold", 16)

        # Sarlavhani markazga joylashtirish
        title_text = "📌 TALABA MA'LUMOTNOMASI"
        title_width = c.stringWidth(title_text, "DejaVuSans-Bold" if fonts_available else "Helvetica-Bold", 16)
        title_x = (page_width - title_width) / 2
        c.drawString(title_x, title_y, title_text)

        # Ma'lumotlar joylashuvini logo mavjudligiga qarab sozlash
        start_y = title_y - 40

        if fonts_available:
            c.setFont("DejaVuSans", 12)
        else:
            c.setFont("Helvetica", 12)

        # Ma'lumotlarni chizish
        line_height = 20  # Qatorlar orasidagi masofa

        c.drawString(100, start_y, f"🏫 Oliy ta'lim muassasasi: {student[1]}")
        c.drawString(100, start_y - line_height, f"📌 Fakultet: {student[2]}")
        c.drawString(100, start_y - line_height * 2, f"📌 Yo'nalish: {student[3]}")
        c.drawString(100, start_y - line_height * 3, f"📌 Kurs: {student[4]} - kurs")
        c.drawString(100, start_y - line_height * 4, f"📌 Guruh: {student[5]}")
        c.drawString(100, start_y - line_height * 5, f"👤 F.I.O: {student[6]}")
        c.drawString(100, start_y - line_height * 6, f"📅 Tug'ilgan sana: {student[7]}")
        c.drawString(100, start_y - line_height * 7, f"🆔 Pasport ID: {student[8]}")
        c.drawString(100, start_y - line_height * 8, f"📜 JSHSHIR: {student[9]}")
        c.drawString(100, start_y - line_height * 9, f"📌 Talabalik holati: {student[10]}")
        c.drawString(100, start_y - line_height * 10, f"📌 O'qish turi: {student[11]}")
        c.drawString(100, start_y - line_height * 11, f"📌 O'qish shakli: {student[12]}")
        c.drawString(100, start_y - line_height * 12, f"📞 Telefon: {student[13]}")
        c.drawString(100, start_y - line_height * 13, f"📅 Berilgan sana: {student[14]}")
        c.drawString(100, start_y - line_height * 14, f"📅 Amal qilish muddati: {student[15]}")

        # Imzo
        c.drawString(100, start_y - line_height * 16, "✍ Mas'ul shaxs imzosi va muhri: ___________")

        c.save()
        return file_path
    except Exception as e:
        print(f"PDF yaratishda xatolik: {e}")
        return None
