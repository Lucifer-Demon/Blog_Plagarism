# Blog Plagiarism Checker

A Django-based web application that helps detect plagiarism in blog posts by comparing them against various sources including uploaded documents and online content.

## Features

- Document upload and text analysis
- Plagiarism detection using Cosine Similarity algorithm
- Support for multiple document formats (PDF, DOCX, plain text)
- Web interface for easy interaction
- Database integration for storing and comparing documents
- Wikipedia integration for source comparison

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual Environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Blog_Plagarism
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate OR .\venv\Scripts\python.exe manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser OR .\venv\Scripts\python.exe manage.py createsuperuser
   ```

## Usage

1. **Start the development server**
   ```bash
   python manage.py runserver OR .\venv\Scripts\python.exe manage.py runserver
   ```

2. **Access the application**
   - Open your web browser and go to `http://127.0.0.1:8000/`
   - Use the web interface to upload documents and check for plagiarism

## Project Structure

- `plagiarismchecker/` - Main Django app containing the core functionality
  - `algorithm/` - Contains the plagiarism detection algorithms
  - `management/` - Custom management commands
  - `migrations/` - Database migrations
- `Plagiarism_Checker/` - Django project settings
- `datasets/` - Sample datasets for testing
- `media/` - User-uploaded files
- `static/` - Static files (CSS, JavaScript, images)

## Configuration

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django Web Framework
- scikit-learn for text processing
- NLTK for natural language processing
- All contributors who helped in the development
