import numpy as np

X = np.array(
    [
        [0, 0, 0, 0],  
        [0, 0, 0, 1],  
        [0, 1, 0, 0],  
        [0, 1, 1, 1],
        [1, 0, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 1, 0],
        [1, 1, 1, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],  
        [1, 0, 0, 0],  
        [1, 1, 0, 1],  
    ]
)

y = np.array(
    [
        [0.9],  
        [0.8],
        [0.7],
        [0.6],
        [0.5],
        [0.6],
        [0.7],
        [0.8],
        [0.7],
        [0.8],
        [0.6],
        [0.9],
    ]
)

input_neurons = 4
hidden_neurons = 3
output_neurons = 1

weights_input_hidden = np.random.uniform(size=(input_neurons, hidden_neurons))
weights_hidden_output = np.random.uniform(size=(hidden_neurons, output_neurons))


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


learning_rate = 0.1
epochs = 10000

for epoch in range(epochs):
    hidden_layer_input = np.dot(X, weights_input_hidden)
    hidden_layer_output = sigmoid(hidden_layer_input)
    output_layer_input = np.dot(hidden_layer_output, weights_hidden_output)
    output_layer_output = sigmoid(output_layer_input)

    output_error = y - output_layer_output
    output_delta = output_error * (output_layer_output * (1 - output_layer_output))
    hidden_layer_error = output_delta.dot(weights_hidden_output.T)
    hidden_layer_delta = hidden_layer_error * (
        hidden_layer_output * (1 - hidden_layer_output)
    )

    weights_hidden_output += hidden_layer_output.T.dot(output_delta) * learning_rate
    weights_input_hidden += X.T.dot(hidden_layer_delta) * learning_rate

test_X = np.array(
    [
        [0, 1, 1, 0],  
        [1, 0, 0, 1],  
    ]
)

hidden_layer_input_test = np.dot(test_X, weights_input_hidden)
hidden_layer_output_test = sigmoid(hidden_layer_input_test)
output_layer_input_test = np.dot(hidden_layer_output_test, weights_hidden_output)
output_layer_output_test = sigmoid(output_layer_input_test)

print("Результати тестування:")
print(output_layer_output_test)
