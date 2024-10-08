# Project Overview

This project is a user authentication and friend request API service. It provides endpoints for user signup, login, user search, and sending friend requests. The APIs are designed to be secure and efficient, with features like case-insensitive email validation, authentication requirements, pagination, and rate limiting.

# Installation Steps

## Prerequisites
- Python 3.8 or higher
- Docker 

## Run Via Docker
  ```
  docker-compose build
  docker-compose up
  ```

## Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/skmadridista/accuknox_proj.git
   cd accuknox_proj
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Start the server:**
   ```bash
   python manage.py runserver
   ```

# API Documentation

## Signup
- **Endpoint**: `/api/userAuth/signup/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User created successfully",
    "user_id": 1
  }
  ```

## Login
- **Endpoint**: `/api/userAuth/login/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "token": "your_auth_token"
  }
  ```

## User Search
- **Endpoint**: `/api/userAuth/search/`
- **Method**: GET
- **Query Parameters**:
  - `page`: Page number for pagination (default: 1)
  - `limit`: Number of users per page (default: 10)
- **Response**:
  ```json
  {
    "users": [
      {
        "id": 1,
        "email": "user1@example.com"
      },
      {
        "id": 2,
        "email": "user2@example.com"
      }
    ],
    "page": 1,
    "total_pages": 5
  }
  ```

## Send Friend Request
- **Endpoint**: `/api/userAuth/friend-request/send/<int:user_id>/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "to_user_id": 2
  }
  ```
- **Response**:
  ```json
  {
    "message": "Friend request sent successfully"
  }
## Accept Friend Request
- **Endpoint**: `/api/userAuth/friend-request/accept/<int:request_id>/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "to_user_id": 2
  }
  ```
- **Response**:
  ```json
  {
    "message": "Friend request accepted successfully"
  }
  ```
## Reject Friend Request
- **Endpoint**: `/api/userAuth/reject_request/<int:request_id>/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "to_user_id": 2
  }
  ```
- **Response**:
  ```json
  {
    "message": "Friend request rejected"
  }
  ```
```
