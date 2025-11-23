-- mysql -u username -p school_timetable_db < schema.sql

-- -- schema.sql
-- -- MySQL dialect

USE school_timetable_db;

-- create schools table if missing (safe)
class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    timezone = db.Column(db.String(255), default="Africa/Dar_es_Salaam")
    created_at = db.Column(db.DateTime, default=func.now())


-- add school_id to users if missing
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS school_id INT NULL,
  ADD FOREIGN KEY IF NOT EXISTS (school_id) REFERENCES schools(id) ON DELETE SET NULL;


-- UPDATE: set existing rows to school_id = 1 (Maahad Istiqama) if you are single-school.
-- **Only run this if you are sure** and you have school id 1:
UPDATE schools SET name = 'Maahad Istiqama' WHERE id = 1;
-- set users.school_id (for pre-existing accounts) if NULL
UPDATE users SET school_id = 1 WHERE school_id IS NULL;
-- set teachers.school_id default to 1 if NULL
UPDATE teachers SET school_id = 1 WHERE school_id IS NULL;
-- set subjects.school_id default to 1 if NULL
UPDATE subjects SET school_id = 1 WHERE school_id IS NULL;
-- set rooms.school_id default to 1 if NULL
UPDATE rooms SET school_id = 1 WHERE room_id IS NULL;


INSERT INTO schools (name, timezone) VALUES ('Maahad Istiqama','Africa/Dar_es_Salaam');

