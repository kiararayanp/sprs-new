# Student Result Prediction System (SRPS)

A Django-based web application that predicts student performance using historical academic data. The system incorporates secure access, intuitive interfaces, and data analytics to assist educators and administrators in making informed decisions.

## Features
- **Multiple User Roles**: Supports role-based access for Admin, Teachers, and Students.
- **Result Prediction**: Employs Multiple Linear Regression (MLR) for accurate performance forecasting.
- **User Verification**: Ensures secure access with admin-based user verification.
- **Task Management**: Teachers can assign, manage, and evaluate tasks for students.
- **Attendance and Results**: Allows tracking of attendance and academic results.


## Technologies Used
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Python, Django
- **Database**: MySQL
- **Development Tools**: Django Development Server, draw.io for diagrams

## Prerequisites

Ensure you have the following installed:

- Python (version 3.8 or higher)

- Git (for version control)

- MySql

## Installation Steps

Follow these steps to get the project up and running:

### Cloning the Repository

First, clone the repository from GitHub:

```bash
git clone <current repo link>
```

### Setup Project Dependencies

Install project dependencies

```
pip install -r requirements.txt
```

Setup the mysql database named test_classroom and run the following command

```
python manage.py makemigrations
python manage.py migrate
```

### Run the development server

```
python manage.py runserver
```

### To visit the Django admin pannel

```
First create super user with your email and password  : py manage.py createsuperuser
Then vist the url : http://127.0.0.1:8000/admin
```

### Some command may differ if you are using operating system other than windows.


