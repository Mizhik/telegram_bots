import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

# Припустимо, що у вас є файл bags.csv з даними
data = pd.read_csv("bags.csv")

# Перевірте, чи є стовпець "gender" для класифікації
if "gender" not in data.columns:
    raise ValueError("Датасет повинен містити стовпець 'gender' для класифікації.")

# Видалення нечислових стовпців, якщо вони є
data_numeric = data.select_dtypes(include=np.number)

# Перевірка наявності числових стовпців після видалення нечислових
if data_numeric.empty:
    raise ValueError(
        "Після видалення нечислових стовпців не залишилося числових даних."
    )

# Підготовка даних для кластеризації та класифікації
X = data_numeric  # Використовуємо всі числові стовпці для кластеризації
y = data["gender"]  # Цільова змінна для класифікації

# Розділення даних на тренувальну та тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Стандартизація ознак
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Кластеризація за допомогою K-means
kmeans = KMeans(n_clusters=2, random_state=42)  # 2 кластери (жіночі/чоловічі)
clusters = kmeans.fit_predict(X_train_scaled)

# Додавання кластерів до тренувальних даних
X_train_clustered = X_train.copy()
X_train_clustered["cluster"] = clusters

# Логістична регресія для класифікації
model = LogisticRegression(random_state=42)
model.fit(X_train_scaled, y_train)
y_pred = model.predict(X_test_scaled)

# Оцінка моделі
accuracy = accuracy_score(y_test, y_pred)
print(f"Точність класифікації: {accuracy:.2f}")
print(classification_report(y_test, y_pred))

# Візуалізація кластеризації (зменшення розмірності за допомогою PCA)
pca = PCA(n_components=2)
principal_components = pca.fit_transform(X_train_scaled)
principal_df = pd.DataFrame(data=principal_components, columns=["PC1", "PC2"])
principal_df["cluster"] = clusters
principal_df["gender"] = y_train.values

plt.figure(figsize=(10, 6))
sns.scatterplot(x="PC1", y="PC2", hue="cluster", style="gender", data=principal_df)
plt.title("Кластеризація сумок")
plt.show()

# Матриця плутанини для класифікації
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues")
plt.title("Матриця плутанини класифікації")
plt.xlabel("Прогнозовані значення")
plt.ylabel("Фактичні значення")
plt.show()

# Збереження результатів класифікації
results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
results.to_csv("classification_results.csv", index=False)

print("Результати збережено у файл classification_results.csv")
