from database import DatabaseConnection
from models import User, PublicHoliday, Leave, HolidayPlan
from password_utils import hash_password, verify_password
from typing import List, Optional
from datetime import date
import json

class UserService:
    def find_by_id(self, user_id: int) -> Optional[User]:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return User(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    role=row['role'],
                    available_leaves=row['available_leaves'],
                    created_at=row.get('created_at')
                )
        return None

    def find_all_users(self) -> List[User]:
        conn = DatabaseConnection().get_connection()
        users = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE role = 'user' ORDER BY created_at DESC")
            for row in cursor.fetchall():
                users.append(User(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    role=row['role'],
                    available_leaves=row['available_leaves'],
                    created_at=row.get('created_at')
                ))
            cursor.close()
        return users

    def count_users(self) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
            cnt = cursor.fetchone()[0]
            cursor.close()
            return cnt
        return 0

    def update_profile(self, user_id: int, name: str, email: str) -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def update_leaves(self, user_id: int, leaves: int) -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET available_leaves = %s WHERE id = %s", (leaves, user_id))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False


class AuthService:
    def __init__(self):
        self.user_service = UserService()

    def login(self, email: str, password: str) -> Optional[User]:
        if not email or not password:
            return None
        email = email.strip()
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()
            if row and verify_password(password, row['password_hash']):
                return User(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    role=row['role'],
                    available_leaves=row['available_leaves'],
                    created_at=row.get('created_at')
                )
        return None

    def register(self, name: str, email: str, password: str) -> Optional[User]:
        if not name or not name.strip():
            raise ValueError("Name is required.")
        if not email or not email.strip():
            raise ValueError("Username / Email is required.")
        if not password or len(password) < 4:
            raise ValueError("Password must be at least 4 characters.")

        name = name.strip()
        email = email.strip()

        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                raise ValueError("An account with this username/email already exists.")

            pwd_hash = hash_password(password)
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, available_leaves)
                VALUES (%s, %s, %s, 'user', 10)
            """, (name, email, pwd_hash))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()

            return User(id=new_id, name=name, email=email, role='user', available_leaves=10)
        return None

    def update_leaves(self, user_id: int, leaves: int) -> bool:
        if leaves < 0:
            raise ValueError("Leaves cannot be negative.")
        return self.user_service.update_leaves(user_id, leaves)

    def update_profile(self, user_id: int, name: str, email: str) -> bool:
        return self.user_service.update_profile(user_id, name, email)

    def refresh_user(self, user_id: int) -> Optional[User]:
        return self.user_service.find_by_id(user_id)


class HolidayService:
    def get_all_holidays(self) -> List[PublicHoliday]:
        conn = DatabaseConnection().get_connection()
        holidays = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM public_holidays ORDER BY holiday_date ASC")
            for row in cursor.fetchall():
                holidays.append(PublicHoliday(
                    id=row['id'],
                    holiday_name=row['holiday_name'],
                    holiday_date=row['holiday_date'],
                    description=row.get('description', '')
                ))
            cursor.close()
        return holidays

    def get_holidays_in_range(self, start_date: date, end_date: date) -> List[PublicHoliday]:
        conn = DatabaseConnection().get_connection()
        holidays = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM public_holidays 
                WHERE holiday_date >= %s AND holiday_date <= %s
                ORDER BY holiday_date ASC
            """, (start_date, end_date))
            for row in cursor.fetchall():
                holidays.append(PublicHoliday(
                    id=row['id'],
                    holiday_name=row['holiday_name'],
                    holiday_date=row['holiday_date'],
                    description=row.get('description', '')
                ))
            cursor.close()
        return holidays

    def add_holiday(self, name: str, holiday_date: date, description: str = "") -> bool:
        if not name or not name.strip():
            raise ValueError("Holiday name is required.")
        if not holiday_date:
            raise ValueError("Date is required.")
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO public_holidays (holiday_name, holiday_date, description)
                VALUES (%s, %s, %s)
            """, (name.strip(), holiday_date, description.strip()))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def update_holiday(self, holiday_id: int, name: str, holiday_date: date, description: str = "") -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE public_holidays 
                SET holiday_name = %s, holiday_date = %s, description = %s
                WHERE id = %s
            """, (name.strip(), holiday_date, description.strip(), holiday_id))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def delete_holiday(self, holiday_id: int) -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM public_holidays WHERE id = %s", (holiday_id,))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def get_holiday_count(self) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM public_holidays")
            cnt = cursor.fetchone()[0]
            cursor.close()
            return cnt
        return 0


