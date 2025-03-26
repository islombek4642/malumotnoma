from aiogram import Router, Bot, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from bot.database import get_student_by_id, add_student, get_all_students
from bot.pdf_generator import generate_pdf
from bot.config import ADMIN_IDS
import re
import os
from datetime import datetime
from bot.database import get_student_by_id, add_student, get_all_students, import_students_from_excel, create_sample_excel
from bot.database import get_student_by_id, add_student, get_all_students, import_students_from_excel, create_sample_excel, delete_student_by_id, delete_all_students

router = Router()

# Holatlar uchun StatesGroup
class Form(StatesGroup):
    select_course = State()  # Kursni tanlash holati
    enter_passport = State()  # Pasport ID yoki JSHSHIR kiritish holati

# Admin uchun holatlar
class AdminForm(StatesGroup):
    waiting_for_command = State()
    add_student = State()
    university = State()
    faculty = State()
    direction = State()
    course = State()
    group_number = State()
    full_name = State()
    birth_date = State()
    passport_id = State()
    jshshir = State()
    status = State()
    education_type = State()
    education_form = State()
    phone = State()
    issued_date = State()
    valid_until = State()
    waiting_for_excel = State()
    confirm_delete_all = State()
    delete_student = State()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    # Admin uchun maxsus xabar
    if message.from_user.id in ADMIN_IDS:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📚 Kursni tanlash")],
                [KeyboardButton(text="👨‍💼 Admin panel")]
            ],
            resize_keyboard=True
        )
        await message.answer("Salom, admin! Quyidagi menyudan tanlang:", reply_markup=keyboard)
        await state.set_state(Form.select_course)
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="1-kurs"), KeyboardButton(text="2-kurs")],
                      [KeyboardButton(text="3-kurs"), KeyboardButton(text="4-kurs")]],
            resize_keyboard=True
        )
        await message.answer("📚 Kursni tanlang:", reply_markup=keyboard)
        await state.set_state(Form.select_course)

@router.message(Command("cancel"))
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi. Qayta boshlash uchun /start buyrug'ini yuboring.",
                        reply_markup=ReplyKeyboardRemove())

@router.message(Form.select_course, F.text == "📚 Kursni tanlash")
async def select_course_handler(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="1-kurs"), KeyboardButton(text="2-kurs")],
                  [KeyboardButton(text="3-kurs"), KeyboardButton(text="4-kurs")]],
        resize_keyboard=True
    )
    await message.answer("📚 Kursni tanlang:", reply_markup=keyboard)
    await state.set_state(Form.select_course)

