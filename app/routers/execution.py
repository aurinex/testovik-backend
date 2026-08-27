# backend/app/routers/execution.py
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..dependencies import get_current_user
from ..models import User
from ..config import settings

router = APIRouter(prefix="/api/run", tags=["execution"])

class CodeRequest(BaseModel):
    code: str
    language: str  # python, javascript, lua

class CodeResponse(BaseModel):
    output: str
    success: bool
    error: Optional[str] = None

class AIPromptRequest(BaseModel):
    prompt: str

class AIPromptResponse(BaseModel):
    response: str
    success: bool

# URL-ы интерпретаторов
INTERPRETER_URLS = {
    "python": settings.PYTHON_INTERPRETER_URL,
    "javascript": settings.NODEJS_INTERPRETER_URL,
    "lua": settings.LUA_INTERPRETER_URL,
}

@router.post("/code", response_model=CodeResponse)
async def execute_code(
    request: CodeRequest,
    user: User = Depends(get_current_user)
):
    """Выполняет код через соответствующий интерпретатор в Docker"""
    
    # Проверки безопасности
    if len(request.code) > 10000:
        raise HTTPException(status_code=400, detail="Код слишком длинный")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт отключён")
    
    # Проверка языка
    if request.language not in INTERPRETER_URLS:
        raise HTTPException(
            status_code=400,
            detail=f"Язык '{request.language}' не поддерживается. Доступны: {', '.join(INTERPRETER_URLS.keys())}"
        )
    
    # Отправляем код в интерпретатор
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                INTERPRETER_URLS[request.language],
                json={
                    "code": request.code,
                    "language": request.language
                }
            )
            
            if response.status_code != 200:
                return CodeResponse(
                    output="",
                    success=False,
                    error=f"Ошибка интерпретатора: {response.status_code}"
                )
            
            data = response.json()
            return CodeResponse(
                output=data.get("output", "(пустой вывод)"),
                success=data.get("success", False),
                error=data.get("error")
            )
            
    except httpx.TimeoutException:
        return CodeResponse(
            output="",
            success=False,
            error="Превышено время выполнения (10 секунд)"
        )
    except Exception as e:
        return CodeResponse(
            output="",
            success=False,
            error=f"Ошибка выполнения: {str(e)}"
        )


# ==================== AI-промптинг ====================

# Можно использовать внешний API или локальную модель
# Пока оставляем имитацию

async def generate_ai_response(prompt: str) -> tuple[str, bool, Optional[str]]:
    """Генерирует ответ на промпт"""
    
    prompt_lower = prompt.lower()
    
    # Сказка про дружбу
    if "сказка" in prompt_lower and ("дружб" in prompt_lower or "дракон" in prompt_lower):
        return (
            "🐉 Жил-был добрый дракон по имени Дракоша. Однажды он встретил храброго котёнка по имени Мурзик. "
            "Сначала они боялись друг друга, но потом поняли, что вместе они сильнее. "
            "Они стали лучшими друзьями и вместе спасли лес от злых колдунов. "
            "С тех пор они всегда помогали друг другу и другим зверятам! 🐱",
            True,
            None
        )
    
    # Советы по безопасности
    if "совет" in prompt_lower and ("безопасн" in prompt_lower or "интернет" in prompt_lower):
        return (
            "🛡️ 3 главных совета по безопасности в интернете:\n\n"
            "1️⃣ 🔐 **Создавай сложные пароли** — используй буквы, цифры и специальные символы.\n"
            "2️⃣ 🎣 **Не попадайся на фишинг** — не переходи по подозрительным ссылкам.\n"
            "3️⃣ 🤫 **Защищай личные данные** — не публикуй адрес, телефон и пароли.",
            True,
            None
        )
    
    return (
        f"🤖 Спасибо за твой промпт!\n\n"
        f"💡 Для лучшего результата попробуй быть более конкретным.\n"
        f"Примеры хороших промптов:\n"
        f"- «Напиши сказку про дракона и котёнка»\n"
        f"- «Дай 3 совета по безопасности в интернете»",
        True,
        None
    )


@router.post("/ai-prompt", response_model=AIPromptResponse)
async def execute_ai_prompt(
    request: AIPromptRequest,
    user: User = Depends(get_current_user)
):
    """Отправляет промпт в ИИ и возвращает ответ"""
    
    if not request.prompt or len(request.prompt) < 3:
        raise HTTPException(status_code=400, detail="Промпт слишком короткий")
    
    if len(request.prompt) > 5000:
        raise HTTPException(status_code=400, detail="Промпт слишком длинный")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт отключён")
    
    response, success, error = await generate_ai_response(request.prompt)
    
    return AIPromptResponse(
        response=response,
        success=success
    )