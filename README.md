# 🎓 KIUT Student Information Bot

A modern Telegram bot for Kimyo International University in Tashkent, Branch Namangan that generates student information certificates in PDF format.

## 📋 Features

* **Student Information Lookup** : Students can request their information certificate by providing their passport ID or JSHSHIR
* **PDF Generation** : Automatically generates professional PDF certificates with university branding
* **Admin Panel** : Administrators can add, view, and manage student records
* **Multi-language Support** : Interface supports Uzbek language with emoji-enhanced readability
* **Secure Authentication** : Admin access is protected by user ID verification

## 🚀 Getting Started

### Prerequisites

* Python 3.7+
* Telegram Bot Token (from [@BotFather](command:_cody.vscode.open?%22https%3A%2F%2Ft.me%2FBotFather%22))
* Required fonts (DejaVuSans)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/kiut-student-bot.git
cd kiut-student-bot
```

Copy

Execute

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Copy

Execute

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Copy

Execute

4. Download required fonts:
   * Download [DejaVuSans.ttf](command:_cody.vscode.open?%22https%3A%2F%2Fdejavu-fonts.github.io%2F%22) and [DejaVuSans-Bold.ttf](command:_cody.vscode.open?%22https%3A%2F%2Fdejavu-fonts.github.io%2F%22)
   * Place them in the `fonts` directory
5. Add your university logo:
   * Place your logo image in the `images` directory as `kiut_logo.jpg`
6. Configure environment variables:
   * Create a `.env` file in the project root
   * Add your bot token and admin IDs:

     ```ini
     BOT_TOKEN="your_bot_token_here"
     ADMIN_IDS="admin_telegram_id_1,admin_telegram_id_2"
     ```

     Copy

     Apply

### Running the Bot

Start the bot with:

```bash
python -m bot.main
```

Copy

Execute

## 📱 Usage

### For Students

1. Start a chat with the bot
2. Select your course (1-4)
3. Enter your passport ID or JSHSHIR
4. Receive your information certificate as a PDF document

### For Administrators

1. Start a chat with the bot
2. Access the admin panel
3. Add new student records
4. View the list of registered students

## 🏗️ Project Structure

```bash
kiut-student-bot/
├── bot/
│   ├── __init__.py
│   ├── config.py        # Configuration and environment variables
│   ├── database.py      # SQLite database operations
│   ├── handlers.py      # Telegram bot message handlers
│   ├── main.py          # Entry point for the application
│   └── pdf_generator.py # PDF certificate generation
├── data/                # Generated PDF certificates
├── database/            # SQLite database files
├── fonts/               # Required font files
├── images/              # University logo and images
├── .env                 # Environment variables (not in git)
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

Copy

Execute

## 🔧 Customization

### Modifying PDF Template

Edit the `pdf_generator.py` file to customize the appearance of the PDF certificates.

### Adding New Fields

To add new student information fields:

1. Update the database schema in `database.py`
2. Modify the admin form in `handlers.py`
3. Update the PDF generation in `pdf_generator.py`

## 🔒 Security Considerations

* The bot uses Telegram user IDs for admin authentication
* Student personal data is stored locally in an SQLite database
* PDF files are generated with unique names based on passport IDs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- [Xamidullayev I.](https://github.com/islombek4642) - Initial work
- Telegram: [@xamidullayev_i](https://t.me/xamidullayev_i)
```

You should also update the repository URL in the installation instructions:

```bash
git clone https://github.com/islombek4642/kiut-student-bot.git
cd kiut-student-bot


## 🙏 Acknowledgments

* [Aiogram](command:_cody.vscode.open?%22https%3A%2F%2Fgithub.com%2Faiogram%2Faiogram%22) - Telegram Bot framework
* [ReportLab](command:_cody.vscode.open?%22https%3A%2F%2Fwww.reportlab.com%2F%22) - PDF generation library
* Kimyo International University in Tashkent, Branch Namangan

Made with ❤️ for KIUT students
