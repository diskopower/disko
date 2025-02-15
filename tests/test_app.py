import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # Теперь импорт должен работать

def test_example():
    """Пример теста."""
    assert 1 + 1 == 2

def test_flask_app():
    """Тест для проверки работы Flask-приложения."""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200