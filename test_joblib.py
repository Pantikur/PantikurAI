import joblib

# Тестовые данные
data = {'name': 'Baura', 'skills': ['Python', 'Machine Learning']}

# Сохраняем
joblib.dump(data, 'test_save.pkl')
print("✅ Данные сохранены в test_save.pkl")

# Загружаем обратно
loaded = joblib.load('test_save.pkl')
print("📥 Загружено:", loaded)