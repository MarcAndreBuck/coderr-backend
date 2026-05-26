
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

# Coderr Backend API

Backend API for Coderr, a Fiverr-like freelance marketplace built with Django and Django REST Framework as part of the Developer Akademie backend course.

The project includes:

- User authentication
- Profile management
- Offers with multiple pricing tiers
- Orders system
- Reviews system
- Platform statistics endpoint
- Token authentication
- Comprehensive automated tests


# Tech Stack

## Environment Variables

Create a `.env` file in the project root if you want to override default settings (optional):

```env
# Example:
DEBUG=True
SECRET_KEY=your-secret-key
```

- Python
- Django
- Django REST Framework
- SQLite
- DRF Token Authentication
- Pillow

---

# Features

## Authentication

- User registration
- User login
- Token authentication

## Profiles

- Customer profiles
- Business profiles
- Public profile access
- Owner-only profile editing

## Offers

- Create offers as business user
- Multiple offer details (Basic / Standard / Premium)
- Update offers
- Delete offers
- Public offer access

## Orders

- Customers can create orders
- Businesses can update order status
- Staff users can delete orders
- Order statistics endpoints

## Reviews

- Customers can review businesses
- Only customers with completed orders can review
- One review per customer per business
- Review update and delete permissions

## Base Info

- Platform statistics endpoint
- Review count
- Average rating
- Business profile count
- Offer count

---

# Installation

## Clone repository

```bash
git clone <your-repository-url>
cd coderr-backend
```

## Create virtual environment

```bash
python -m venv venv
```

## Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS


```bash
source venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Database Setup

## Run migrations

```bash
python manage.py migrate
```

## Create superuser (optional)

```bash
python manage.py createsuperuser
```

---

# Start Development Server

```bash
python manage.py runserver
```

Server runs on:

```text
http://127.0.0.1:8000/
```

---

# API Endpoints

## Example Requests

### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/registration/ \
	-H "Content-Type: application/json" \
	-d '{"username": "testuser", "email": "test@example.com", "password": "TestPassword123!", "repeated_password": "TestPassword123!", "type": "customer"}'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
	-H "Content-Type: application/json" \
	-d '{"username": "testuser", "password": "TestPassword123!"}'
```

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/registration/` | Register user |
| POST | `/api/login/` | Login user |

---

## Profiles

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/profile/<id>/` | Get profile |
| PATCH | `/api/profile/<id>/` | Update own profile |

---

## Offers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/offers/` | List offers |
| POST | `/api/offers/` | Create offer |
| GET | `/api/offers/<id>/` | Offer detail |
| PATCH | `/api/offers/<id>/` | Update own offer |
| DELETE | `/api/offers/<id>/` | Delete own offer |

---

## Orders

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/orders/` | List user orders |
| POST | `/api/orders/` | Create order |
| PATCH | `/api/orders/<id>/` | Update order status |
| DELETE | `/api/orders/<id>/` | Delete order |
| GET | `/api/order-count/<business_user_id>/` | Active order count |
| GET | `/api/completed-order-count/<business_user_id>/` | Completed order count |

---

## Reviews

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reviews/` | List reviews |
| POST | `/api/reviews/` | Create review |
| PATCH | `/api/reviews/<id>/` | Update own review |
| DELETE | `/api/reviews/<id>/` | Delete own review |

---

## Base Info

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/base-info/` | Platform statistics |

---

# Running Tests

## Run all tests

```bash
python manage.py test
```

## Run coverage

```bash
coverage run manage.py test
coverage report
```

---

# Test Coverage

Current project coverage:

```text
98%
```

---

# Permissions Overview

---

# Media & Uploads

Uploaded files (z.B. Profilbilder, Angebotsbilder) werden im Ordner `uploads/` bzw. `offer_images/` gespeichert. Stelle sicher, dass dieser Ordner im Deployment existiert und beschreibbar ist.

## Profiles

- Everyone can view profiles
- Only owners can edit profiles

## Offers

- Everyone can view offers
- Only business users can create offers
- Only owners can edit/delete offers

## Orders

- Customers can create orders
- Businesses can update order status
- Only staff users can delete orders

## Reviews

- Only customers can create reviews
- Only customers with completed orders can review
- Only reviewers can edit/delete reviews

---

# Author

Marc-André Buck

---

# Contribution

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

