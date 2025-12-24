def format_application(app):
    return f"""📋 ЗАЯВКА #{app.id}

💎 Тариф: {app.tariff}
💰 Сума: {app.amount}₴
👤 Ім'я: {app.name}
🎯 Мета: {app.purpose}
📞 Контакт: {app.contact}"""

def format_project(project):
    return f"""🖥 ПРОЕКТ #{project.id}

👤 Власник: {project.leader_username}
💎 Тариф: {project.tariff}
🤖 Ботів: {project.bots_used}/{project.bots_limit}
👥 Менеджерів: {project.managers_used}/{project.managers_limit}"""
