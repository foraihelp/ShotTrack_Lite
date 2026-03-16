from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def connect():
    return sqlite3.connect(DATABASE)


def init_db():

    conn = connect()
    c = conn.cursor()

    # PROJECT TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS projects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        status TEXT
    )
    """)

    # REEL / EPISODE TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS units(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status TEXT,
        project_id INTEGER
    )
    """)

    # SEQUENCE TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS sequences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status TEXT,
        unit_id INTEGER
    )
    """)

    # SHOT TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS shots(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        status TEXT,
        sequence_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


# ---------------- PROJECT PAGE ----------------

@app.route("/", methods=["GET","POST"])
def home():

    conn = connect()
    c = conn.cursor()

    if request.method == "POST":

        action = request.form["action"]

        # CREATE PROJECT
        if action == "create":

            name = request.form["name"]
            type = request.form["type"]
            status = request.form["status"]

            c.execute(
                "INSERT INTO projects(name,type,status) VALUES (?,?,?)",
                (name,type,status)
            )

        # RENAME PROJECT
        if action == "rename":

            pid = request.form["id"]
            new_name = request.form["new"]

            c.execute(
                "UPDATE projects SET name=? WHERE id=?",
                (new_name,pid)
            )

        # DELETE PROJECT
        if action == "delete":

            pid = request.form["id"]

            c.execute(
                "DELETE FROM projects WHERE id=?",
                (pid,)
            )

        # UPDATE TYPE
        if action == "type":

            pid = request.form["id"]
            value = request.form["value"]

            c.execute(
                "UPDATE projects SET type=? WHERE id=?",
                (value,pid)
            )

        # UPDATE STATUS
        if action == "status":

            pid = request.form["id"]
            value = request.form["value"]

            c.execute(
                "UPDATE projects SET status=? WHERE id=?",
                (value,pid)
            )

        conn.commit()

        return redirect("/")

    c.execute("SELECT * FROM projects")
    projects = c.fetchall()

    conn.close()

    return render_template("projects.html",projects=projects)


# ---------------- REEL PAGE ----------------

@app.route("/project/<int:pid>", methods=["GET","POST"])
def project(pid):

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE id=?", (pid,))
    project = c.fetchone()

    if request.method == "POST":

        action = request.form["action"]

        # ADD REEL / EPISODE
        if action == "add":

            c.execute("SELECT COUNT(*) FROM units WHERE project_id=?", (pid,))
            next_number = c.fetchone()[0] + 1

            project_name = project[1]

            if project[2] == "Movie":
                name = f"{project_name}_R{str(next_number).zfill(2)}"
            else:
                name = f"{project_name}_EP{str(next_number).zfill(2)}"

            c.execute(
                "INSERT INTO units(name,status,project_id) VALUES (?,?,?)",
                (name,"YTS",pid)
            )

        # RENAME REEL
        if action == "rename":

            uid = request.form["id"]
            new = request.form["new"]

            c.execute(
                "UPDATE units SET name=? WHERE id=?",
                (new,uid)
            )

        # DELETE REEL
        if action == "delete":

            uid = request.form["id"]

            c.execute(
                "DELETE FROM units WHERE id=?",
                (uid,)
            )

        # UPDATE REEL STATUS
        if action == "status":

            uid = request.form["id"]
            value = request.form["value"]

            c.execute(
                "UPDATE units SET status=? WHERE id=?",
                (value,uid)
            )

        conn.commit()

        return redirect(f"/project/{pid}")

    c.execute("SELECT * FROM units WHERE project_id=?", (pid,))
    units = c.fetchall()

    conn.close()

    return render_template("units.html",project=project,units=units)


# ---------------- SEQUENCE PAGE ----------------

@app.route("/unit/<int:uid>", methods=["GET","POST"])
def unit(uid):

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM units WHERE id=?", (uid,))
    unit = c.fetchone()

    c.execute("SELECT * FROM projects WHERE id=?", (unit[3],))
    project = c.fetchone()

    if request.method == "POST":

        action = request.form["action"]

        if action == "add":

            c.execute("SELECT COUNT(*) FROM sequences WHERE unit_id=?", (uid,))
            next_number = c.fetchone()[0] + 1

            name = f"{unit[1]}_SQ{str(next_number).zfill(3)}"

            c.execute(
                "INSERT INTO sequences(name,status,unit_id) VALUES (?,?,?)",
                (name,"YTS",uid)
            )

        if action == "rename":

            sid = request.form["id"]
            new = request.form["new"]

            c.execute(
                "UPDATE sequences SET name=? WHERE id=?",
                (new,sid)
            )

        if action == "delete":

            sid = request.form["id"]

            c.execute(
                "DELETE FROM sequences WHERE id=?",
                (sid,)
            )

        if action == "status":

            sid = request.form["id"]
            value = request.form["value"]

            c.execute(
                "UPDATE sequences SET status=? WHERE id=?",
                (value,sid)
            )

        conn.commit()

        return redirect(f"/unit/{uid}")

    c.execute("SELECT * FROM sequences WHERE unit_id=?", (uid,))
    sequences = c.fetchall()

    conn.close()

    return render_template(
        "sequences.html",
        project=project,
        unit=unit,
        sequences=sequences
    )


# ---------------- SHOT PAGE ----------------

@app.route("/sequence/<int:sid>", methods=["GET","POST"])
def sequence(sid):

    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM sequences WHERE id=?", (sid,))
    sequence = c.fetchone()

    c.execute("SELECT * FROM units WHERE id=?", (sequence[3],))
    unit = c.fetchone()

    c.execute("SELECT * FROM projects WHERE id=?", (unit[3],))
    project = c.fetchone()

    if request.method == "POST":

        action = request.form["action"]

        if action == "add":

            c.execute("SELECT COUNT(*) FROM shots WHERE sequence_id=?", (sid,))
            next_number = c.fetchone()[0] + 1

            name = f"{sequence[1]}_SH{str(next_number).zfill(3)}"

            c.execute(
                "INSERT INTO shots(name,status,sequence_id) VALUES (?,?,?)",
                (name,"YTS",sid)
            )

        if action == "rename":

            shot_id = request.form["id"]
            new = request.form["new"]

            c.execute(
                "UPDATE shots SET name=? WHERE id=?",
                (new,shot_id)
            )

        if action == "delete":

            shot_id = request.form["id"]

            c.execute(
                "DELETE FROM shots WHERE id=?",
                (shot_id,)
            )

        if action == "status":

            shot_id = request.form["id"]
            value = request.form["value"]

            c.execute(
                "UPDATE shots SET status=? WHERE id=?",
                (value,shot_id)
            )

        conn.commit()

        return redirect(f"/sequence/{sid}")

    c.execute("SELECT * FROM shots WHERE sequence_id=?", (sid,))
    shots = c.fetchall()

    conn.close()

    return render_template(
        "shots.html",
        project=project,
        unit=unit,
        sequence=sequence,
        shots=shots
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
