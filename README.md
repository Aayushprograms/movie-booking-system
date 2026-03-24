# 🎬 Movie Booking System

A Django-based Movie Booking System with advanced analytics dashboard, concurrency-safe seat reservation, and real-time data visualization.

---

## 🚀 Features

### 🎥 Movie Management
- Filter movies by language and genre
- Sort by rating and release date
- Pagination for large datasets
- Movie detail page with trailer support

---

### 💺 Seat Booking System
- Concurrency-safe seat reservation using database locking
- Prevents double booking
- Automatic seat release after timeout
- Handles edge cases (network issues, app close)

---

### 💳 Payment Integration
- Simulated Razorpay payment system
- Idempotency support to prevent duplicate payments
- Secure payment verification

---

### 🔔 Webhook Handling
- Secure webhook endpoint
- Signature verification
- Duplicate event prevention

---

### 📊 Admin Analytics Dashboard
- Daily, Weekly, Monthly Revenue
- Most Popular Movies
- Peak Booking Hours
- Busiest Movies (Seat Occupancy)
- Cancellation Rate
- Interactive charts using Chart.js

---

### ⚡ Performance Optimization
- Database-level aggregation (annotate, aggregate)
- Indexed queries for scalability
- Caching (Redis / in-memory) to reduce DB load

---

### 🔐 Security
- Role-based admin access
- Django authentication system
- Secure password hashing

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **Caching:** Redis / LocMemCache
- **Frontend:** HTML, CSS, Chart.js
- **API:** TMDB (Movie Data)

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/Aayushprograms/movie-booking-system.git
cd movie-booking-system