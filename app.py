import os
import csv
from flask import Flask, render_template, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from services.llm_service import get_llm_analysis

# Опциональный импорт pdfplumber (только если нужна поддержка PDF)
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv'} | ({'pdf'} if PDF_SUPPORT else set())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_filepath(filepath):
    """Проверяет, что filepath находится в папке uploads и безопасен."""
    if not filepath:
        return False
    # Нормализуем путь и проверяем, что он внутри UPLOAD_FOLDER
    abs_upload = os.path.abspath(app.config['UPLOAD_FOLDER'])
    abs_filepath = os.path.abspath(filepath)
    return abs_filepath.startswith(abs_upload)

def read_data_file(filepath):
    """Читает CSV, Excel или PDF файл и возвращает Pandas DataFrame."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл не найден: {filepath}")

    if '.' not in filepath:
        raise ValueError(f"Файл не имеет расширения: {filepath}")
    file_extension = filepath.lower().rsplit('.', 1)[1]

    if file_extension == 'csv':
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(f.read(1024))
                f.seek(0)
                return pd.read_csv(filepath, sep=dialect.delimiter, encoding='utf-8')
        except csv.Error:
            # Попытка с разделителем по умолчанию, если сниффер не справился
            return pd.read_csv(filepath, sep=',', encoding='utf-8')
    elif file_extension == 'pdf':
        if not PDF_SUPPORT:
            raise ValueError('Поддержка PDF недоступна. Установите библиотеку: pip install pdfplumber')
        try:
            with pdfplumber.open(filepath) as pdf:
                if not pdf.pages:
                    raise ValueError('PDF-файл не содержит страниц.')
                
                first_page = pdf.pages[0]
                tables = first_page.extract_tables()
                
                if not tables:
                    raise ValueError('В PDF-файле не найдено таблиц на первой странице.')
                
                table_data = tables[0]
                
                if not table_data or len(table_data) < 2:
                    raise ValueError('В PDF-файле недостаточно данных: нужны заголовок и хотя бы одна строка данных.')
                
                # Первая строка считается заголовком
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                return df
        except (ValueError, KeyError, IndexError, AttributeError) as e:
            raise ValueError(f"Ошибка при чтении PDF-файла: {e}")
    elif file_extension in ['xls', 'xlsx']:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Неподдерживаемый тип файла: {file_extension}")


def convert_dataframe_columns(df):
    """Преобразует колонки DataFrame: даты в datetime, колонки 'год'/'year' в числовые."""
    for col in df.columns:
        col_lower = str(col).lower() if col else ''
        
        # Обрабатываем колонки 'год'/'year'
        if col_lower in ('year', 'год'):
            try:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.year
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except (ValueError, TypeError):
                pass
            continue
        
        # Конвертируем в дату ТОЛЬКО если название колонки явно указывает на дату
        date_keywords = ['дата', 'date', 'время', 'time', 'день', 'day', 'месяц', 'month']
        if any(keyword in col_lower for keyword in date_keywords):
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except (ValueError, TypeError):
                    pass
    return df

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = read_data_file(filepath)
            df = convert_dataframe_columns(df)
        except (FileNotFoundError, ValueError) as e:
            print(f"[ERROR upload_file] Error reading file {filepath}: {e}")
            return jsonify({'error': str(e)}), 400
            
        # Basic Analytics
        analytics = {}
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                analytics[col] = {'Сумма': float(df[col].sum()), 'Уникальных значений': int(df[col].nunique())}
            else:
                analytics[col] = {'Уникальных значений': int(df[col].nunique())}

        # Columns that can be used as "year" for line chart (numeric, year-like)
        def is_year_column(col):
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False
            if col and str(col).lower() in ('year', 'год'):
                return True
            try:
                s = df[col].dropna()
                if len(s) == 0:
                    return False
                min_val, max_val = s.min(), s.max()
                return 1900 <= min_val <= 2100 and 1900 <= max_val <= 2100
            except (TypeError, ValueError):
                return False

        year_cols = [col for col in df.columns if is_year_column(col)]
        # Get column types for chart selection
        column_types = {
            'numerical': [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])],
            'categorical': [col for col in df.columns if df[col].nunique() < 50 and not pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_datetime64_any_dtype(df[col])],
            'date': [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])],
            'year': year_cols
        }

        return jsonify({
            'table_html': df.head(100).to_html(classes='table table-striped', index=False),
            'analytics': analytics,
            'column_types': column_types,
            'filepath': filepath
        })
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/generate_chart', methods=['POST'])
def generate_chart():
    data = request.get_json()
    filepath = data.get('filepath')
    chart_type = data.get('chart_type')
    x_col = data.get('x_col')
    y_col = data.get('y_col')

    if not all([filepath, chart_type, x_col, y_col]):
        return jsonify({'error': 'Missing parameters for chart generation'}), 400

    if not is_safe_filepath(filepath):
        return jsonify({'error': 'Invalid file path'}), 400
        
    try:
        df = read_data_file(filepath)
        df = convert_dataframe_columns(df)

        chart_data = {}
        if chart_type == 'bar':
            # Ensure x is categorical and y is numerical
            if not pd.api.types.is_numeric_dtype(df[y_col]):
                 return jsonify({'error': f'Для гистограммы ось Y ({y_col}) должна быть числовой.'}), 400
            
            chart_df = df.groupby(x_col)[y_col].sum().reset_index()
            chart_data = {
                'labels': chart_df[x_col].tolist(),
                'data': chart_df[y_col].tolist(),
                'label': f'Сумма {y_col} по {x_col}'
                }

        elif chart_type == 'line':
            # Ensure y is numerical
            if not pd.api.types.is_numeric_dtype(df[y_col]):
                return jsonify({'error': f'Для линейного графика ось Y ({y_col}) должна быть числовой.'}), 400

            # X-axis: date or numeric year column
            if pd.api.types.is_numeric_dtype(df[x_col]):
                # Числовая колонка «год» — используем временную колонку с датой, чтобы не затереть year при X=Y=year
                df = df.dropna(subset=[x_col, y_col]).copy()
                x_date_col = '_x_date_'
                df[x_date_col] = pd.to_datetime(df[x_col].astype(int).astype(str) + '-01-01', errors='coerce')
                df = df.dropna(subset=[x_date_col])
                if df.empty:
                    return jsonify({'error': 'Недостаточно данных для построения линейного графика.'}), 400
                df = df.sort_values(by=x_date_col)
                try:
                    line_chart_df = df.groupby(pd.Grouper(key=x_date_col, freq='YE'))[y_col].sum().reset_index()
                except ValueError:
                    line_chart_df = df.groupby(pd.Grouper(key=x_date_col, freq='Y'))[y_col].sum().reset_index()
                labels = line_chart_df[x_date_col].dt.strftime('%Y').tolist()
            else:
                # Ось X — дата
                if not pd.api.types.is_datetime64_any_dtype(df[x_col]):
                    try:
                        df[x_col] = pd.to_datetime(df[x_col], errors='coerce')
                    except (ValueError, TypeError):
                        return jsonify({'error': f'Не удалось преобразовать ось X ({x_col}) в дату.'}), 400
                if not pd.api.types.is_datetime64_any_dtype(df[x_col]):
                    return jsonify({'error': f'Для линейного графика ось X ({x_col}) должна быть датой или годом.'}), 400
                df = df.dropna(subset=[x_col, y_col])
                if df.empty:
                    return jsonify({'error': 'Недостаточно данных для построения линейного графика.'}), 400
                df = df.sort_values(by=x_col)
                try:
                    line_chart_df = df.groupby(pd.Grouper(key=x_col, freq='ME'))[y_col].sum().reset_index()
                except ValueError:
                    try:
                        line_chart_df = df.groupby(pd.Grouper(key=x_col, freq='M'))[y_col].sum().reset_index()
                    except Exception:
                        df['year_month'] = df[x_col].dt.to_period('M')
                        line_chart_df = df.groupby('year_month')[y_col].sum().reset_index()
                        line_chart_df[x_col] = line_chart_df['year_month'].dt.to_timestamp()
                        line_chart_df = line_chart_df.drop(columns=['year_month'])
                if pd.api.types.is_datetime64_any_dtype(line_chart_df[x_col]) and hasattr(line_chart_df[x_col].dt, 'tz') and line_chart_df[x_col].dt.tz is not None:
                    line_chart_df[x_col] = line_chart_df[x_col].dt.tz_localize(None)
                labels = line_chart_df[x_col].dt.strftime('%Y-%m').tolist()

            line_chart_df = line_chart_df.dropna(subset=[y_col])
            if line_chart_df.empty:
                return jsonify({'error': 'Недостаточно данных для построения линейного графика.'}), 400
            chart_data = {
                'labels': labels,
                'data': line_chart_df[y_col].tolist(),
                'label': f'Сумма {y_col} по времени'
            }
            
        return jsonify({'chart_data': chart_data})

    except Exception as e:
        print(f"Error in /analyze_data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/load_more', methods=['POST'])
def load_more():
    data = request.json
    if not data or not data.get('filepath'):
        return jsonify({'error': 'Invalid request'}), 400

    filepath = data.get('filepath')
    offset = data.get('offset', 100)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found or specified.'}), 400

    if not is_safe_filepath(filepath):
        return jsonify({'error': 'Invalid file path'}), 400
        
    try:
        df = read_data_file(filepath)

        if offset >= len(df):
            return jsonify({'html': '', 'end': True})
            
        more_data_html = df.iloc[offset:offset+100].to_html(header=False, index=False)
        return jsonify({'html': more_data_html, 'end': False})
    except (FileNotFoundError, ValueError) as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_data', methods=['POST'])
def analyze_data():
    """Анализ данных через локальную LLM (Ollama)"""
    data = request.get_json()
    table_data = data.get('table_data')
    
    if not table_data:
        print("Error: No table data received for analysis")
        return jsonify({'error': 'Нет данных таблицы для анализа'}), 400

    try:
        print(f"Calling Ollama LLM service...")
        ai_response = get_llm_analysis(table_data)
        print(f"LLM response received: {ai_response[:200]}...")

        return jsonify({
            'ai_analysis': ai_response,
            'used_model': 'ollama'
        })
    except Exception as e:
        print(f"Error in analyze_data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
