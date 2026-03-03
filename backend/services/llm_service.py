"""
Локальный LLM сервис через Ollama
Использует модель gemma3:1b для анализа табличных данных
"""
import os
import requests
from typing import List


class OllamaService:
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
        self.model = model or os.getenv('OLLAMA_MODEL', 'gemma3:1b')
        self.api_url = f"{self.host}/api/chat"
    
    def analyze_data(self, table_rows: List[str]) -> str:
        """
        Анализирует первые 15 строк таблицы
        
        Args:
            table_rows: список строк таблицы (заголовок + данные)
            
        Returns:
            str: текстовый анализ от LLM
        """
        # Берём первые 15 строк
        sample_data = table_rows[:15] if len(table_rows) > 15 else table_rows
        
        # Системный промпт
        system_prompt = """Ты — аналитик продаж. Анализируй КРАТКО и КОНКРЕТНО.

Формат ответа (СТРОГО):

**Ключевые показатели:**
- Общая выручка: [посчитай сумму всех продаж]
- Средний чек: [общая выручка / количество строк]

**ТОП-3 товара:**
1. [Название] - [сумма] руб
2. [Название] - [сумма] руб  
3. [Название] - [сумма] руб

**Худшие продажи:**
1. [Название] - [сумма] руб
2. [Название] - [сумма] руб

**Рекомендации:**
- [1 конкретная рекомендация]
- [1 конкретная рекомендация]

ВАЖНО: Используй ТОЛЬКО реальные названия товаров из таблицы. Не выдумывай данные."""
        
        # Формируем данные для анализа
        user_content = f"Проанализируй следующие данные:\n\n{chr(10).join(sample_data)}"
        
        # Формируем запрос к Ollama
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 400,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=180  # 3 минуты
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Извлекаем ответ из структуры Ollama
            if "message" in result and "content" in result["message"]:
                return result["message"]["content"]
            else:
                return "Ошибка: неожиданный формат ответа от Ollama"
                
        except requests.exceptions.ConnectionError:
            return "❌ Ошибка: Не удалось подключиться к Ollama. Убедитесь, что сервис запущен."
        except requests.exceptions.Timeout:
            return "❌ Ошибка: Превышено время ожидания ответа от Ollama (3 минуты)."
        except requests.exceptions.HTTPError as e:
            return f"❌ Ошибка HTTP: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"❌ Ошибка при запросе к Ollama: {str(e)}"


# Глобальный экземпляр сервиса
ollama_service = OllamaService()


def get_llm_analysis(table_data: List[str]) -> str:
    """
    Публичная функция для получения анализа от LLM
    
    Args:
        table_data: список строк таблицы
        
    Returns:
        str: текстовый анализ
    """
    return ollama_service.analyze_data(table_data)
