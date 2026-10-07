# Web Calculator Backend

Software Engineering Practice - Assignment 1

## Project Description

This project is the backend service of a web calculator.

The backend is implemented with FastAPI and SQLite.

## Features

- Basic arithmetic operations
- Parentheses
- Decimal numbers
- Negative numbers
- Expression validation
- Division-by-zero handling
- Calculation history
- Delete history records
- SQLite persistent storage
- RESTful API

## Technology Stack

- Python
- FastAPI
- SQLite
- Uvicorn

## API

### Calculate

POST `/api/calculate`

Example request:

```json
{
  "expression": "(1+2)*3"
}