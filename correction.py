from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from dotenv import load_dotenv
from functools import wraps
from emailer import send_admin_notification
import os
import csv
import io
from db import init_db

load_dotenv()

def create_app():
    app = Flask(__name__)
    init_db()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("is_admin"):
               return redirect(url_for("admin_login"))
            return view(*args, **kwargs)
        return wrapped
    
    @app.get("/")
    def home():
        return render_template("home.html", title="Home")

    @app.get("/about")
    def about():
        return render_template("about.html", title="About")

    @app.get("/program")
    def program():
        return render_template("program.html", title="Program")

    @app.get("/community")
    def community():
        return render_template("community.html", title="Community")

    @app.get("/resources")
    def resources():
        return render_template("resources.html", title="Resources")

    @app.get("/publications")
    def publications():
        return render_template("publications.html", title="Publications")

    @app.get("/scholarships")
    def scholarships():
        return render_template("scholarships.html", title="Scholarships & Awards")

    @app.route("/apply", methods=["GET", "POST"])
    def apply():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            city = request.form.get("city", "").strip()
            french_level = request.form.get("french_level", "").strip()
            university_status = request.form.get("university_status", "").strip()
            motivation = request.form.get("motivation", "").strip()

            # Basic validation
            errors = []
            if not full_name: errors.append("Full name is required.")
            if not email: errors.append("Email is required.")
            if not phone: errors.append("Phone number is required.")
            if not motivation: errors.append("Motivation is required.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template("apply.html", title="Apply",
                                      form=request.form)

            # Save to DB
            from db import get_connection
            conn = get_connection()
            conn.execute("""
                INSERT INTO applications (full_name, email, phone, city, french_level, university_status, motivation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (full_name, email, phone, city, french_level, university_status, motivation))
            conn.commit()
            conn.close()
            from emailer import send_admin_notification

            send_admin_notification(
                subject="New NGLF Application Submitted",
                body=(
                    f"A new application was submitted:\n\n"
                    f"Name: {full_name}\n"
                    f"Email: {email}\n"
                    f"Phone: {phone}\n"
                    f"City/State: {city or '-'}\n"
                    f"French Level: {french_level or '-'}\n"
                    f"University Status: {university_status or '-'}\n\n"
                    f"Motivation:\n{motivation}\n"
                )
            )


            flash("Application submitted successfully! We’ll get back to you soon.", "success")
            return redirect(url_for("apply"))

        return render_template("apply.html", title="Apply", form={})
    

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
           password = request.form.get("password", "")
        if password == os.getenv("ADMIN_PASSWORD"):
            session["is_admin"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin_applications"))
        flash("Incorrect password.", "error")
    return render_template("admin_login.html", title="Admin Login")


    @app.get("/admin/logout")
    def admin_logout():
        session.pop("is_admin", None)
        flash("Logged out.", "success")
        return redirect(url_for("home"))


    @app.get("/admin/applications")
    @admin_required
    def admin_applications():
        from db import get_connection
        conn = get_connection()
        rows = conn.execute("""
            SELECT id, full_name, email, phone, city, french_level, university_status, motivation, created_at
            FROM applications
            ORDER BY id DESC
        """).fetchall()
        conn.close()
        return render_template("admin_applications.html", title="Applications", applications=rows)


    @app.get("/admin/applications.csv")
    @admin_required
    def admin_export_csv():
        from db import get_connection
        conn = get_connection()
        rows = conn.execute("""
            SELECT id, full_name, email, phone, city, french_level, university_status, motivation, created_at
            FROM applications
            ORDER BY id DESC
        """).fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id","full_name","email","phone","city","french_level","university_status","motivation","created_at"])
        for r in rows:
            writer.writerow([r["id"], r["full_name"], r["email"], r["phone"], r["city"], r["french_level"], r["university_status"], r["motivation"], r["created_at"]])
  
        mem = io.BytesIO(output.getvalue().encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="applications.csv")


    @app.get("/donate")
    def donate():
        return render_template("donate.html", title="Donate")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