@router.message(Form.select_course, F.text == "👨‍💼 Admin panel")
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⚠️ Sizda admin huquqlari yo'q!")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="📊 Excel import")],
            [KeyboardButton(text="📝 Namuna fayl")],
            [KeyboardButton(text="🗑 Talabani o'chirish")],
            [KeyboardButton(text="🗑 Barcha talabalarni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)
    await state.set_state(AdminForm.waiting_for_command)

@router.message(Form.select_course)
async def course_handler(message: types.Message, state: FSMContext):
    # Kursni tanlagandan keyin pasport ID yoki JSHSHIR so'rash
    if message.text in ["1-kurs", "2-kurs", "3-kurs", "4-kurs"]:
        # Tanlangan kursni saqlash
        course = int(message.text.split("-")[0])  # "1-kurs" dan 1 ni olish
        await state.update_data(selected_course=course)

        # Klaviaturani olib tashlash
        await message.answer("🔑 Pasport ID yoki JSHSHIR ni kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.enter_passport)  # Pasport ID kiritish holatiga o'tish
    elif message.from_user.id in ADMIN_IDS and message.text == "👨‍💼 Admin panel":
        # Admin panel uchun
        await admin_panel(message, state)
    else:
        await message.answer("⚠️ Iltimos, tugmalardan birini tanlang!")

@router.message(Form.enter_passport)
async def passport_handler(message: types.Message, state: FSMContext):
    # Pasport ID yoki JSHSHIR validatsiyasi
    input_text = message.text.strip()

    # Pasport ID formati: AA1234567 yoki JSHSHIR formati: 12345678901234
    passport_pattern = r'^[A-Z]{2}\d{7}$'
    jshshir_pattern = r'^\d{14}$'

    if not (re.match(passport_pattern, input_text) or re.match(jshshir_pattern, input_text)):
        await message.answer("⚠️ Noto'g'ri format! Pasport ID (AA1234567) yoki JSHSHIR (14 ta raqam) kiriting.")
        return

    try:
        # Tanlangan kursni olish
        user_data = await state.get_data()
        selected_course = user_data.get("selected_course")

        # Foydalanuvchi kiritgan pasport ID yoki JSHSHIR va kurs bo'yicha ma'lumotni qidirish
        from database import get_student_by_id_and_course

        student = get_student_by_id_and_course(input_text, selected_course)

        if student:
            pdf_path = generate_pdf(student)
            if pdf_path:
                await message.answer_document(document=types.FSInputFile(pdf_path), caption="📄 Ma'lumotnoma yuklandi.")
                await state.clear()  # Holatni tozalash
                # Bosh menyuga qaytish
                await start_handler(message, state)
            else:
                await message.answer("⚠️ PDF yaratishda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")
                # Bosh menyuga qaytish
                await state.clear()
                await start_handler(message, state)
        else:
            await message.answer(f"⚠️ {selected_course}-kursda bunday pasport ID yoki JSHSHIR topilmadi!")
            # Bosh menyuga qaytish
            await state.clear()
            await start_handler(message, state)
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {str(e)}")
        await state.clear()
        await start_handler(message, state)
# Admin panel uchun funksiyalar
@router.message(AdminForm.waiting_for_command, F.text == "➕ Talaba qo'shish")
async def add_student_start(message: types.Message, state: FSMContext):
    await message.answer("🏫 Oliy ta'lim muassasasi nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminForm.university)

@router.message(AdminForm.waiting_for_command, F.text == "📋 Talabalar ro'yxati")
async def list_students(message: types.Message, state: FSMContext):
    students = get_all_students()
    if not students:
        await message.answer("⚠️ Ma'lumotlar bazasida talabalar yo'q!")
        return

    text = "📋 Talabalar ro'yxati:\n\n"
    for student in students[:20]:  # Faqat 20 ta talabani ko'rsatish
        text += f"ID: {student[0]}, F.I.O: {student[6]}, Pasport: {student[8]}\n"

    if len(students) > 20:
        text += f"\nJami {len(students)} ta talaba mavjud. Faqat dastlabki 20 tasi ko'rsatildi."

    await message.answer(text)

@router.message(AdminForm.waiting_for_command, F.text == "🔙 Orqaga")
async def back_to_main(message: types.Message, state: FSMContext):
    await start_handler(message, state)

@router.message(AdminForm.university)
async def process_university(message: types.Message, state: FSMContext):
    await state.update_data(university=message.text)
    await message.answer("📌 Fakultet nomini kiriting:")
    await state.set_state(AdminForm.faculty)

@router.message(AdminForm.faculty)
async def process_faculty(message: types.Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await message.answer("📌 Yo'nalish nomini kiriting:")
    await state.set_state(AdminForm.direction)

@router.message(AdminForm.direction)
async def process_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await message.answer("📌 Kursni kiriting (1-4):")
    await state.set_state(AdminForm.course)

@router.message(AdminForm.course)
async def process_course(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 1 or int(message.text) > 4:
        await message.answer("⚠️ Iltimos, 1 dan 4 gacha bo'lgan raqamni kiriting!")
        return

    await state.update_data(course=int(message.text))
    await message.answer("📌 Guruh raqamini kiriting:")
    await state.set_state(AdminForm.group_number)

@router.message(AdminForm.group_number)
async def process_group(message: types.Message, state: FSMContext):
    await state.update_data(group_number=message.text)
    await message.answer("👤 Talabaning F.I.O.sini kiriting:")
    await state.set_state(AdminForm.full_name)

@router.message(AdminForm.full_name)
async def process_fullname(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("📅 Tug'ilgan sanani kiriting (DD.MM.YYYY):")
    await state.set_state(AdminForm.birth_date)

@router.message(AdminForm.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    # Sana validatsiyasi
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! Sanani DD.MM.YYYY formatida kiriting (masalan, 01.01.2000)")
        return

    await state.update_data(birth_date=message.text)
    await message.answer("🆔 Pasport ID ni kiriting (AA1234567):")
    await state.set_state(AdminForm.passport_id)

@router.message(AdminForm.passport_id)
async def process_passport_id(message: types.Message, state: FSMContext):
    # Pasport ID validatsiyasi
    passport_pattern = r'^[A-Z]{2}\d{7}$'
    if not re.match(passport_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! Pasport ID ni AA1234567 formatida kiriting")
        return

    # Pasport ID mavjudligini tekshirish
    if get_student_by_id(message.text):
        await message.answer("⚠️ Bu pasport ID bilan talaba allaqachon mavjud!")
        return

    await state.update_data(passport_id=message.text)
    await message.answer("📜 JSHSHIR ni kiriting (14 ta raqam):")
    await state.set_state(AdminForm.jshshir)

@router.message(AdminForm.jshshir)
async def process_jshshir(message: types.Message, state: FSMContext):
    # JSHSHIR validatsiyasi
    jshshir_pattern = r'^\d{14}$'
    if not re.match(jshshir_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! JSHSHIR 14 ta raqamdan iborat bo'lishi kerak")
        return

    # JSHSHIR mavjudligini tekshirish
    if get_student_by_id(message.text):
        await message.answer("⚠️ Bu JSHSHIR bilan talaba allaqachon mavjud!")
        return

    await state.update_data(jshshir=message.text)
    await message.answer("📌 Talabalik holatini kiriting (aktiv/o'qishdan chetlashtirilgan/akademik ta'til):")
    await state.set_state(AdminForm.status)

@router.message(AdminForm.status)
async def process_status(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer("📌 O'qish turini kiriting (davlat granti/to'lov-kontrakt):")
    await state.set_state(AdminForm.education_type)

@router.message(AdminForm.status)
async def process_status(message: types.Message, state: FSMContext):
    await state.update_data(status=message.text)
    await message.answer("📌 O'qish turini kiriting (davlat granti/to'lov-kontrakt):")
    await state.set_state(AdminForm.education_type)

@router.message(AdminForm.education_type)
async def process_education_type(message: types.Message, state: FSMContext):
    await state.update_data(education_type=message.text)
    await message.answer("📌 O'qish shaklini kiriting (kunduzgi/sirtqi/kechki):")
    await state.set_state(AdminForm.education_form)

@router.message(AdminForm.education_form)
async def process_education_form(message: types.Message, state: FSMContext):
    await state.update_data(education_form=message.text)
    await message.answer("📞 Telefon raqamini kiriting (+998XXXXXXXXX):")
    await state.set_state(AdminForm.phone)

@router.message(AdminForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    # Telefon raqami validatsiyasi
    phone_pattern = r'^\+998\d{9}$'
    if not re.match(phone_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! Telefon raqamini +998XXXXXXXXX formatida kiriting")
        return

    await state.update_data(phone=message.text)
    await message.answer("📅 Ma'lumotnoma berilgan sanani kiriting (DD.MM.YYYY):")
    await state.set_state(AdminForm.issued_date)

@router.message(AdminForm.issued_date)
async def process_issued_date(message: types.Message, state: FSMContext):
    # Sana validatsiyasi
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! Sanani DD.MM.YYYY formatida kiriting (masalan, 01.01.2023)")
        return

    await state.update_data(issued_date=message.text)
    await message.answer("📅 Ma'lumotnoma amal qilish muddatini kiriting (DD.MM.YYYY):")
    await state.set_state(AdminForm.valid_until)

@router.message(AdminForm.valid_until)
async def process_valid_until(message: types.Message, state: FSMContext):
    # Sana validatsiyasi
    date_pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(date_pattern, message.text):
        await message.answer("⚠️ Noto'g'ri format! Sanani DD.MM.YYYY formatida kiriting (masalan, 01.01.2024)")
        return

    await state.update_data(valid_until=message.text)

    # Barcha ma'lumotlarni olish
    data = await state.get_data()

    try:
        # Ma'lumotlar bazasiga qo'shish
        result = add_student(
            data['university'], data['faculty'], data['direction'], data['course'],
            data['group_number'], data['full_name'], data['birth_date'], data['passport_id'],
            data['jshshir'], data['status'], data['education_type'], data['education_form'],
            data['phone'], data['issued_date'], data['valid_until']
        )

        if result:
            await message.answer("✅ Talaba ma'lumotlari muvaffaqiyatli qo'shildi!")
        else:
            await message.answer("⚠️ Ma'lumotlarni qo'shishda xatolik yuz berdi.")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {str(e)}")

    # Admin panelga qaytish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)
    await state.set_state(AdminForm.waiting_for_command)

@router.message(AdminForm.waiting_for_command, F.text == "📊 Excel import")
async def excel_import_command(message: types.Message, state: FSMContext):
    await message.answer("Excel faylni yuklang. Fayl quyidagi ustunlarni o'z ichiga olishi kerak:\n\n"
                        "university, faculty, direction, course, group_number, full_name, "
                        "birth_date, passport_id, jshshir, status, education_type, "
                        "education_form, phone, issued_date, valid_until")
    await state.set_state(AdminForm.waiting_for_excel)

@router.message(AdminForm.waiting_for_excel, F.document)
async def process_excel_import(message: types.Message, state: FSMContext):
    try:
        # Faylni yuklab olish
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = f"temp_{message.document.file_name}"
        await message.bot.download_file(file.file_path, file_path)

        # Excel faylni import qilish
        success_count, error_count, error_details = import_students_from_excel(file_path)

        # Vaqtinchalik faylni o'chirish
        os.remove(file_path)

        # Natijalarni ko'rsatish
        result_text = "Import natijasi:\n\n"
        result_text += f"✅ {success_count} ta talaba muvaffaqiyatli qo'shildi\n\n"
        result_text += f"❌ {error_count} ta qatorda xatolik"

        # Agar xatoliklar haqida batafsil ma'lumot bo'lsa, qo'shish
        if error_details:
            result_text += f"\n\nXatoliklar tavsifi:{error_details}"

        await message.answer(result_text)
    except Exception as e:
        await message.answer(f"⚠️ Faylni import qilishda xatolik: {str(e)}")

    # Admin panelga qaytish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="📊 Excel import")],
            [KeyboardButton(text="📝 Namuna fayl")],
            [KeyboardButton(text="🗑 Talabani o'chirish")],
            [KeyboardButton(text="🗑 Barcha talabalarni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)

    await state.set_state(AdminForm.waiting_for_command)
@router.message(AdminForm.waiting_for_command, F.text == "📝 Namuna fayl")
async def sample_file_command(message: types.Message, state: FSMContext):
    # Namuna Excel fayl yaratish
    file_path = create_sample_excel()

    if file_path:
        await message.answer_document(document=types.FSInputFile(file_path), caption="📝 Namuna Excel fayl")
        # Faylni o'chirish
        os.remove(file_path)
    else:
        await message.answer("⚠️ Namuna fayl yaratishda xatolik yuz berdi")

@router.message(AdminForm.waiting_for_command, F.text == "🗑 Talabani o'chirish")
async def delete_student_command(message: types.Message, state: FSMContext):
    await message.answer("O'chirmoqchi bo'lgan talabaning pasport ID sini kiriting (masalan, AA1234567):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminForm.delete_student)

@router.message(AdminForm.delete_student)
async def process_delete_student(message: types.Message, state: FSMContext):
    passport_id = message.text.strip()

    # Pasport ID formatini tekshirish
    passport_pattern = r'^[A-Z]{2}\d{7}$'

    if not re.match(passport_pattern, passport_id):
        await message.answer("⚠️ Noto'g'ri format! Pasport ID ni AA1234567 formatida kiriting")
        return

    # Talabani pasport ID bo'yicha o'chirish
    from database import delete_student_by_passport
    result = delete_student_by_passport(passport_id)

    if result:
        student_id, student_name = result
        await message.answer(f"✅ {student_name} (ID: {student_id}, Pasport: {passport_id}) muvaffaqiyatli o'chirildi!")
    else:
        await message.answer(f"⚠️ {passport_id} pasport ID li talaba topilmadi.")

    # Admin panelga qaytish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="📊 Excel import")],
            [KeyboardButton(text="📝 Namuna fayl")],
            [KeyboardButton(text="🗑 Talabani o'chirish")],
            [KeyboardButton(text="🗑 Barcha talabalarni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)
    await state.set_state(AdminForm.waiting_for_command)
@router.message(AdminForm.waiting_for_command, F.text == "🗑 Barcha talabalarni o'chirish")
async def delete_all_students_command(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha, barcha talabalarni o'chirish")],
            [KeyboardButton(text="❌ Yo'q, bekor qilish")]
        ],
        resize_keyboard=True
    )
    await message.answer("⚠️ DIQQAT! Barcha talabalar ma'lumotlari o'chiriladi. Bu amalni qaytarib bo'lmaydi. Davom etishni xohlaysizmi?", reply_markup=keyboard)
    await state.set_state(AdminForm.confirm_delete_all)

@router.message(AdminForm.confirm_delete_all, F.text == "✅ Ha, barcha talabalarni o'chirish")
async def confirm_delete_all(message: types.Message, state: FSMContext):
    deleted_count = delete_all_students()
    await message.answer(f"✅ Jami {deleted_count} ta talaba ma'lumotlari o'chirildi.")

    # Admin panelga qaytish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="📊 Excel import")],
            [KeyboardButton(text="📝 Namuna fayl")],
            [KeyboardButton(text="🗑 Talabani o'chirish")],
            [KeyboardButton(text="🗑 Barcha talabalarni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)
    await state.set_state(AdminForm.waiting_for_command)

@router.message(AdminForm.confirm_delete_all, F.text == "❌ Yo'q, bekor qilish")
async def cancel_delete_all(message: types.Message, state: FSMContext):
    await message.answer("✅ O'chirish bekor qilindi.")

    # Admin panelga qaytish
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Talaba qo'shish")],
            [KeyboardButton(text="📋 Talabalar ro'yxati")],
            [KeyboardButton(text="📊 Excel import")],
            [KeyboardButton(text="📝 Namuna fayl")],
            [KeyboardButton(text="🗑 Talabani o'chirish")],
            [KeyboardButton(text="🗑 Barcha talabalarni o'chirish")],
            [KeyboardButton(text="🔙 Orqaga")]
        ],
        resize_keyboard=True
    )
    await message.answer("👨‍💼 Admin panel:", reply_markup=keyboard)
    await state.set_state(AdminForm.waiting_for_command)
