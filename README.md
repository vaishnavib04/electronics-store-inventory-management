# Electronics Store Inventory Management System (ESIMS)

## Overview

The Electronics Store Inventory Management System (ESIMS) is a web-based application designed to manage the products, inventory, suppliers, purchases, and sales of an electronics store. It aims to simplify stock tracking, maintain accurate inventory records, and support efficient store operations.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **ORM:** Flask-SQLAlchemy
- **Database Driver:** PyMySQL
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** pytest
- **Version Control:** Git and GitHub
- **Continuous Integration:** GitHub Actions

## Planned Features

- Role-based access control
- Product and category management screens
- Purchase and sales transaction management
- Stock movement history
- Inventory and sales reports

## Sprint 1 Demonstration

The Sprint 1 working product demonstration is available here:

[Watch the Sprint 1 demonstration](./sprint_videos/sprint1_demo.mp4)

Sprint 1 currently includes:

- User login, logout, and protected dashboard
- Inventory listing and search by product name or SKU
- Low-stock reporting
- Supplier listing, creation, and editing
- Database models, validation, and automated tests

## Repository Structure

```text
electronics-store-inventory-management/
├── SRS/
├── Software_Architecture_and_Design_Specification/
├── Software_Test_Plan/
├── app/
│   ├── auth/
│   ├── products/
│   ├── inventory/
│   ├── suppliers/
│   ├── purchases/
│   ├── sales/
│   ├── reports/
│   ├── templates/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── __init__.py
│   ├── extensions.py
│   └── models.py
├── tests/
├── sprint_videos/
│   └── sprint1_demo.mp4
├── .github/
│   └── workflows/
├── .env                  # Local configuration; not committed
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

The application folders and files are being developed incrementally.

## Prerequisites

- Python installed
- MySQL Server installed and running
- Git installed
- Visual Studio Code or another code editor

## Setup Instructions

### 1. Clone the repository

```powershell
git clone https://github.com/vaishnavib04/electronics-store-inventory-management.git
cd electronics-store-inventory-management
```

### 2. Create and activate a virtual environment

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 4. Configure the database

Create a MySQL database named `esims_db`, or use the database name agreed upon by the team.

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-random-secret
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/esims_db
```

Replace `YOUR_PASSWORD` with your MySQL password. URL-encode special characters in the password when required.

**Security:** Never commit `.env` or expose database credentials in the repository.

### 5. Run the application

Ensure the database configuration is correct, then run:

```powershell
py run.py
```

Open `http://127.0.0.1:5000` in your browser.

### 6. Run tests

```powershell
py -m pytest -v
```

## Development Workflow

1. Pull the latest changes from the shared repository.
2. Work on an assigned GitHub issue.
3. Create a separate branch for the task.
4. Implement the changes and run relevant tests.
5. Push the branch and open a pull request.
6. Review and merge changes after the required checks pass.

## Project Status

Sprint 1 is complete with working authentication, inventory, low-stock reporting, supplier management, database models, automated tests, and continuous integration. Additional product, purchase, sales, reporting, and role-based access-control features are planned for future sprints.