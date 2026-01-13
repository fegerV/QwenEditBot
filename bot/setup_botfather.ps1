# setup_botfather.ps1
# Скрипт для автоматической настройки бота через API Telegram

param(
    [string]$BotToken = $(Read-Host "Введите токен бота (BOT_TOKEN)")
)

# Проверка ввода токена
if ([string]::IsNullOrWhiteSpace($BotToken)) {
    Write-Host "❌ Ошибка: Токен бота не может быть пустым!" -ForegroundColor Red
    Write-Host "Получите токен от @BotFather в Telegram" -ForegroundColor Yellow
    exit 1
}

$ApiUrl = "https://api.telegram.org/bot$BotToken"

Write-Host "🤖 Настройка QwenEditBot через BotFather API..." -ForegroundColor Green
Write-Host "Токен бота: $($BotToken.Substring(0, 8))..." -ForegroundColor Gray
Write-Host ""

# Проверка токена
Write-Host "1. Проверка токена бота..." -ForegroundColor Cyan
try {
    $tokenCheck = Invoke-RestMethod -Uri "$ApiUrl/getMe"
    if ($tokenCheck.ok) {
        Write-Host "✅ Токен действителен!" -ForegroundColor Green
        Write-Host "   Бот: $($tokenCheck.result.first_name) (@$($tokenCheck.result.username))" -ForegroundColor Gray
    } else {
        Write-Host "❌ Недействительный токен!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Ошибка при проверке токена: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Установка команд
Write-Host "2. Настройка команд бота..." -ForegroundColor Cyan

$commands = @(
    @{ command = "start"; description = "Запустить бота" }
    @{ command = "help"; description = "Справка по боту" }
    @{ command = "menu"; description = "Главное меню" }
    @{ command = "balance"; description = "Показать баланс" }
    @{ command = "cancel"; description = "Отменить действие" }
)

$commandsJson = $commands | ConvertTo-Json -Depth 10

try {
    $commandsResult = Invoke-RestMethod -Uri "$ApiUrl/setMyCommands" `
        -Method Post `
        -ContentType "application/json" `
        -Body $commandsJson

    if ($commandsResult.ok) {
        Write-Host "✅ Команды успешно установлены!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при установке команд: $($commandsResult.description)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка сети при установке команд: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Установка описания
Write-Host "3. Настройка описания бота..." -ForegroundColor Cyan

$description = "QwenEditBot - AI редактор фото с нейросетью Qwen. Редактируйте фото по стилям или собственному промпту."

$descriptionBody = @{
    description = $description
} | ConvertTo-Json

try {
    $descriptionResult = Invoke-RestMethod -Uri "$ApiUrl/setMyDescription" `
        -Method Post `
        -ContentType "application/json" `
        -Body $descriptionBody

    if ($descriptionResult.ok) {
        Write-Host "✅ Описание успешно установлено!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при установке описания: $($descriptionResult.description)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка сети при установке описания: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Установка информации о боте
Write-Host "4. Настройка информации о боте..." -ForegroundColor Cyan

$aboutText = "Быстрый и простой редактор фото на основе нейросети Qwen. Применяйте стили, изменяйте освещение, добавляйте эффекты. Работает за 10-30 секунд!"

$aboutBody = @{
    about = $aboutText
} | ConvertTo-Json

try {
    $aboutResult = Invoke-RestMethod -Uri "$ApiUrl/setMyShortDescription" `
        -Method Post `
        -ContentType "application/json" `
        -Body $aboutBody

    if ($aboutResult.ok) {
        Write-Host "✅ Информация о боте успешно установлена!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при установке информации: $($aboutResult.description)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка сети при установке информации: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Результат
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "🎉 Настройка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Что настроено:" -ForegroundColor Yellow
Write-Host "   ✅ 5 команд бота" -ForegroundColor Green
Write-Host "   ✅ Описание бота" -ForegroundColor Green
Write-Host "   ✅ Информация о боте" -ForegroundColor Green
Write-Host ""
Write-Host "🔍 Проверьте настройку:" -ForegroundColor Yellow
Write-Host "1. Откройте чат с вашим ботом" -ForegroundColor White
Write-Host "2. Начните вводить '/' - должны появиться команды" -ForegroundColor White
Write-Host "3. Откройте профиль бота - должно отображаться описание" -ForegroundColor White
Write-Host ""
Write-Host "📚 Дополнительные инструкции: SETUP_INSTRUCTIONS.md" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Yellow