CREATE TABLE education_levels (
  id INT AUTO_INCREMENT PRIMARY KEY,
  school_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  level_type ENUM('nursery', 'lower_primary', 'upper_primary', 'secondary') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB;


CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  school_id INT NOT NULL,
  name VARCHAR(150) NOT NULL,
  code VARCHAR(10) NOT NULL,
  subject_type ENUM('core', 'elective', 'practical', 'lab') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE subject_level_assignments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  subject_id INT NOT NULL,
  education_level_id INT NOT NULL,
  periods_per_week INT NOT NULL,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  FOREIGN KEY (education_level_id) REFERENCES education_levels(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE teachers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  school_id INT NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100) NOT NULL,
  email VARCHAR(255),
  qualification ENUM('Nursery', 'Lower pimary', 'Upper primary', 'Secondary') NOT NULL,
  max_periods_per_day INT DEFAULT 6,
  max_periods_per_week INT DEFAULT 30,
  FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE teacher_subject_qualifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  teacher_id INT NOT NULL,
  subject_id INT NOT NULL,
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE classes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  school_id INT NOT NULL,
  education_level_id INT NOT NULL,
  name VARCHAR(50) NOT NULL,
  assigned_teacher_id INT,
  FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
  FOREIGN KEY (education_level_id) REFERENCES education_levels(id) ON DELETE CASCADE,
  FOREIGN KEY (assigned_teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE rooms (
  id INT AUTO_INCREMENT PRIMARY KEY,
  school_id INT NOT NULL,
  name VARCHAR(50) NOT NULL,
  capacity INT,
  FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE class_subject_assignments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  class_id INT NOT NULL,
  subject_id INT NOT NULL,
  teacher_id INT NOT NULL,
  FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE timetables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  class_subject_assignment_id INT NOT NULL,
  room_id INT NOT NULL,
  day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  FOREIGN KEY (class_subject_assignment_id) REFERENCES class_subject_assignments(id) ON DELETE CASCADE,
  FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
) ENGINE=InnoDB;




-- Education Levels
INSERT INTO education_levels (id, school_id, name, level_type)
VALUES
(1, 1, 'Nursery', 'nursery'),

(2, 1, 'Standard 1A', 'lower_primary'),
(3, 1, 'Standard 1B', 'lower_primary'),
(4, 1, 'Standard 2A', 'lower_primary'),
(5, 1, 'Standard 2B', 'lower_primary'),
(6, 1, 'Standard 3A', 'lower_primary'),
(7, 1, 'Standard 3B', 'lower_primary'),

(8, 1, 'Standard 4A', 'upper_primary'),
(9, 1, 'Standard 4B', 'upper_primary'),
(10, 1, 'Standard 5A', 'upper_primary'),
(11, 1, 'Standard 5B', 'upper_primary'),
(12, 1, 'Standard 6A', 'upper_primary'),
(13, 1, 'Standard 6B', 'upper_primary'),
(14, 1, 'Standard 7A', 'upper_primary'),
(15, 1, 'Standard 7B', 'upper_primary'),

(16, 1, 'Form 1A', 'secondary'),
(17, 1, 'Form 1B', 'secondary'),
(18, 1, 'Form 2A', 'secondary'),
(19, 1, 'Form 2B', 'secondary'),
(20, 1, 'Form 3A', 'secondary'),
(21, 1, 'Form 3B', 'secondary'),
(22, 1, 'Form 4A', 'secondary'),
(23, 1, 'Form 4B', 'secondary');


INSERT INTO subjects (id, school_id, name, code, subject_type)
VALUES
(1, 1, 'Play Activities', 'PLAY', 'practical'),
(2, 1, 'Basic Literacy', 'BLIT', 'core'),
(3, 1, 'Basic Numeracy', 'BNUM', 'core'),

(4, 1, 'English', 'ENG', 'core'),
(5, 1, 'Mathematics', 'MATH', 'core'),
(6, 1, 'Kiswahili', 'KSW', 'core'),
(7, 1, 'Science', 'SCI', 'core'),
(8, 1, 'Civics', 'CVC', 'core'),
(9, 1, 'Social Studies', 'SST', 'core'),

(10, 1, 'Biology', 'BIO', 'lab'),
(11, 1, 'Chemistry', 'CHEM', 'lab'),
(12, 1, 'Physics', 'PHY', 'lab'),
(13, 1, 'Geography', 'GEO', 'core'),
(14, 1, 'History', 'HIST', 'core'),
(15, 1, 'Commerce', 'COM', 'elective'),
(16, 1, 'Bookkeeping', 'BK', 'elective'),
(17, 1, 'Computer Studies', 'COMP', 'elective');


INSERT INTO subject_level_assignments (subject_id, education_level_id, periods_per_week)
VALUES
-- Nursery
(1, 1, 6), (2, 1, 5), (3, 1, 5),

-- Standard 1–7 (core subjects)
(4, 2, 5), (5, 2, 5), (6, 2, 5), (7, 2, 4), (8, 2, 3), (9, 2, 3),
(4, 3, 5), (5, 3, 5), (6, 3, 5), (7, 3, 4), (8, 3, 3), (9, 3, 3),
-- repeat for Standard 2A–7B
(4, 4, 5), (5, 4, 5), (6, 4, 5), (7, 4, 4), (8, 4, 3), (9, 4, 3),
(4, 5, 5), (5, 5, 5), (6, 5, 5), (7, 5, 4), (8, 5, 3), (9, 5, 3),
-- ... continue for levels 6 to 15

-- Secondary (Form 1A–4B)
(4, 16, 5), (5, 16, 5), (6, 16, 4), (10, 16, 4), (11, 16, 4), (12, 16, 4), (13, 16, 4), (14, 16, 3), (8, 16, 3), (15, 16, 2), (16, 16, 2), (17, 16, 2),
-- repeat for Form 1B - 4B
(4, 17, 5), (5, 17, 5), (6, 17, 4), (10, 17, 4), (11, 17, 4), (12, 17, 4), (13, 17, 4), (14, 17, 3), (8, 17, 3), (15, 17, 2), (16, 17, 2), (17, 17, 2);


INSERT INTO teacher_subject_qualifications (teacher_id, subject_id)
VALUES
-- Nursery teacher
(1, 1), (1, 2), (1, 3),

-- Lower primary teacher
(2, 4), (2, 5), (2, 6), (2, 7),

-- Upper primary teacher
(3, 4), (3, 5), (3, 6), (3, 7), (3, 9),

-- Secondary teachers
(4, 4), (4, 5), (4, 10), (4, 11), (4, 12),
(5, 13), (5, 14), (5, 15), (5, 16), (5, 17);


INSERT INTO classes (id, school_id, name, education_level_id, assigned_teacher_id)
VALUES
(1, 1, 'Nursery', 1, 1),

(2, 1, 'Standard 1A', 2, 2),
(3, 1, 'Standard 1B', 3, 3),
(4, 1, 'Standard 2A', 4, 2),
(5, 1, 'Standard 2B', 5, 3),
(6, 1, 'Standard 3A', 6, 2),
(7, 1, 'Standard 3B', 7, 3),

(8, 1, 'Standard 4A', 8, 4),
(9, 1, 'Standard 4B', 9, 5),
(10, 1, 'Standard 5A', 10, 4),
(11, 1, 'Standard 5B', 11, 5),
(12, 1, 'Standard 6A', 12, 6),
(13, 1, 'Standard 6B', 13, 6),
(14, 1, 'Standard 7A', 14, 4),
(15, 1, 'Standard 7B', 15, 5),

(16, 1, 'Form 1A', 16, 7),
(17, 1, 'Form 1B', 17, 8),
(18, 1, 'Form 2A', 18, 9),
(19, 1, 'Form 2B', 19, 10),
(20, 1, 'Form 3A', 20, 11),
(21, 1, 'Form 3B', 21, 12),
(22, 1, 'Form 4A', 22, 7),
(23, 1, 'Form 4B', 23, 8);


INSERT INTO rooms (id, school_id, name, capacity)
VALUES
(1, 1, 'Room A', 30),
(2, 1, 'Room B', 35),
(3, 1, 'Science Lab', 25),
(4, 1, 'Computer Lab', 20);


INSERT INTO class_subject_assignments (class_id, subject_id, teacher_id)
VALUES
(1, 1, 1), (1, 2, 1), (1, 3, 1),

-- Standard 1A
(2, 4, 2), (2, 5, 2), (2, 6, 2), (2, 7, 2),

-- Form 1A
(4, 4, 4), (4, 5, 4), (4, 10, 4), (4, 11, 4), (4, 12, 4),
(5, 13, 5), (5, 14, 5), (5, 15, 5), (5, 16, 5), (5, 17, 5);

INSERT INTO teachers (id, first_name, last_name, email, max_periods_per_day, max_periods_per_week, school_id, qualification)
VALUES
(1, 'Asha', 'Nuru', 'asha.nuru@example.com', 4, 20, 1, 'Nursery'),
(2, 'John', 'Michael', 'john.michael@example.com', 5, 25, 1, 'Lower primary'),
(3, 'Mary', 'Joseph', 'mary.joseph@example.com', 5, 25, 1, 'Lower primary'),
(4, 'Peter', 'Mbwana', 'peter.mbwana@example.com', 6, 28, 1, 'Upper primary'),
(5, 'Fatma', 'Salim', 'fatma.salim@example.com', 6, 28, 1, 'Upper primary'),
(6, 'Juma', 'Ali', 'juma.ali@example.com', 6, 30, 1, 'Upper primary'),

(7, 'Sara', 'Kassim', 'sara.kassim@example.com', 6, 30, 1, 'Secondary'),
(8, 'Hamisi', 'Bakari', 'hamisi.bakari@example.com', 6, 30, 1, 'Secondary'),
(9, 'Ester', 'Paul', 'ester.paul@example.com', 6, 30, 1, 'Secondary'),
(10, 'Abdallah', 'Kheri', 'abdallah.kheri@example.com', 6, 30, 1, 'Secondary'),
(11, 'Hassan', 'Mohamed', 'hassan.mohamed@example.com', 6, 30, 1, 'Secondary'),
(12, 'Zainab', 'Suleiman', 'zainab.suleiman@example.com', 6, 30, 1, 'Secondary');


INSERT INTO class_subject_assignments (class_id, subject_id, teacher_id) VALUES
-- Grade 1
(1, 1, 1),  -- English
(1, 2, 2),  -- Math
(1, 3, 2),  -- Science
(1, 4, 3),  -- Social Studies
(1, 5, 4),  -- ICT
(1, 6, 5),  -- Arabic
(1, 7, 1),  -- Kiswahili
(1, 8, 3),  -- Geography

-- Grade 2
(2, 1, 1),
(2, 2, 2),
(2, 3, 2),
(2, 4, 3),
(2, 5, 4),
(2, 6, 5),
(2, 7, 1),
(2, 8, 3),

-- Grade 3
(3, 1, 1),
(3, 2, 2),
(3, 3, 2),
(3, 4, 3),
(3, 5, 4),
(3, 6, 5),
(3, 7, 1),
(3, 8, 3),

-- Grade 4
(4, 1, 1),
(4, 2, 2),
(4, 3, 2),
(4, 4, 3),
(4, 5, 4),
(4, 6, 5),
(4, 7, 1),
(4, 8, 3),

-- Grade 5
(5, 1, 1),
(5, 2, 2),
(5, 3, 2),
(5, 4, 3),
(5, 5, 4),
(5, 6, 5),
(5, 7, 1),
(5, 8, 3),

-- Grade 6
(6, 1, 1),
(6, 2, 2),
(6, 3, 2),
(6, 4, 3),
(6, 5, 4),
(6, 6, 5),
(6, 7, 1),
(6, 8, 3),

-- Grade 7
(7, 1, 1),
(7, 2, 2),
(7, 3, 2),
(7, 4, 3),
(7, 5, 4),
(7, 6, 5),
(7, 7, 1),
(7, 8, 3);


INSERT INTO period_template (day_name, period_number, start_time, end_time) VALUES
-- Monday
('Monday', 1, '08:00', '08:40'),
('Monday', 2, '08:40', '09:20'),
('Monday', 3, '09:20', '10:00'),
('Monday', 4, '10:20', '11:00'),
('Monday', 5, '11:00', '11:40'),
('Monday', 6, '11:40', '12:20'),
('Monday', 7, '12:20', '13:00'),
('Monday', 8, '14:00', '14:40'),

-- Tuesday
('Tuesday', 1, '08:00', '08:40'),
('Tuesday', 2, '08:40', '09:20'),
('Tuesday', 3, '09:20', '10:00'),
('Tuesday', 4, '10:20', '11:00'),
('Tuesday', 5, '11:00', '11:40'),
('Tuesday', 6, '11:40', '12:20'),
('Tuesday', 7, '12:20', '13:00'),
('Tuesday', 8, '14:00', '14:40'),

-- Wednesday
('Wednesday', 1, '08:00', '08:40'),
('Wednesday', 2, '08:40', '09:20'),
('Wednesday', 3, '09:20', '10:00'),
('Wednesday', 4, '10:20', '11:00'),
('Wednesday', 5, '11:00', '11:40'),
('Wednesday', 6, '11:40', '12:20'),
('Wednesday', 7, '12:20', '13:00'),
('Wednesday', 8, '14:00', '14:40'),

-- Thursday
('Thursday', 1, '08:00', '08:40'),
('Thursday', 2, '08:40', '09:20'),
('Thursday', 3, '09:20', '10:00'),
('Thursday', 4, '10:20', '11:00'),
('Thursday', 5, '11:00', '11:40'),
('Thursday', 6, '11:40', '12:20'),
('Thursday', 7, '12:20', '13:00'),
('Thursday', 8, '14:00', '14:40'),

-- Friday
('Friday', 1, '08:00', '08:40'),
('Friday', 2, '08:40', '09:20'),
('Friday', 3, '09:20', '10:00'),
('Friday', 4, '10:20', '11:00'),
('Friday', 5, '11:00', '11:40'),
('Friday', 6, '11:40', '12:20'),
('Friday', 7, '12:20', '13:00'),
('Friday', 8, '14:00', '14:40');

INSERT INTO timetables (class_id, subject_id, teacher_id, day_name, period_number) VALUES
-- Grade 1 (class_id = 1)
('1','1','1','Monday',1),   -- English
('1','2','2','Monday',2),   -- Math
('1','3','2','Monday',3),   -- Science
('1','7','1','Monday',4),   -- Kiswahili
('1','4','3','Monday',5),   -- Social Studies
('1','8','3','Monday',6),   -- Geography
('1','5','4','Monday',7),   -- ICT
('1','6','5','Monday',8),   -- Arabic

-- Tuesday
('1','2','2','Tuesday',1),
('1','1','1','Tuesday',2),
('1','3','2','Tuesday',3),
('1','7','1','Tuesday',4),
('1','4','3','Tuesday',5),
('1','5','4','Tuesday',6),
('1','8','3','Tuesday',7),
('1','6','5','Tuesday',8);
