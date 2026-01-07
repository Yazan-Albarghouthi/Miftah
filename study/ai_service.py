"""
AI service for generating flashcards and quizzes using OpenAI API.
"""

import json
import re
from openai import OpenAI
from django.conf import settings


def detect_language(text):
    """
    Detect if text is primarily Arabic or English.
    Returns 'ar' for Arabic, 'en' for English.
    """
    # Count Arabic characters (Arabic Unicode range)
    arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
    # Count English characters
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    if arabic_chars > english_chars:
        return 'ar'
    return 'en'


def get_openai_client():
    """Get configured OpenAI client."""
    return OpenAI(
        api_key=settings.OPENAI_API_KEY
    )


def clean_json_response(response_text):
    """
    Clean AI response to extract valid JSON.
    Sometimes AI wraps JSON in markdown code blocks.
    """
    # Remove markdown code blocks if present
    cleaned = response_text.strip()

    # Remove ```json or ``` wrapper
    if cleaned.startswith('```'):
        # Find the end of the first line (might be ```json)
        first_newline = cleaned.find('\n')
        if first_newline != -1:
            cleaned = cleaned[first_newline + 1:]
        # Remove trailing ```
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]

    return cleaned.strip()


def generate_flashcards(text, count=10):
    """
    Generate flashcards from the provided text using OpenAI.

    Args:
        text: Source text to generate flashcards from
        count: Number of flashcards to generate (default 10)

    Returns:
        dict with 'success', 'language', 'flashcards' or 'error'
    """
    language = detect_language(text)

    if language == 'ar':
        system_prompt = """أنت مساعد تعليمي متخصص في إنشاء بطاقات تعليمية.
قواعد مهمة:
1. استخدم فقط المعلومات الموجودة في النص المقدم
2. إذا لم تكن المعلومة موجودة في النص، اكتب "غير مذكور في النص"
3. اجعل الأسئلة واضحة ومباشرة
4. اجعل الإجابات موجزة ودقيقة
5. أرجع JSON فقط بدون أي نص إضافي"""

        user_prompt = f"""أنشئ {count} بطاقة تعليمية من النص التالي.

النص:
{text}

أرجع JSON بالتنسيق التالي فقط:
{{"flashcards": [{{"question": "السؤال", "answer": "الإجابة"}}]}}"""

    else:
        system_prompt = """You are an educational assistant specialized in creating flashcards.
Important rules:
1. Use ONLY information from the provided text
2. If information is not stated in the text, write "Not stated in the text"
3. Make questions clear and direct
4. Keep answers concise and accurate
5. Return JSON only without any additional text"""

        user_prompt = f"""Create {count} flashcards from the following text.

Text:
{text}

Return JSON in this format only:
{{"flashcards": [{{"question": "Question here", "answer": "Answer here"}}]}}"""

    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=4000
        )

        response_text = response.choices[0].message.content
        cleaned_json = clean_json_response(response_text)

        # Parse JSON
        data = json.loads(cleaned_json)

        # Validate structure
        if 'flashcards' not in data:
            raise ValueError("Missing 'flashcards' key in response")

        flashcards = data['flashcards']
        if not isinstance(flashcards, list):
            raise ValueError("'flashcards' must be a list")

        # Validate each flashcard
        for i, card in enumerate(flashcards):
            if 'question' not in card or 'answer' not in card:
                raise ValueError(f"Flashcard {i} missing question or answer")

        return {
            'success': True,
            'language': language,
            'flashcards': flashcards
        }

    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'خطأ في تحليل الرد: {str(e)}' if language == 'ar' else f'JSON parsing error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'خطأ في الاتصال بالخدمة: {str(e)}' if language == 'ar' else f'Service error: {str(e)}'
        }


