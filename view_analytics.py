#!/usr/bin/env python3
"""
Скрипт для просмотра аналитики использования пресетов и промптов
Показывает статистику выбора пресетов и кастомных промптов пользователями
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

# Добавляем путь к backend для импорта
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.database import SessionLocal, engine
from app.models import Job, Preset, User, JobStatus
from app.config import settings


class AnalyticsViewer:
    """Класс для просмотра аналитики использования пресетов и промптов"""
    
    def __init__(self):
        self.db: Session = SessionLocal()
        self.presets_cache: Dict[int, Preset] = {}
        self._load_presets()
    
    def _load_presets(self):
        """Загрузить все пресеты в кэш"""
        presets = self.db.query(Preset).all()
        for preset in presets:
            self.presets_cache[preset.id] = preset
    
    def _match_prompt_to_preset(self, prompt: str) -> Optional[Preset]:
        """Сопоставить промпт с пресетом (точное совпадение или частичное)"""
        if not prompt:
            return None
        
        prompt_clean = prompt.strip()
        
        # Сначала ищем точное совпадение
        for preset in self.presets_cache.values():
            if preset.prompt and preset.prompt.strip() == prompt_clean:
                return preset
        
        # Затем ищем частичное совпадение (промпт пресета содержится в промпте джобы)
        for preset in self.presets_cache.values():
            if preset.prompt and preset.prompt.strip() in prompt_clean:
                return preset
        
        return None
    
    def get_preset_usage_stats(self, days: Optional[int] = None) -> Dict:
        """Получить статистику использования пресетов"""
        query = self.db.query(Job)
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Job.created_at >= cutoff_date)
        
        jobs = query.filter(Job.status.in_([JobStatus.completed, JobStatus.processing, JobStatus.queued])).all()
        
        preset_usage = Counter()
        custom_prompts = []
        preset_details = defaultdict(list)
        
        for job in jobs:
            matched_preset = self._match_prompt_to_preset(job.prompt)
            
            if matched_preset:
                preset_key = f"{matched_preset.category} / {matched_preset.name}"
                preset_usage[preset_key] += 1
                preset_details[preset_key].append({
                    'job_id': job.id,
                    'user_id': job.user_id,
                    'created_at': job.created_at,
                    'status': job.status.value
                })
            else:
                custom_prompts.append({
                    'job_id': job.id,
                    'user_id': job.user_id,
                    'prompt': job.prompt[:100] + '...' if job.prompt and len(job.prompt) > 100 else job.prompt,
                    'created_at': job.created_at,
                    'status': job.status.value
                })
        
        return {
            'preset_usage': dict(preset_usage.most_common()),
            'custom_prompts': custom_prompts,
            'preset_details': dict(preset_details),
            'total_jobs': len(jobs),
            'preset_jobs': sum(preset_usage.values()),
            'custom_jobs': len(custom_prompts)
        }
    
    def get_user_stats(self, days: Optional[int] = None) -> List[Dict]:
        """Получить статистику по пользователям"""
        query = self.db.query(
            User.user_id,
            User.username,
            User.telegram_id,
            func.count(Job.id).label('job_count')
        ).join(Job, User.user_id == Job.user_id)
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Job.created_at >= cutoff_date)
        
        query = query.group_by(User.user_id, User.username, User.telegram_id)
        query = query.order_by(desc('job_count'))
        
        results = query.all()
        
        return [
            {
                'user_id': row.user_id,
                'username': row.username or f"user_{row.telegram_id}",
                'telegram_id': row.telegram_id,
                'job_count': row.job_count
            }
            for row in results
        ]
    
    def get_recent_jobs(self, limit: int = 20) -> List[Dict]:
        """Получить последние джобы с деталями"""
        jobs = self.db.query(Job).join(User).order_by(desc(Job.created_at)).limit(limit).all()
        
        result = []
        for job in jobs:
            matched_preset = self._match_prompt_to_preset(job.prompt)
            preset_info = None
            if matched_preset:
                preset_info = f"{matched_preset.category} / {matched_preset.name}"
            
            result.append({
                'job_id': job.id,
                'user_id': job.user_id,
                'username': job.user.username if job.user else None,
                'telegram_id': job.user.telegram_id if job.user else None,
                'preset': preset_info,
                'prompt': job.prompt[:150] + '...' if job.prompt and len(job.prompt) > 150 else job.prompt,
                'is_custom': matched_preset is None,
                'status': job.status.value,
                'created_at': job.created_at
            })
        
        return result
    
    def print_preset_usage_stats(self, days: Optional[int] = None):
        """Вывести статистику использования пресетов"""
        stats = self.get_preset_usage_stats(days)
        
        print("\n" + "="*80)
        print("📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ ПРЕСЕТОВ")
        if days:
            print(f"   Период: последние {days} дней")
        print("="*80)
        
        print(f"\n📈 Общая статистика:")
        print(f"   Всего джоб: {stats['total_jobs']}")
        print(f"   С пресетами: {stats['preset_jobs']} ({stats['preset_jobs']/stats['total_jobs']*100:.1f}%)" if stats['total_jobs'] > 0 else "   С пресетами: 0")
        print(f"   Кастомных промптов: {stats['custom_jobs']} ({stats['custom_jobs']/stats['total_jobs']*100:.1f}%)" if stats['total_jobs'] > 0 else "   Кастомных промптов: 0")
        
        if stats['preset_usage']:
            print(f"\n🏆 ТОП ПРЕСЕТОВ (по использованию):")
            print("-" * 80)
            for i, (preset_name, count) in enumerate(stats['preset_usage'].most_common(20), 1):
                percentage = (count / stats['preset_jobs'] * 100) if stats['preset_jobs'] > 0 else 0
                print(f"   {i:2d}. {preset_name:50s} | {count:4d} раз ({percentage:5.1f}%)")
        
        if stats['custom_prompts']:
            print(f"\n✍️  ПОСЛЕДНИЕ КАСТОМНЫЕ ПРОМПТЫ (показано до 10):")
            print("-" * 80)
            for i, prompt_data in enumerate(stats['custom_prompts'][:10], 1):
                print(f"\n   {i}. Job ID: {prompt_data['job_id']}, User ID: {prompt_data['user_id']}")
                print(f"      Промпт: {prompt_data['prompt']}")
                print(f"      Дата: {prompt_data['created_at']}, Статус: {prompt_data['status']}")
    
    def print_user_stats(self, days: Optional[int] = None):
        """Вывести статистику по пользователям"""
        stats = self.get_user_stats(days)
        
        print("\n" + "="*80)
        print("👥 СТАТИСТИКА ПО ПОЛЬЗОВАТЕЛЯМ")
        if days:
            print(f"   Период: последние {days} дней")
        print("="*80)
        
        if not stats:
            print("\n   Нет данных")
            return
        
        print(f"\n📊 ТОП ПОЛЬЗОВАТЕЛЕЙ (по количеству джоб):")
        print("-" * 80)
        for i, user in enumerate(stats[:20], 1):
            print(f"   {i:2d}. @{user['username']:20s} | User ID: {user['user_id']:5d} | Telegram ID: {user['telegram_id']:10d} | Джоб: {user['job_count']:4d}")
    
    def print_recent_jobs(self, limit: int = 20):
        """Вывести последние джобы"""
        jobs = self.get_recent_jobs(limit)
        
        print("\n" + "="*80)
        print(f"🕐 ПОСЛЕДНИЕ {limit} ДЖОБ")
        print("="*80)
        
        if not jobs:
            print("\n   Нет данных")
            return
        
        for i, job in enumerate(jobs, 1):
            preset_marker = "🎨" if job['preset'] else "✍️"
            preset_info = f"Пресет: {job['preset']}" if job['preset'] else "Кастомный промпт"
            
            print(f"\n   {i}. {preset_marker} Job ID: {job['job_id']}")
            print(f"      Пользователь: @{job['username'] or 'unknown'} (ID: {job['user_id']}, TG: {job['telegram_id']})")
            print(f"      {preset_info}")
            if job['is_custom']:
                print(f"      Промпт: {job['prompt']}")
            print(f"      Статус: {job['status']}, Дата: {job['created_at']}")
    
    def print_full_report(self, days: Optional[int] = None):
        """Вывести полный отчет"""
        self.print_preset_usage_stats(days)
        self.print_user_stats(days)
        self.print_recent_jobs(20)
        print("\n" + "="*80)
        print("✅ Отчет завершен")
        print("="*80 + "\n")
    
    def close(self):
        """Закрыть соединение с БД"""
        self.db.close()


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Просмотр аналитики использования пресетов и промптов",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python view_analytics.py                    # Полный отчет
  python view_analytics.py --presets          # Только статистика пресетов
  python view_analytics.py --users            # Только статистика пользователей
  python view_analytics.py --recent           # Только последние джобы
  python view_analytics.py --days 7           # Статистика за последние 7 дней
  python view_analytics.py --presets --days 30 # Пресеты за последние 30 дней
        """
    )
    
    parser.add_argument('--presets', action='store_true', help='Показать статистику пресетов')
    parser.add_argument('--users', action='store_true', help='Показать статистику пользователей')
    parser.add_argument('--recent', action='store_true', help='Показать последние джобы')
    parser.add_argument('--days', type=int, help='Период в днях (например, 7 для последней недели)')
    parser.add_argument('--limit', type=int, default=20, help='Количество последних джоб (по умолчанию: 20)')
    
    args = parser.parse_args()
    
    viewer = AnalyticsViewer()
    
    try:
        if args.presets:
            viewer.print_preset_usage_stats(args.days)
        elif args.users:
            viewer.print_user_stats(args.days)
        elif args.recent:
            viewer.print_recent_jobs(args.limit)
        else:
            # Полный отчет по умолчанию
            viewer.print_full_report(args.days)
    finally:
        viewer.close()


if __name__ == "__main__":
    main()
