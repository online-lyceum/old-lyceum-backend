with open('./async_lyceum_api/description.md', encoding='utf-8') as file:
    description = file.read()

application_metadata = {
    "title": "Асинхронное API расписания для проекта Лицей в Цифре",
    "description": description,
    "version": "0.0.2.dev1",
}
