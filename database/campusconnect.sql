-- CampusConnect MySQL Schema
-- Created for final year major project

CREATE DATABASE IF NOT EXISTS campusconnect;
USE campusconnect;

-- Disable foreign key checks to allow clean table re-creation if needed
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------
-- Table `users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `hashed_password` VARCHAR(255) NOT NULL,
  `role` ENUM('student', 'placed student', 'admin') NOT NULL DEFAULT 'student',
  `register_number` VARCHAR(50) DEFAULT NULL,
  `department` VARCHAR(100) DEFAULT NULL,
  `batch` VARCHAR(20) DEFAULT NULL,
  `college` VARCHAR(150) DEFAULT NULL,
  `skills` TEXT DEFAULT NULL, -- Comma-separated or JSON
  `github` VARCHAR(255) DEFAULT NULL,
  `linkedin` VARCHAR(255) DEFAULT NULL,
  `resume_url` VARCHAR(255) DEFAULT NULL,
  `profile_pic_url` VARCHAR(255) DEFAULT NULL,
  `placement_status` ENUM('unplaced', 'placed') NOT NULL DEFAULT 'unplaced',
  `company_name` VARCHAR(100) DEFAULT NULL,
  `job_role` VARCHAR(100) DEFAULT NULL,
  `ctc` DECIMAL(5,2) DEFAULT NULL, -- CTC in LPA (e.g. 12.50)
  `is_verified` TINYINT(1) NOT NULL DEFAULT 0,
  `verification_token` VARCHAR(255) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_email (`email`),
  INDEX idx_user_username (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `companies`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `companies`;
CREATE TABLE IF NOT EXISTS `companies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `logo_url` VARCHAR(255) DEFAULT NULL,
  `website` VARCHAR(255) DEFAULT NULL,
  `industry` VARCHAR(100) DEFAULT NULL,
  `description` TEXT DEFAULT NULL,
  `average_package` DECIMAL(5,2) DEFAULT NULL, -- in LPA
  `highest_package` DECIMAL(5,2) DEFAULT NULL, -- in LPA
  `eligibility` TEXT DEFAULT NULL,
  `selection_process` TEXT DEFAULT NULL,
  `hiring_pattern` TEXT DEFAULT NULL,
  `faq` TEXT DEFAULT NULL, -- JSON structured FAQ
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_company_name (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `placement_experiences`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `placement_experiences`;
CREATE TABLE IF NOT EXISTS `placement_experiences` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `company_id` INT NOT NULL,
  `job_role` VARCHAR(100) NOT NULL,
  `ctc` DECIMAL(5,2) NOT NULL, -- in LPA
  `job_type` ENUM('Internship', 'Full-Time', 'Internship + Full-Time') NOT NULL DEFAULT 'Full-Time',
  `location` VARCHAR(100) DEFAULT NULL,
  `drive_date` DATE DEFAULT NULL,
  `hiring_type` ENUM('On Campus', 'Off Campus', 'Pool Campus') NOT NULL DEFAULT 'On Campus',
  `eligibility_criteria` TEXT DEFAULT NULL,
  `rounds_count` INT NOT NULL DEFAULT 1,
  `difficulty` ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Medium',
  `result` ENUM('Selected', 'Rejected') NOT NULL DEFAULT 'Selected',
  
  -- Detailed sections
  `experience_details` TEXT NOT NULL,
  `prep_strategy` TEXT DEFAULT NULL,
  `prep_timeline` TEXT DEFAULT NULL,
  `coding_round_exp` TEXT DEFAULT NULL,
  `tech_questions` TEXT DEFAULT NULL,
  `hr_questions` TEXT DEFAULT NULL,
  `behavioral_questions` TEXT DEFAULT NULL,
  `sql_questions` TEXT DEFAULT NULL,
  `system_design_questions` TEXT DEFAULT NULL,
  `mistakes` TEXT DEFAULT NULL,
  `tips` TEXT DEFAULT NULL,
  `resources_used` TEXT DEFAULT NULL,
  `leetcode_solved` TEXT DEFAULT NULL,
  `projects_asked` TEXT DEFAULT NULL,
  `resume_tips` TEXT DEFAULT NULL,
  `final_suggestions` TEXT DEFAULT NULL,
  
  `attachment_url` VARCHAR(255) DEFAULT NULL,
  `tags` VARCHAR(255) DEFAULT NULL, -- Comma-separated list
  `is_approved` TINYINT(1) NOT NULL DEFAULT 0, -- Approved by admin
  `likes_count` INT NOT NULL DEFAULT 0,
  `comments_count` INT NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE,
  INDEX idx_exp_company (`company_id`),
  INDEX idx_exp_user (`user_id`),
  INDEX idx_exp_approved (`is_approved`),
  INDEX idx_exp_ctc (`ctc`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `interview_questions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `interview_questions`;
CREATE TABLE IF NOT EXISTS `interview_questions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `company_id` INT NOT NULL,
  `role` VARCHAR(100) NOT NULL,
  `category` ENUM('DSA', 'OOPS', 'DBMS', 'Operating System', 'Computer Networks', 'SQL', 'Java', 'Python', 'JavaScript', 'HTML', 'CSS', 'Bootstrap', 'HR', 'Aptitude') NOT NULL DEFAULT 'DSA',
  `question_text` TEXT NOT NULL,
  `answer_text` TEXT DEFAULT NULL,
  `difficulty` ENUM('Easy', 'Medium', 'Hard') NOT NULL DEFAULT 'Medium',
  `topic` VARCHAR(100) DEFAULT NULL,
  `likes_count` INT NOT NULL DEFAULT 0,
  `comments_count` INT NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE,
  INDEX idx_q_category (`category`),
  INDEX idx_q_company (`company_id`),
  INDEX idx_q_difficulty (`difficulty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `roadmaps`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `roadmaps`;
CREATE TABLE IF NOT EXISTS `roadmaps` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `target_company` VARCHAR(100) DEFAULT NULL,
  `target_role` VARCHAR(100) DEFAULT NULL,
  `duration` VARCHAR(50) DEFAULT NULL, -- e.g., "3 Months", "6 Weeks"
  `daily_plan` TEXT DEFAULT NULL,
  `weekly_plan` TEXT DEFAULT NULL,
  `topics` TEXT DEFAULT NULL,
  `resources` TEXT DEFAULT NULL,
  `youtube_links` TEXT DEFAULT NULL,
  `pdf_notes_url` VARCHAR(255) DEFAULT NULL,
  `leetcode_sheet` TEXT DEFAULT NULL,
  `gfg_links` TEXT DEFAULT NULL,
  `likes_count` INT NOT NULL DEFAULT 0,
  `comments_count` INT NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_roadmap_user (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `comments`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE IF NOT EXISTS `comments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `parent_type` ENUM('experience', 'question', 'roadmap') NOT NULL,
  `parent_id` INT NOT NULL,
  `comment_text` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_comment_parent (`parent_type`, `parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `likes`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `likes`;
CREATE TABLE IF NOT EXISTS `likes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `parent_type` ENUM('experience', 'question', 'roadmap') NOT NULL,
  `parent_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `unique_user_like` (`user_id`, `parent_type`, `parent_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_like_parent (`parent_type`, `parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `bookmarks`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `bookmarks`;
CREATE TABLE IF NOT EXISTS `bookmarks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `parent_type` ENUM('experience', 'question', 'roadmap') NOT NULL,
  `parent_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `unique_user_bookmark` (`user_id`, `parent_type`, `parent_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_bookmark_parent (`parent_type`, `parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `follows`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `follows`;
CREATE TABLE IF NOT EXISTS `follows` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `follower_id` INT NOT NULL,
  `followed_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE KEY `unique_follow` (`follower_id`, `followed_id`),
  FOREIGN KEY (`follower_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`followed_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `notifications`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL, -- Target user
  `actor_id` INT NOT NULL, -- User who triggered notification
  `type` ENUM('like', 'comment', 'follow', 'post_approval', 'admin_alert') NOT NULL,
  `parent_type` ENUM('experience', 'question', 'roadmap', 'user') DEFAULT NULL,
  `parent_id` INT DEFAULT NULL,
  `message` TEXT NOT NULL,
  `is_read` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`actor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_notification_user (`user_id`, `is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------
-- Table `reports`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `reports`;
CREATE TABLE IF NOT EXISTS `reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL, -- Reporter
  `parent_type` ENUM('experience', 'question', 'roadmap', 'comment') NOT NULL,
  `parent_id` INT NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `details` TEXT DEFAULT NULL,
  `status` ENUM('Pending', 'Resolved', 'Dismissed') NOT NULL DEFAULT 'Pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  INDEX idx_report_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------
-- Sample Seed Data
-- -----------------------------------------------------
-- Default Admin password: 'adminpassword' (hashed version: '$2b$12$K.l96R9r/l6yN82.1hP2xef1i0u7pUkyH38eE/iWb.XlO9V/gX0vS')
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `role`, `is_verified`, `placement_status`) VALUES
(1, 'admin', 'admin@campusconnect.com', '$2b$12$K.l96R9r/l6yN82.1hP2xef1i0u7pUkyH38eE/iWb.XlO9V/gX0vS', 'admin', 1, 'unplaced');

-- Default User password: 'password123' (hashed version: '$2b$12$4m7.zZ0Zq6tB/y9JzU.d8O9Y.W/3Nn72uP.C3jM4W66k8aJ4e6UHe')
INSERT INTO `users` (`id`, `username`, `email`, `hashed_password`, `role`, `register_number`, `department`, `batch`, `college`, `skills`, `placement_status`, `is_verified`) VALUES
(2, 'johndoe', 'johndoe@college.edu', '$2b$12$4m7.zZ0Zq6tB/y9JzU.d8O9Y.W/3Nn72uP.C3jM4W66k8aJ4e6UHe', 'student', 'REG001', 'Computer Applications', '2023-2026', 'National Institute of Technology', 'Java, Python, HTML, CSS, SQL', 'unplaced', 1),
(3, 'anasharma', 'anasharma@college.edu', '$2b$12$4m7.zZ0Zq6tB/y9JzU.d8O9Y.W/3Nn72uP.C3jM4W66k8aJ4e6UHe', 'placed student', 'REG002', 'Computer Science', '2022-2026', 'National Institute of Technology', 'C++, Python, DSA, System Design, AWS', 'placed', 1);

UPDATE `users` SET `company_name` = 'Google', `job_role` = 'Software Engineer', `ctc` = 32.50 WHERE `id` = 3;

INSERT INTO `companies` (`id`, `name`, `website`, `industry`, `description`, `average_package`, `highest_package`, `eligibility`, `selection_process`, `hiring_pattern`) VALUES
(1, 'Google', 'https://google.com', 'Technology', 'Multinational technology company focusing on search, cloud computing, and AI.', 18.50, 45.00, 'CGPA >= 8.0, No active backlogs', 'Coding Assessment -> 3 Technical Rounds -> 1 Googley & Leadership Round', 'Coding & DSA intensive, focuses on problem-solving ability'),
(2, 'Microsoft', 'https://microsoft.com', 'Technology', 'Global leader in software, cloud solutions, and personal computing devices.', 16.00, 40.00, 'CGPA >= 7.5, CS/IT/MCA branch preferred', 'Online Assessment -> 2 Technical Rounds -> 1 System Design/Managerial Round', 'DSA + OOPS + System Design concepts');

INSERT INTO `placement_experiences` (`id`, `user_id`, `company_id`, `job_role`, `ctc`, `job_type`, `location`, `drive_date`, `hiring_type`, `eligibility_criteria`, `rounds_count`, `difficulty`, `result`, `experience_details`, `prep_strategy`, `prep_timeline`, `coding_round_exp`, `tech_questions`, `hr_questions`, `behavioral_questions`, `sql_questions`, `system_design_questions`, `mistakes`, `tips`, `resources_used`, `leetcode_solved`, `projects_asked`, `resume_tips`, `final_suggestions`, `tags`, `is_approved`) VALUES
(1, 3, 1, 'Software Engineer', 32.50, 'Full-Time', 'Bangalore, India', '2026-06-10', 'On Campus', 'CGPA >= 8.0', 4, 'Hard', 'Selected', 
'It was an amazing recruitment drive. The process was completely online.', 
'Practiced DSA questions on Leetcode, focused on Graphs and Dynamic Programming. Revised Operating Systems and DBMS concepts.', 
'Started preparing seriously from 3rd year. Dedicated 4-5 hours daily.', 
'The coding round had 2 questions on Leetcode medium/hard levels. One DP question and one graph traversal.', 
'Question 1: Find the shortest path in a weighted grid with obstacles.\nQuestion 2: Design an efficient algorithm for cache eviction.', 
'Standard questions about goals, relocation preference, and career interests.', 
'Tell me about a time you had a conflict with a teammate and how you resolved it.', 
'Explain 3rd Normal Form and write a query to find the second highest salary.', 
'Design a URL shortener like TinyURL. Talked about database schema, load balancer, and caching.', 
'Panic during the second round when I could not immediately find the DP solution. Took a deep breath and talked out loud.', 
'Be clear in your communication. Think aloud so the interviewer knows your approach.', 
'Leetcode, GeeksforGeeks, NeetCode YouTube channel.', 
'Solved around 450 problems (150 Easy, 250 Medium, 50 Hard).', 
'Explain the database design of your final year e-commerce project.', 
'Keep it to one page, highlight key impact statements rather than listing tech stacks.', 
'Consistency is the key. Keep solving at least 2 questions daily.', 
'Google, SWE, FullTime, Hard', 1);

INSERT INTO `interview_questions` (`id`, `user_id`, `company_id`, `role`, `category`, `question_text`, `answer_text`, `difficulty`, `topic`) VALUES
(1, 3, 1, 'Software Engineer', 'DSA', 'Given a binary tree, find its maximum path sum.', 'We can solve this recursively. For each node, compute the max path sum passing through it as: node.val + max(0, left) + max(0, right). Update the global max path sum and return the node value plus the maximum of its left or right child paths.', 'Hard', 'Binary Trees / Recursion'),
(2, 3, 2, 'Software Engineer', 'SQL', 'Find the Nth highest salary in an Employee table.', 'Using standard SQL: SELECT MIN(salary) FROM (SELECT DISTINCT salary FROM Employee ORDER BY salary DESC LIMIT N) AS Emp;', 'Medium', 'SQL Joins & Aggregations');
