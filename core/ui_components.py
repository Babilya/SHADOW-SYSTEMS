"""
Shared UI Components for consistent UX across all menus
- Inline search
- Pagination
- Progress indicators
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Callable, Any, Optional
import math


class Paginator:
    """Universal pagination component for any list data"""
    
    def __init__(
        self, 
        items: List[Any], 
        page: int = 1, 
        per_page: int = 10,
        callback_prefix: str = "page"
    ):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.callback_prefix = callback_prefix
        self.total_pages = max(1, math.ceil(len(items) / per_page))
    
    @property
    def current_items(self) -> List[Any]:
        """Get items for current page"""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages
    
    def get_nav_buttons(self) -> List[InlineKeyboardButton]:
        """Generate navigation buttons"""
        buttons = []
        
        if self.has_prev:
            buttons.append(InlineKeyboardButton(
                text="◀️ Назад", 
                callback_data=f"{self.callback_prefix}:{self.page - 1}"
            ))
        
        buttons.append(InlineKeyboardButton(
            text=f"📄 {self.page}/{self.total_pages}",
            callback_data="page_info"
        ))
        
        if self.has_next:
            buttons.append(InlineKeyboardButton(
                text="Вперед ▶️",
                callback_data=f"{self.callback_prefix}:{self.page + 1}"
            ))
        
        return buttons
    
    def get_info_text(self) -> str:
        """Get pagination info text"""
        start = (self.page - 1) * self.per_page + 1
        end = min(self.page * self.per_page, len(self.items))
        return f"📊 Показано {start}-{end} з {len(self.items)}"


class ProgressBar:
    """Visual progress indicator"""
    
    FILLED = "█"
    EMPTY = "░"
    
    @staticmethod
    def render(progress: int, width: int = 10) -> str:
        """Render a text-based progress bar"""
        progress = max(0, min(100, progress))
        filled = int(width * progress / 100)
        empty = width - filled
        bar = ProgressBar.FILLED * filled + ProgressBar.EMPTY * empty
        return f"[{bar}] {progress}%"
    
    @staticmethod
    def render_emoji(progress: int) -> str:
        """Render an emoji-based progress bar"""
        progress = max(0, min(100, progress))
        
        if progress == 100:
            return "✅ Завершено"
        elif progress >= 75:
            return "🟢🟢🟢⚪ 75%"
        elif progress >= 50:
            return "🟢🟢⚪⚪ 50%"
        elif progress >= 25:
            return "🟢⚪⚪⚪ 25%"
        else:
            return "⚪⚪⚪⚪ 0%"
    
    @staticmethod
    def render_detailed(progress: int, label: str = "Прогрес") -> str:
        """Render detailed progress with label"""
        bar = ProgressBar.render(progress)
        return f"<b>{label}:</b> {bar}"


class InlineSearchBuilder:
    """Builder for inline search functionality"""
    
    @staticmethod
    def build_search_button(callback_data: str, placeholder: str = "Пошук...") -> InlineKeyboardButton:
        """Create a search button that triggers switch_inline_query"""
        return InlineKeyboardButton(
            text=f"🔍 {placeholder}",
            switch_inline_query_current_chat=""
        )
    
    @staticmethod
    def filter_items(items: List[Any], query: str, key_func: Callable[[Any], str]) -> List[Any]:
        """Filter items by search query"""
        if not query:
            return items
        
        query_lower = query.lower()
        return [item for item in items if query_lower in key_func(item).lower()]


class MenuBuilder:
    """Helper to build consistent menus"""
    
    @staticmethod
    def build_grid(
        buttons: List[tuple], 
        columns: int = 2, 
        back_callback: str = "back_to_menu"
    ) -> InlineKeyboardMarkup:
        """Build a grid layout from (text, callback) tuples"""
        keyboard = []
        row = []
        
        for text, callback in buttons:
            row.append(InlineKeyboardButton(text=text, callback_data=callback))
            if len(row) >= columns:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def build_list(
        items: List[Any],
        format_func: Callable[[Any], tuple],
        page: int = 1,
        per_page: int = 10,
        callback_prefix: str = "item",
        back_callback: str = "back_to_menu"
    ) -> InlineKeyboardMarkup:
        """Build a paginated list menu"""
        paginator = Paginator(items, page, per_page, f"{callback_prefix}_page")
        
        keyboard = []
        for item in paginator.current_items:
            text, callback = format_func(item)
            keyboard.append([InlineKeyboardButton(text=text, callback_data=callback)])
        
        if paginator.total_pages > 1:
            keyboard.append(paginator.get_nav_buttons())
        
        keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=back_callback)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)


def format_divider(style: str = "double") -> str:
    """Generate consistent dividers"""
    styles = {
        "double": "═══════════════════════",
        "single": "───────────────────────",
        "dots": "• • • • • • • • • • • •",
        "dashes": "━━━━━━━━━━━━━━━━━━━━━━━"
    }
    return styles.get(style, styles["double"])
