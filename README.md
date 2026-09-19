# HelpDesk Ticketing System


A simple Flask-based helpdesk ticketing system for managing internal support requests.


## Overview


This system supports a realistic helpdesk workflow:


- Employees create tickets
- ICT staff take and resolve tickets
- Procurement reviews purchase approvals
- The original reporter can confirm and close the ticket after resolution


## Features


- User login
- Role-based access
- Ticket creation
- Ticket assignment
- Procurement approval workflow
- Ticket status tracking
- SQLite database
- Bootstrap-based interface


## Project Structure


```text
helpdesk/
├── app.py
├── requirements.txt
├── README.md
└── templates/
    ├── login.html
    ├── create.html
    └── index.html
```


## Demo Users


| Username | Password | Role | Department |
|----------|----------|------|------------|
| admin | admin123 | admin | ICT |
| ict | ict123 | ict | ICT |
| hr | hr123 | employee | HR |
| finance | finance123 | employee | Finance |
| procurement | procurement123 | procurement | Procurement |


## Installation


1. Create a folder:
   ```bash
   mkdir helpdesk
   cd helpdesk
   ```


2. Create these files:
   - app.py
   - requirements.txt
   - templates/login.html
   - templates/create.html
   - templates/index.html


3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


4. Run the application:
   ```bash
   python app.py
   ```


5. Open in the browser:
   ```text
   http://127.0.0.1:5000/login
   ```


## Workflow


1. An employee creates a ticket.
2. ICT takes the ticket.
3. If a purchase is needed, ICT requests approval.
4. Procurement approves or rejects the request.
5. ICT resolves the issue.
6. The reporter closes the ticket after confirmation.


## Technologies Used


- Flask
- Flask-SQLAlchemy
- SQLite
- Bootstrap 5


## Notes


This project is intended for learning and demo purposes. It is not production-ready for real enterprise use without additional security improvements such as:


- proper database-backed user management
- password reset features
- CSRF protection
- stronger authorization checks
- audit logging
- production deployment hardening


## License


This project is provided for educational and demonstration purposes.
```