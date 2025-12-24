class NotificationSystem:
    @staticmethod
    async def notify_admin(bot, admin_id: int, text: str):
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"Error: {e}")
