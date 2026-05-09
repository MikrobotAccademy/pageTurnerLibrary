# 📚 PageTurner Library System

> **Welcome to your first day.**
>
> Your predecessor, Jordan, built this library management system for a small
> local library. Jordan is no longer with us. Nobody will say why.
>
> What Jordan left behind: a half-working Python application, zero inline
> comments, and a sticky note on the monitor that read *"it mostly works"*.
>
> Your job is to make it **actually** work.

---

## What the App Does

PageTurner is a command-line tool for library staff to:

- Maintain a catalogue of books (add, remove, search)
- Check books in and out to borrowers
- Track due dates and flag overdue returns
- Persist all data to disk between sessions
- View borrowing statistics

## Project Structure

```
librarymanager/
├── library.py                  # The application (the crime scene)
├── tests/
│   └── test_library.py         # Test suite — several tests fail on purpose
├── data/                       # Created automatically when you save
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/<instructor>/pageturner-library.git
cd pageturner-library
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python library.py
```

### 5. Run the tests

```bash
python -m pytest tests/ -v
```

Several tests fail right away. That's normal. Your job is to fix the bugs that
make them fail.

---

## How Fixes Are Submitted

1. **Claim an issue** — comment on it so classmates know it's taken.
2. **Create a branch** named after the issue:
   ```bash
   git checkout -b fix/issue-2-classmethod
   ```
3. **Fix the bug** — keep changes targeted. Don't rewrite the whole file.
4. **Verify** the relevant test now passes.
5. **Commit** with a message that references the issue number:
   ```bash
   git commit -m "Fix #2: add @classmethod decorator to Book.from_dict"
   ```
6. **Open a Pull Request** → your instructor reviews and merges → points awarded.

---

## Points

| Difficulty | Points |
|------------|--------|
| 🟢 Easy    | 5 pts  |
| 🟡 Medium  | 10 pts |
| 🔴 Hard    | 15 pts |

Points go to the **first correct PR** that closes the issue.

---

*"It mostly works." — Jordan, former employee*
