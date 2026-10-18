# Electronics Store Inventory Management System (ESIMS)

## Overview

The Electronics Store Inventory Management System (ESIMS) is a web-based application designed to help manage an electronics store's products, inventory, suppliers, purchases, sales, and reports.

The system aims to maintain accurate stock records, prevent invalid inventory updates, identify low-stock products, and provide useful inventory and sales information.

## Technology Stack

- **Backend:** Python and Flask
- **Frontend:** HTML, CSS, Bootstrap, and Jinja templates
- **Database:** MySQL
- **Database access:** SQLAlchemy ORM
- **Authentication:** Flask sessions and password hashing
- **Testing:** pytest
- **Version control and collaboration:** Git and GitHub
- **Project tracking:** GitHub Projects and GitHub Issues
- **Automation:** GitHub Actions

## Planned Features

- User login and logout
- Product creation, viewing, updating, and searching
- Unique SKU validation
- Stock quantity tracking and low-stock alerts
- Prevention of negative inventory
- Supplier management
- Purchase recording and stock updates
- Sales recording and stock updates
- Inventory reports
- Date-range sales reports

## Project Structure

```text
electronics-store-inventory-management/
│
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   │
│   ├── auth/
│   │   └── routes.py
│   ├── products/
│   │   └── routes.py
│   ├── inventory/
│   │   └── routes.py
│   ├── suppliers/
│   │   └── routes.py
│   ├── purchases/
│   │   └── routes.py
│   ├── sales/
│   │   └── routes.py
│   ├── reports/
│   │   └── routes.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── products/
│   │   ├── inventory/
│   │   ├── suppliers/
│   │   ├── purchases/
│   │   ├── sales/
│   │   └── reports/
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── tests/
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
└── README.md
```

Files and folders will be added as the corresponding features are implemented.

## Prerequisites

- Python 3
- MySQL Server
- Git
- A code editor such as Visual Studio Code

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd ESIMS
   ```

2. Create and activate a Python virtual environment:

   **Windows:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the MySQL database using the database name and configuration documented by the project.

5. Configure the required environment variables using `.env.example` as a reference. Do not commit actual credentials.

6. Start the application using the run instructions implemented in `app.py`.

## Running Tests

Run the automated tests from the project root:

```bash
pytest
```

## Development Workflow

1. Select an issue from the GitHub Project board.
2. Create a feature branch.
3. Implement the feature and add relevant tests.
4. Commit and push your changes.
5. Open a pull request linked to the relevant issue.
6. Request a review and ensure required GitHub Actions checks pass.
7. Merge the approved pull request into the main branch.

## Project Scope

ESIMS focuses on internal electronics-store inventory operations. Online shopping, online payments, delivery management, and advanced accounting are outside the planned scope.

## Project Status

The project is in the setup and planning stage. Features will be implemented incrementally across the planned sprints.