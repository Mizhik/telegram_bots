import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.decomposition import PCA

# Завантаження даних
data = pd.read_csv("heart_failure_patients.csv")

# 1. Попередній аналіз даних
print("Перші 5 рядків даних:")
print(data.head())
print("\nІнформація про дані:")
print(data.info())
print("\nСтатистичний опис даних:")
print(data.describe())

# 2. Візуалізація розподілу смертності
plt.figure(figsize=(8, 6))
sns.countplot(x="DEATH_EVENT", data=data)
plt.title("Розподіл смертності пацієнтів")
plt.xlabel("Смертність (0 = Вижив, 1 = Помер)")
plt.ylabel("Кількість")
plt.savefig("death_distribution.png")
plt.show()

# 3. Кластеризація пацієнтів
# Вибір ознак для кластеризації (виключаємо patient_name)
features = data.drop(["DEATH_EVENT", "patient_name"], axis=1)
# Стандартизація даних
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# Визначення оптимальної кількості кластерів (метод ліктя)
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init="k-means++", random_state=42)
    kmeans.fit(scaled_features)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(range(1, 11), wcss, marker="o", linestyle="--")
plt.title("Метод ліктя для визначення оптимальної кількості кластерів")
plt.xlabel("Кількість кластерів")
plt.ylabel("WCSS")
plt.savefig("elbow_method.png")
plt.show()

# Кластеризація з оптимальною кількістю кластерів (припустимо 3)
kmeans = KMeans(n_clusters=3, init="k-means++", random_state=42)
clusters = kmeans.fit_predict(scaled_features)
data["Cluster"] = clusters

# Візуалізація кластерів (зменшення розмірності за допомогою PCA)
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_features)
principal_df = pd.DataFrame(data=principal_components, columns=["PC1", "PC2"])
principal_df["Cluster"] = clusters
principal_df["DEATH_EVENT"] = data["DEATH_EVENT"]

plt.figure(figsize=(12, 8))
sns.scatterplot(
    x="PC1",
    y="PC2",
    hue="Cluster",
    style="DEATH_EVENT",
    data=principal_df,
    palette="viridis",
    s=100,
)
plt.title("Кластеризація пацієнтів (PCA)")
plt.savefig("clustering_pca.png")
plt.show()

# 4. Кореляційний аналіз (виключаємо patient_name)
plt.figure(figsize=(12, 10))
corr_matrix = data.drop("patient_name", axis=1).corr()
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Кореляційна матриця")
plt.savefig("correlation_matrix.png")
plt.show()

# 5. Вибір найважливіших ознак для прогнозування
important_features = [
    "age",
    "ejection_fraction",
    "serum_creatinine",
    "serum_sodium",
    "time",
]
X = data[important_features]
y = data["DEATH_EVENT"]

# 6. Розділення даних на тренувальну та тестову вибірки
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Стандартизація даних
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 7. Навчання моделі логістичної регресії з зваженими класами
model = LogisticRegression(class_weight="balanced", max_iter=1000)
model.fit(X_train_scaled, y_train)

# Прогнозування на тестовій вибірці
y_pred = model.predict(X_test_scaled)

# Оцінка точності моделі
accuracy = accuracy_score(y_test, y_pred)
print(f"\nТочність моделі: {accuracy:.2f}")

# Матриця плутанини
conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues")
plt.title("Матриця плутанини")
plt.xlabel("Прогнозовані значення")
plt.ylabel("Фактичні значення")
plt.savefig("confusion_matrix.png")
plt.show()

# Звіт про класифікацію
print("\nЗвіт про класифікацію:")
print(classification_report(y_test, y_pred))

# 8. Збереження результатів
results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
results.to_csv("prediction_results.csv", index=False)

# Збереження важливих характеристик моделі
model_coef = pd.DataFrame(
    {"Feature": important_features, "Coefficient": model.coef_[0]}
)
model_coef.to_csv("model_coefficients.csv", index=False)

print("\nАналіз завершено. Результати збережено у файлах.")
