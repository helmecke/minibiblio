-- Library Management System Database Schema

-- Readers table (Leserverzeichnis)
CREATE TABLE IF NOT EXISTS readers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone TEXT NOT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_number TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    isbn TEXT,
    publication_year INTEGER,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Loans table (tracks borrowing and returns)
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT DEFAULT 'borrowed' CHECK (status IN ('borrowed', 'returned')),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reader_id) REFERENCES readers (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);

-- Audit log table (tracks all loan-related activities)
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER,
    reader_id INTEGER,
    book_id INTEGER,
    action TEXT NOT NULL CHECK (action IN ('checkout', 'return', 'extend', 'delete')),
    description TEXT NOT NULL,
    old_values TEXT,  -- JSON string of old values
    new_values TEXT,  -- JSON string of new values
    user_info TEXT,   -- Information about who performed the action
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (loan_id) REFERENCES loans (id),
    FOREIGN KEY (reader_id) REFERENCES readers (id),
    FOREIGN KEY (book_id) REFERENCES books (id)
);

-- Indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_readers_name ON readers (name);
CREATE INDEX IF NOT EXISTS idx_readers_number ON readers (reader_number);
CREATE INDEX IF NOT EXISTS idx_books_title ON books (title);
CREATE INDEX IF NOT EXISTS idx_books_number ON books (book_number);
CREATE INDEX IF NOT EXISTS idx_loans_reader_id ON loans (reader_id);
CREATE INDEX IF NOT EXISTS idx_loans_book_id ON loans (book_id);
CREATE INDEX IF NOT EXISTS idx_loans_status ON loans (status);
CREATE INDEX IF NOT EXISTS idx_audit_log_loan_id ON audit_log (loan_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log (action);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log (timestamp);