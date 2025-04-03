import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def neuron_output(x1, x2, x3, w1, w2, w3, b):
    z = w1 * x1 + w2 * x2 + w3 * x3 + b
    return sigmoid(z)


# Приклад використання
x1 = 1  # Середній розмір
x2 = 0  # Шкіра
x3 = 1  # Сучасний стиль
w1 = 0.2
w2 = -0.1
w3 = 0.3
b = -0.5

output = neuron_output(x1, x2, x3, w1, w2, w3, b)
print("Вихід нейрона:", output)

# Навчальні дані
X = np.array(
    [
        [0, 0, 0],  # Мала шкіряна класична
        [1, 0, 1],  # Середня шкіряна сучасна
        [2, 1, 2],  # Велика текстильна вінтажна
        [0, 2, 1],  # Мала замшева сучасна
        [1, 1, 0],  # Середня текстильна класична
        [2, 0, 2],  # Велика шкіряна вінтажна
    ]
)

y = np.array([[0], [1], [2], [0], [1], [2]])  # Класи сумок

# Ініціалізація вагових коефіцієнтів
input_neurons = 3
hidden_neurons = 4
output_neurons = 3

weights_input_hidden = np.random.uniform(size=(input_neurons, hidden_neurons))
weights_hidden_output = np.random.uniform(size=(hidden_neurons, output_neurons))

# Навчання
learning_rate = 0.1
epochs = 10000

for epoch in range(epochs):
    # Пряме поширення
    hidden_layer_input = np.dot(X, weights_input_hidden)
    hidden_layer_output = sigmoid(hidden_layer_input)
    output_layer_input = np.dot(hidden_layer_output, weights_hidden_output)
    output_layer_output = sigmoid(output_layer_input)

    # Зворотне поширення
    output_error = y - output_layer_output
    output_delta = output_error * (output_layer_output * (1 - output_layer_output))
    hidden_layer_error = output_delta.dot(weights_hidden_output.T)
    hidden_layer_delta = hidden_layer_error * (
        hidden_layer_output * (1 - hidden_layer_output)
    )

    # Оновлення вагових коефіцієнтів
    weights_hidden_output += hidden_layer_output.T.dot(output_delta) * learning_rate
    weights_input_hidden += X.T.dot(hidden_layer_delta) * learning_rate

# Виведення вагових коефіцієнтів
print("Вагові коефіцієнти (вхідний-прихований шар):")
print(weights_input_hidden)
print("\nВагові коефіцієнти (прихований-вихідний шар):")
print(weights_hidden_output)

# Тестові дані
test_X = np.array([[0, 1, 0], [1, 2, 1], [2, 0, 1]])

# Прогноз
hidden_layer_input_test = np.dot(test_X, weights_input_hidden)
hidden_layer_output_test = sigmoid(hidden_layer_input_test)
output_layer_input_test = np.dot(hidden_layer_output_test, weights_hidden_output)
output_layer_output_test = sigmoid(output_layer_input_test)

print("\nРезультати тестування:")
print(output_layer_output_test)

# Середньоквадратична помилка (MSE)
mse = np.mean((y - output_layer_output) ** 2)
print("\nMSE:", mse)

import json

results = {
    "weights_input_hidden": weights_input_hidden.tolist(),
    "weights_hidden_output": weights_hidden_output.tolist(),
    "test_results": output_layer_output_test.tolist(),
    "mse": mse,
}

with open("neural_network_results_2.json", "w") as f:
    json.dump(results, f)

print("\nРезультати збережено у файл neural_network_results.json")
