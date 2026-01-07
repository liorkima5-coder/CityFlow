# 🏙️ CityFlow - Municipal Operations CRM

**CityFlow** היא מערכת SaaS מתקדמת לניהול אופרציה עירונית, פניות תושבים ופרויקטים תשתיתיים.
המערכת נבנתה בדגש על חווית משתמש (UX/UI), יעילות תפעולית ותמיכה מלאה בעברית (RTL).

## 🚀 פיצ'רים מרכזיים

* **ניהול פניות (Ticketing System):** מעקב מלא אחר פניות תושבים, סטטוסים, עדיפויות וצ'אט פנימי/חיצוני לכל פנייה.
* **ניהול פרויקטים:** שיוך פרויקטים למנהלי פרויקטים (PM) ומהנדסים, כולל מעקב אחר חטיבות ואזורים.
* **הרשאות ותפקידים (RBAC):** הפרדה מלאה בין Admin, Project Manager ו-Engineer.
* **דשבורד חכם:** תצוגה גרפית של KPIs, פניות פתוחות ופילוחים בזמן אמת.
* **עיצוב רספונסיבי:** מותאם למובייל ולדסקטופ באמצעות Bootstrap 5 בעיצוב מותאם אישית.

## 🛠️ טכנולוגיות

* **Backend:** Python 3, Flask
* **Database:** SQLAlchemy (SQLite for Dev / MySQL for Prod)
* **Frontend:** Jinja2 Templates, Bootstrap 5 (RTL), Custom CSS
* **Authentication:** Flask-Login, Werkzeug Security

## ⚙️ הוראות התקנה והרצה (Local Setup)

1. **שכפול הפרויקט:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/CityFlow-System.git](https://github.com/YOUR_USERNAME/CityFlow-System.git)
   cd CityFlow-System
