#!/bin/bash
# setup_botfather.sh
# Скрипт для автоматической настройки бота через API Telegram

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Функция для проверки зависимостей
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ Ошибка: curl не установлен!${NC}"
        echo "Установите curl для продолжения:"
        echo "  Ubuntu/Debian: sudo apt-get install curl"
        echo "  CentOS/RHEL: sudo yum install curl"
        echo "  macOS: brew install curl"
        exit 1
    fi
}

# Функция для проверки токена
check_token() {
    local token="$1"
    if [[ -z "$token" ]]; then
        echo -e "${RED}❌ Ошибка: Токен бота не может быть пустым!${NC}"
        echo "Получите токен от @BotFather в Telegram"
        exit 1
    fi
}

# Функция для проверки ответа API
check_response() {
    local response="$1"
    local operation="$2"
    
    if echo "$response" | grep -q '"ok":true'; then
        echo -e "${GREEN}✅ $operation успешно выполнено!${NC}"
        return 0
    else
        echo -e "${RED}❌ Ошибка при выполнении: $operation${NC}"
        echo "$response" | grep -o '"description":"[^"]*"' | cut -d'"' -f4
        return 1
    fi
}

echo -e "${GREEN}🤖 Настройка QwenEditBot через BotFather API...${NC}"

# Проверка зависимостей
check_dependencies

# Ввод токена
read -p "Введите токен бота (BOT_TOKEN): " BOT_TOKEN

# Проверка токена
check_token "$BOT_TOKEN"

API_URL="https://api.telegram.org/bot$BOT_TOKEN"

echo -e "${CYAN}Токен бота: ${BOT_TOKEN:0:8}...${NC}"
echo ""

# Проверка токена
echo -e "${CYAN}1. Проверка токена бота...${NC}"
TOKEN_CHECK=$(curl -s "$API_URL/getMe")

if echo "$TOKEN_CHECK" | grep -q '"ok":true'; then
    BOT_NAME=$(echo "$TOKEN_CHECK" | grep -o '"first_name":"[^"]*"' | cut -d'"' -f4)
    BOT_USERNAME=$(echo "$TOKEN_CHECK" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Токен действителен!${NC}"
    echo -e "${WHITE}   Бот: $BOT_NAME (@$BOT_USERNAME)${NC}"
else
    echo -e "${RED}❌ Недействительный токен!${NC}"
    exit 1
fi

echo ""

# Установка команд
echo -e "${CYAN}2. Настройка команд бота...${NC}"

COMMANDS_JSON='{
  "commands": [
    {"command": "start", "description": "Запустить бота"},
    {"command": "help", "description": "Справка по боту"},
    {"command": "menu", "description": "Главное меню"},
    {"command": "balance", "description": "Показать баланс"},
    {"command": "cancel", "description": "Отменить действие"}
  ]
}'

COMMANDS_RESULT=$(curl -s -X POST "$API_URL/setMyCommands" \
  -H "Content-Type: application/json" \
  -d "$COMMANDS_JSON")

check_response "$COMMANDS_RESULT" "Установка команд"

echo ""

# Установка описания
echo -e "${CYAN}3. Настройка описания бота...${NC}"

DESCRIPTION_JSON='{
  "description": "QwenEditBot - AI редактор фото с нейросетью Qwen. Редактируйте фото по стилям или собственному промпту."
}'

DESCRIPTION_RESULT=$(curl -s -X POST "$API_URL/setMyDescription" \
  -H "Content-Type: application/json" \
  -d "$DESCRIPTION_JSON")

check_response "$DESCRIPTION_RESULT" "Установка описания"

echo ""

# Установка информации о боте
echo -e "${CYAN}4. Настройка информации о боте...${NC}"

ABOUT_JSON='{
  "about": "Быстрый и простой редактор фото на основе нейросети Qwen. Применяйте стили, изменяйте освещение, добавляйте эффекты. Работает за 10-30 секунд!"
}'

ABOUT_RESULT=$(curl -s -X POST "$API_URL/setMyShortDescription" \
  -H "Content-Type: application/json" \
  -d "$ABOUT_JSON")

check_response "$ABOUT_RESULT" "Установка информации о боте"

echo ""

# Результат
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}🎉 Настройка завершена!${NC}"
echo ""
echo -e "${YELLOW}📋 Что настроено:${NC}"
echo -e "${GREEN}   ✅ 5 команд бота${NC}"
echo -e "${GREEN}   ✅ Описание бота${NC}"
echo -e "${GREEN}   ✅ Информация о боте${NC}"
echo ""
echo -e "${YELLOW}🔍 Проверьте настройку:${NC}"
echo -e "${WHITE}1. Откройте чат с вашим ботом${NC}"
echo -e "${WHITE}2. Начните вводить '/' - должны появиться команды${NC}"
echo -e "${WHITE}3. Откройте профиль бота - должно отображаться описание${NC}"
echo ""
echo -e "${CYAN}📚 Дополнительные инструкции: SETUP_INSTRUCTIONS.md${NC}"
echo -e "${YELLOW}========================================${NC}"