class LeaveService:
    def get_user_leaves(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Leave]:
        conn = DatabaseConnection().get_connection()
        leaves = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            if start_date and end_date:
                cursor.execute("""
                    SELECT * FROM user_leaves 
                    WHERE user_id = %s AND leave_date >= %s AND leave_date <= %s
                    ORDER BY leave_date ASC
                """, (user_id, start_date, end_date))
            else:
                cursor.execute("""
                    SELECT * FROM user_leaves 
                    WHERE user_id = %s 
                    ORDER BY leave_date ASC
                """, (user_id,))
            for row in cursor.fetchall():
                leaves.append(Leave(
                    id=row['id'],
                    user_id=row['user_id'],
                    leave_date=row['leave_date'],
                    status=row['status']
                ))
            cursor.close()
        return leaves

    def get_user_leaves_in_range(self, user_id: int, start_date: date, end_date: date) -> List[Leave]:
        return self.get_user_leaves(user_id, start_date, end_date)

    def add_leave(self, user_id: int, leave_date: date) -> bool:
        if not leave_date:
            raise ValueError("Date is required.")
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            # Check duplicate
            cursor.execute("SELECT id FROM user_leaves WHERE user_id = %s AND leave_date = %s", (user_id, leave_date))
            if cursor.fetchone():
                cursor.close()
                raise ValueError("Leave already exists for this date.")

            cursor.execute("""
                INSERT INTO user_leaves (user_id, leave_date, status) 
                VALUES (%s, %s, 'approved')
            """, (user_id, leave_date))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def delete_leave(self, leave_id: int) -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_leaves WHERE id = %s", (leave_id,))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def get_used_leave_count(self, user_id: int) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_leaves WHERE user_id = %s", (user_id,))
            cnt = cursor.fetchone()[0]
            cursor.close()
            return cnt
        return 0


class PlanService:
    def get_user_plans(self, user_id: int) -> List[HolidayPlan]:
        conn = DatabaseConnection().get_connection()
        plans = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM holiday_plans WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
            for row in cursor.fetchall():
                recs = []
                if row['recommended_dates']:
                    try:
                        raw = json.loads(row['recommended_dates'])
                        recs = [date.fromisoformat(d) for d in raw]
                    except Exception:
                        # Fallback for comma-separated dates from Java
                        recs = [date.fromisoformat(d.strip()) for d in row['recommended_dates'].split(",") if d.strip()]

                plans.append(HolidayPlan(
                    id=row['id'],
                    user_id=row['user_id'],
                    plan_name=row['plan_name'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    leaves_used=row['leaves_used'],
                    consecutive_days=row['consecutive_days'],
                    efficiency=row['efficiency'],
                    recommended_dates=recs,
                    created_at=row.get('created_at')
                ))
            cursor.close()
        return plans

    def get_all_plans(self) -> List[HolidayPlan]:
        conn = DatabaseConnection().get_connection()
        plans = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM holiday_plans ORDER BY created_at DESC")
            for row in cursor.fetchall():
                recs = []
                if row['recommended_dates']:
                    try:
                        raw = json.loads(row['recommended_dates'])
                        recs = [date.fromisoformat(d) for d in raw]
                    except Exception:
                        recs = [date.fromisoformat(d.strip()) for d in row['recommended_dates'].split(",") if d.strip()]

                plans.append(HolidayPlan(
                    id=row['id'],
                    user_id=row['user_id'],
                    plan_name=row['plan_name'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    leaves_used=row['leaves_used'],
                    consecutive_days=row['consecutive_days'],
                    efficiency=row['efficiency'],
                    recommended_dates=recs,
                    created_at=row.get('created_at')
                ))
            cursor.close()
        return plans

    def save_plan(self, plan: HolidayPlan) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            recs_json = json.dumps([d.isoformat() for d in plan.recommended_dates])
            cursor.execute("""
                INSERT INTO holiday_plans 
                (user_id, plan_name, start_date, end_date, leaves_used, consecutive_days, efficiency, recommended_dates)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (plan.user_id, plan.plan_name, plan.start_date, plan.end_date, plan.leaves_used, plan.consecutive_days, plan.efficiency, recs_json))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.close()
            return new_id
        return 0

    def delete_plan(self, plan_id: int) -> bool:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM holiday_plans WHERE id = %s", (plan_id,))
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            return affected > 0
        return False

    def count_user_plans(self, user_id: int) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM holiday_plans WHERE user_id = %s", (user_id,))
            cnt = cursor.fetchone()[0]
            cursor.close()
            return cnt
        return 0

    def count_all_plans(self) -> int:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM holiday_plans")
            cnt = cursor.fetchone()[0]
            cursor.close()
            return cnt
        return 0

    def get_best_plan(self) -> Optional[HolidayPlan]:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM holiday_plans ORDER BY efficiency DESC, consecutive_days DESC LIMIT 1")
            row = cursor.fetchone()
            cursor.close()
            if row:
                recs = []
                if row['recommended_dates']:
                    try:
                        raw = json.loads(row['recommended_dates'])
                        recs = [date.fromisoformat(d) for d in raw]
                    except Exception:
                        recs = [date.fromisoformat(d.strip()) for d in row['recommended_dates'].split(",") if d.strip()]
                return HolidayPlan(
                    id=row['id'],
                    user_id=row['user_id'],
                    plan_name=row['plan_name'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    leaves_used=row['leaves_used'],
                    consecutive_days=row['consecutive_days'],
                    efficiency=row['efficiency'],
                    recommended_dates=recs,
                    created_at=row.get('created_at')
                )
        return None

    def get_average_efficiency(self) -> float:
        conn = DatabaseConnection().get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(efficiency) FROM holiday_plans")
            res = cursor.fetchone()[0]
            cursor.close()
            return float(res) if res is not None else 0.0
        return 0.0
