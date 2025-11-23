# School Timetable — Server (Flask)

**Project**: Automated School Timetabling System  
**Author**: (Your name)  
**Purpose**: Generate realistic, conflict-free timetables for classes and teachers, exportable to PDF/Excel, with admin UI and API.

---

## Features (realistic / production-minded)
- Admin panel: manage schools, classes, subjects, teachers, rooms, and periods.
- Import/export: Excel import/export of teachers, subjects, class-subject assignments.
- Auto-generator: constraints-aware scheduler that creates:
  - Class timetables (per class / grade)
  - Teacher timetables (per teacher)
  - Room allocations
- Constraints supported:
  - Max periods per teacher per day/week
  - Subject-specific number of periods per week per class
  - Room capacity and room-type constraints (lab / lecture)
  - Blackout times (teacher unavailable)
  - Consecutive period rules and break placement
  - Priority ordering (e.g., core subjects first)
- Outputs: printable PDF (xhtml2pdf), Excel (openpyxl), and JSON API.
- Auth: simple admin user (Flask-Login).
- Dockerized (MySQL) and easy local setup.

---

## Quickstart (development)

1. Copy `.env.example` → `.env` and edit.
2. Build & run with Docker:
   ```bash
   docker-compose up --build
