''' script for the routes of the web service '''

# pylint: disable=unused-variable

import datetime
from flask import render_template, request, redirect, url_for, Blueprint

from src.database.database import get_db
from src.util import config_util

bp = Blueprint('ziel', __name__)

def init_routes(app):
    ''' init the routes for the web service '''

    # Main View
    @app.route('/', methods= ['GET'])
    def index():
        with get_db().cursor() as cursor:
            # SQL-Abfrage, um die Zieldaten abzurufen
            sql = """
                SELECT
                    z.zielid,
                    z.aussage, 
                    z.kriterien, 
                    z.bewertung, 
                    z.kommentar, 
                    z.abteilungsid,
                    z.letzteaenderung, 
                    a.name AS abteilungsname,
                    h.geandertvon               
                FROM 
                    ziel z
                JOIN 
                    abteilung a ON z.abteilungsid = a.id  -- Verknüpfung der Abteilung
                LEFT JOIN 
                    historie h ON z.zielid = h.ziellid;  
            """
            cursor.execute(sql)
            ziele = cursor.fetchall()  # Abfragen aller Ziele

            # Abteilungsdaten abrufen
            cursor.execute("SELECT id, name FROM abteilung")  # Abteilungsdaten
            abteilungen = cursor.fetchall()  # Alle Abteilungen

            # Übergebe die Daten an die Vorlage
            return render_template("index.html.j2", ziele=ziele, abteilungen=abteilungen)

        

    @bp.route('/add_ziel', methods=['POST'])
    def add_ziel():
        abteilungsid = request.form['abteilungsid']
        aussage = request.form['aussage']
        kriterien = request.form['kriterien']
        bewertung = request.form['bewertung']
        kommentar = request.form['kommentar']
        geaendertvon = request.form['geaendertvon']

        # Aktuelle Zeit für letzte Änderung
        letzteaenderung = datetime.datetime.utcnow()  # Stellen Sie sicher, dass Sie datetime importiert haben

        try:
            with get_db().cursor() as cursor:
                # SQL-Befehl zum Einfügen der neuen Daten in die ziel-Tabelle
                sql = """
                    INSERT INTO ziel (abteilungsid, aussage, kriterien, bewertung, kommentar, letzteaenderung)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING zielid;  -- Rückgabe der ID des neu eingefügten Ziels
                """
                cursor.execute(sql, (abteilungsid, aussage, kriterien, bewertung, kommentar, letzteaenderung))
                zielid = cursor.fetchone()[0]  # ID des neu eingefügten Ziels abrufen
                
                # SQL-Befehl zum Einfügen in die historie-Tabelle
                sql_historie = """
                    INSERT INTO historie (ziellid, geandertvon, aenderungsdatum)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql_historie, (zielid, geaendertvon, letzteaenderung))
                get_db().commit()  # Änderungen speichern

            print('Ziel erfolgreich hinzugefügt!', 'success')  # Erfolgsnachricht
            return redirect(url_for('index'))  # Zurück zur Index-Seite

        except Exception as e:
            print(f"Fehler beim Hinzufügen des Ziels: {e}")
            return redirect(url_for('index', error='Fehler beim Hinzufügen des Ziels'))






    @bp.route('/edit', methods=['POST'])    
    def edit_ziel():
        zielid = request.form['zielid']  # Die ID des zu bearbeitenden Ziels
        abteilungsid = request.form['abteilungsid']
        aussage = request.form['aussage']
        kriterien = request.form['kriterien']
        bewertung = int(request.form['bewertung'])
        kommentar = request.form['kommentar']
        geaendertvon = request.form['geaendertvon']

        db = get_db()
        with db.cursor() as cursor:
            # SQL-Abfrage zum Aktualisieren eines Ziels
            sql = """
            UPDATE ziel 
            SET abteilungsid = %s, aussage = %s, kriterien = %s, bewertung = %s, kommentar = %s, letzte_aenderung = NOW(), aenderer = %s
            WHERE zielid = %s
            """
            cursor.execute(sql, (abteilungsid, aussage, kriterien, bewertung, kommentar, geaendertvon, zielid))
            db.commit()

        return redirect(url_for('ziel.index'))
    

    @bp.route('/historie/<int:id>', methods=['GET'])
    def historie(id):
        with get_db().cursor() as cursor:
            # SQL-Abfrage, um die Zieldaten abzurufen
            sql = f"""
                SELECT
                    geandertvon               
                FROM 
                    historie; 
            """
            cursor.execute(sql)
            historien = cursor.fetchall()  # Abfragen aller Ziele
            print(historien)
        return render_template("historie.html.j2", historien=historien, zielid=id)
