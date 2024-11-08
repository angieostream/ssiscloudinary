DROP DATABASE IF EXISTS `webssis`;

CREATE DATABASE `webssis`;
USE `webssis`;

-- Create colleges table
CREATE TABLE `colleges` (
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`code`)
);

-- Create programs table
CREATE TABLE `programs` (
  `code` VARCHAR(10) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `college_code` VARCHAR(10),
  PRIMARY KEY (`code`),
  FOREIGN KEY (`college_code`) REFERENCES `colleges`(`code`)
    ON DELETE CASCADE   
    ON UPDATE CASCADE
);

-- Create students table
CREATE TABLE `students` (
  `image_url` VARCHAR(255),
  `id` VARCHAR(9) NOT NULL,
  `firstname` VARCHAR(255) NOT NULL,
  `lastname` VARCHAR(255) NOT NULL,
  `course` VARCHAR(10),
  `year` INT CHECK (year >= 1 AND year <= 4),
  `gender` ENUM('Male', 'Female', 'Other') NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`course`) REFERENCES `programs`(`code`)
    ON DELETE SET NULL   
    ON UPDATE CASCADE
);

INSERT INTO colleges (code, name) VALUES ('CCS', 'College of Computer Studies');
INSERT INTO colleges (code, name) VALUES ('COE', 'College of Engineering');

INSERT INTO programs (code, name, college_code) VALUES ('BSCS', 'Bachelor of Science in Computer Science', 'CCS');
INSERT INTO programs (code, name, college_code) VALUES ('BSEE', 'Bachelor of Science in Electrical Engineering', 'COE');