def generate_quiz(text, count=10):
    """
    Generate quiz questions from the provided text using OpenAI.

    Args:
        text: Source text to generate quiz from
        count: Number of questions to generate (default 10)

    Returns:
        dict with 'success', 'language', 'questions' or 'error'
    """
    language = detect_language(text)

    if language == 'ar':
        system_prompt = """أنت مساعد تعليمي متخصص في إنشاء أسئلة اختبار متعددة الخيارات.
قواعد مهمة:
1. استخدم فقط المعلومات الموجودة في النص المقدم
2. كل سؤال يجب أن يحتوي على 4 خيارات بالضبط
3. إجابة صحيحة واحدة فقط لكل سؤال
4. اكتب شرحاً لكل خيار يوضح لماذا هو صحيح أو خاطئ
5. إذا لم تكن المعلومة موجودة في النص، اكتب "غير مذكور في النص"
6. أرجع JSON فقط بدون أي نص إضافي

تنسيق الشرح:
أ) شرح الخيار الأول
ب) شرح الخيار الثاني
ج) شرح الخيار الثالث
د) شرح الخيار الرابع"""

        user_prompt = f"""أنشئ {count} سؤال اختبار متعدد الخيارات من النص التالي.

النص:
{text}

أرجع JSON بالتنسيق التالي فقط:
{{"questions": [{{"question": "السؤال", "options": ["خيار1", "خيار2", "خيار3", "خيار4"], "correctIndex": 0, "explanation": "أ) شرح... ب) شرح... ج) شرح... د) شرح..."}}]}}"""

    else:
        system_prompt = """You are an educational assistant specialized in creating multiple choice quiz questions.
Important rules:
1. Use ONLY information from the provided text
2. Each question must have exactly 4 options
3. Only one correct answer per question
4. Write an explanation for each option explaining why it's correct or incorrect
5. If information is not stated in the text, write "Not stated in the text"
6. Return JSON only without any additional text

Explanation format:
A) Explanation for first option
B) Explanation for second option
C) Explanation for third option
D) Explanation for fourth option"""

        user_prompt = f"""Create {count} multiple choice quiz questions from the following text.

Text:
{text}

Return JSON in this format only:
{{"questions": [{{"question": "Question here", "options": ["option1", "option2", "option3", "option4"], "correctIndex": 0, "explanation": "A) explanation... B) explanation... C) explanation... D) explanation..."}}]}}"""

    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=6000
        )

        response_text = response.choices[0].message.content
        cleaned_json = clean_json_response(response_text)

        # Parse JSON
        data = json.loads(cleaned_json)

        # Validate structure
        if 'questions' not in data:
            raise ValueError("Missing 'questions' key in response")

        questions = data['questions']
        if not isinstance(questions, list):
            raise ValueError("'questions' must be a list")

        # Validate each question
        for i, q in enumerate(questions):
            if 'question' not in q:
                raise ValueError(f"Question {i} missing 'question' field")
            if 'options' not in q or len(q['options']) != 4:
                raise ValueError(f"Question {i} must have exactly 4 options")
            if 'correctIndex' not in q or not (0 <= q['correctIndex'] <= 3):
                raise ValueError(f"Question {i} has invalid correctIndex")
            if 'explanation' not in q:
                raise ValueError(f"Question {i} missing explanation")

        return {
            'success': True,
            'language': language,
            'questions': questions
        }

    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'خطأ في تحليل الرد: {str(e)}' if language == 'ar' else f'JSON parsing error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'خطأ في الاتصال بالخدمة: {str(e)}' if language == 'ar' else f'Service error: {str(e)}'
        }


def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.

    Args:
        pdf_file: Django uploaded file object

    Returns:
        dict with 'success' and 'text' or 'error'
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_file)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = '\n'.join(text_parts).strip()

        if not full_text:
            return {
                'success': False,
                'error': 'لا يمكن استخراج نص من هذا الملف. يبدو أنه ملف PDF ممسوح ضوئياً (صور). يرجى استخدام ملف PDF يحتوي على نص قابل للنسخ.',
                'is_ocr': True
            }

        # Check if extracted text is too short (might be partial OCR or corrupted)
        if len(full_text) < 50:
            return {
                'success': False,
                'error': 'النص المستخرج قصير جداً (أقل من 50 حرف). قد يكون الملف ممسوحاً ضوئياً أو تالفاً. يرجى استخدام ملف PDF آخر.',
                'is_ocr': True
            }

        return {
            'success': True,
            'text': full_text,
            'char_count': len(full_text)
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'خطأ في قراءة الملف: {str(e)}'
        }
