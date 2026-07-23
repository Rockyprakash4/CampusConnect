import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure the backend directory itself is on the path (main.py, database.py etc.
# use flat imports like "from database import Base", so the backend/ folder,
# not its parent, must be on sys.path)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app
from database import Base, engine, SessionLocal
import models

client = TestClient(app)

class TestCampusConnect(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Always use a local test SQLite database for test runs
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        
        # Clean up database for clean run
        cls.db.query(models.Comment).delete()
        cls.db.query(models.Like).delete()
        cls.db.query(models.Bookmark).delete()
        cls.db.query(models.PlacementExperience).delete()
        cls.db.query(models.InterviewQuestion).delete()
        cls.db.query(models.Company).delete()
        cls.db.query(models.User).delete()
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        # Remove sqlite db after testing
        if os.path.exists("./campusconnect.db"):
            try:
                pass # keep it for development inspection
            except:
                pass

    def test_01_user_registration(self):
        print("\n[Test 1] Registering test student...")
        response = client.post("/api/auth/register", json={
            "username": "studenttest",
            "email": "student@college.edu",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "studenttest")
        self.assertEqual(data["role"], "admin") # First registered user gets auto-promoted to admin in our routers
        
        print("[Test 1.1] Registering second student...")
        response2 = client.post("/api/auth/register", json={
            "username": "placedstudent",
            "email": "placed@college.edu",
            "password": "password123"
        })
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2["role"], "student") # Subsequent user is standard student

    def test_02_email_verification(self):
        print("\n[Test 2] Verifying student email...")
        # Retrieve verification token directly from DB
        user = self.db.query(models.User).filter(models.User.username == "placedstudent").first()
        token = user.verification_token
        self.assertIsNotNone(token)
        
        response = client.get(f"/api/auth/verify-email?token={token}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("verified", response.json()["message"])
        
        # Verify first student (admin) as well
        admin_user = self.db.query(models.User).filter(models.User.username == "studenttest").first()
        client.get(f"/api/auth/verify-email?token={admin_user.verification_token}")

    def test_03_login_and_jwt(self):
        print("\n[Test 3] Testing user logins (JWT issuing)...")
        # Log in student
        response = client.post("/api/auth/login", data={
            "username": "placedstudent",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        login_data = response.json()
        self.assertIn("access_token", login_data)
        self.assertEqual(login_data["role"], "student")
        
        # Save token for subsequent tests
        self.__class__.student_token = login_data["access_token"]
        
        # Log in admin
        response_admin = client.post("/api/auth/login", data={
            "username": "studenttest",
            "password": "password123"
        })
        self.assertEqual(response_admin.status_code, 200)
        self.__class__.admin_token = response_admin.json()["access_token"]

    def test_04_profile_management(self):
        print("\n[Test 4] Updating profile details...")
        headers = {"Authorization": f"Bearer {self.student_token}"}
        response = client.put("/api/users/me", headers=headers, json={
            "register_number": "MCA202604",
            "department": "Computer Applications",
            "batch": "2024-2026",
            "college": "National Institute of Technology",
            "skills": "Python, FastAPI, SQL, HTML/CSS",
            "placement_status": "placed", # updates role to placed student
            "company_name": "Google",
            "job_role": "Software Engineering Intern",
            "ctc": 18.50
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["role"], "placed student")
        self.assertEqual(data["placement_status"], "placed")
        self.assertEqual(data["company_name"], "Google")

    def test_05_create_placement_experience(self):
        print("\n[Test 5] Sharing placement experience (Placed Student role)...")
        headers = {"Authorization": f"Bearer {self.student_token}"}
        response = client.post("/api/experiences/", headers=headers, json={
            "company_name": "Microsoft",
            "job_role": "Software Engineer",
            "ctc": 24.50,
            "job_type": "Full-Time",
            "location": "Hyderabad, India",
            "difficulty": "Hard",
            "result": "Selected",
            "experience_details": "Completed a coding round and 3 tech interviews. Questions centered on graph traversals, system design, and database queries.",
            "prep_strategy": "Practiced Leetcode questions daily and studied DBMS indexes.",
            "tips": "Revise object-oriented systems and communicate clearly during interviews."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["job_role"], "Software Engineer")
        self.assertEqual(data["is_approved"], False) # Requires Admin moderation
        self.__class__.experience_id = data["id"]

    def test_06_admin_moderation_approval(self):
        print("\n[Test 6] Moderating experience approval (Admin role)...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Fetch pending experiences
        pending_res = client.get("/api/admin/experiences/pending", headers=headers)
        self.assertEqual(pending_res.status_code, 200)
        self.assertEqual(len(pending_res.json()), 1)
        
        # Approve experience
        approve_res = client.post(f"/api/admin/experiences/{self.experience_id}/approve", headers=headers)
        self.assertEqual(approve_res.status_code, 200)
        self.assertIn("approved", approve_res.json()["message"])

    def test_07_social_interactions(self):
        print("\n[Test 7] Verifying Likes, Comments, and bookmarks...")
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        # 1. Like
        like_res = client.post("/api/interactions/like", headers=headers, json={
            "parent_type": "experience",
            "parent_id": self.experience_id
        })
        self.assertEqual(like_res.status_code, 200)
        self.assertEqual(like_res.json()["status"], "liked")
        
        # 2. Comment
        comment_res = client.post("/api/interactions/comment", headers=headers, json={
            "parent_type": "experience",
            "parent_id": self.experience_id,
            "comment_text": "Excellent walkthrough, thank you senior!"
        })
        self.assertEqual(comment_res.status_code, 200)
        self.assertEqual(comment_res.json()["comment_text"], "Excellent walkthrough, thank you senior!")
        
        # 3. Read Comments
        comments_list = client.get(f"/api/interactions/comments/experience/{self.experience_id}")
        self.assertEqual(comments_list.status_code, 200)
        self.assertEqual(len(comments_list.json()), 1)

    def test_08_pdf_generation(self):
        print("\n[Test 8] Testing ReportLab PDF download streaming...")
        response = client.get(f"/api/experiences/{self.experience_id}/pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(len(response.content) > 0)
        print(f"[Test 8.1] Streamed PDF file successfully. File size: {len(response.content)} bytes.")

if __name__ == "__main__":
    unittest.main()
