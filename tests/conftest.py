"""Shared fixtures for eco-code-analyzer tests."""

import pytest


@pytest.fixture
def sample_efficient_code():
    return '''
result = [item * 2 for item in range(100)]
total = sum(x for x in result if x > 10)
found = any(x > 50 for x in result)

with open("test.txt", "r") as f:
    data = f.read()
'''


@pytest.fixture
def sample_inefficient_code():
    return '''
result = []
for item in range(100):
    result.append(item * 2)

total = 0
for x in result:
    if x > 10:
        total += x

f = open("test.txt", "r")
data = f.read()
f.close()

global_data = {}

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''


@pytest.fixture
def sample_io_heavy_code():
    return '''
import requests

results = []
for user_id in range(100):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    results.append(response.json())

for item in items:
    with open("output.txt", "w") as f:
        f.write(str(item))
'''


@pytest.fixture
def sample_nested_loops():
    return '''
for i in range(n):
    for j in range(n):
        for k in range(n):
            matrix[i][j] += a[i][k] * b[k][j]
'''


@pytest.fixture
def sample_empty_code():
    return ''


@pytest.fixture
def sample_syntax_error():
    return 'def broken(:\n    pass'
