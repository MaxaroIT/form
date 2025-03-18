from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import json
import urllib.parse
import logging
import traceback

# Configureer logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialiseer de Flask-app met de aangepaste template-folder (map "Index")
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5'  # Vervang door een unieke sleutel

# Configureer SQL Server-verbinding
try:
    params = urllib.parse.quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=maxreportsrvr.database.windows.net;'
        'DATABASE=max_report_db;'
        'UID=reportadmin;'
        'PWD=#DAff!%nz8r7'
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={params}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    logger.info("Database URI geconfigureerd: %s", app.config['SQLALCHEMY_DATABASE_URI'])
except Exception as e:
    logger.error("Fout bij het configureren van de database URI: %s", str(e))
    traceback.print_exc()
    raise

# Initialiseer de database
try:
    db = SQLAlchemy(app)
    logger.info("SQLAlchemy succesvol geïnitialiseerd.")
except Exception as e:
    logger.error("Fout bij het initialiseren van SQLAlchemy: %s", str(e))
    traceback.print_exc()
    raise

# Lijst met medewerkers voor de selectvelden
EMPLOYEES = [
    "Danny Herbig",
    "Edine Loosman",
    "Davey Monsuur",

]


# Definieer het database model
class Project(db.Model):
    __tablename__ = 'projects_staging'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    goal_scope = db.Column(db.Text, nullable=False)
    project_leader = db.Column(db.String(50), nullable=False)
    # Opslag van stakeholder-gegevens als JSON (bijv. {"Stakeholder1": 10.5, "Stakeholder2": 5})
    stakeholder_hours = db.Column(db.Text, nullable=False)

# Test de databaseverbinding en modeltoegang
try:
    with app.app_context():
        result = db.session.execute(text("SELECT 1")).fetchone()
        logger.info("Databaseverbinding succesvol getest: %s", result)
        Project.query.first()
        logger.info("Modeltoegang succesvol getest.")
except Exception as e:
    logger.error("Fout bij het testen van de databaseverbinding of model: %s", str(e))
    traceback.print_exc()
    raise

# --- Definieer een subformulier voor stakeholder-invoer ---
from wtforms import Form as WTForm  # Eenvoudig WTForm voor de subvelden

class StakeholderEntryForm(WTForm):
    stakeholder = SelectField('Stakeholder', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired()])
    hours = FloatField('Aantal Uren', validators=[DataRequired()])

# --- Definieer het hoofdformulier ---
class ProjectForm(FlaskForm):
    project_name = StringField('Projectnaam', validators=[DataRequired()])
    goal_scope = TextAreaField('Doel en Scope (SMART)', validators=[DataRequired()])
    project_leader = SelectField('Projectleider', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired()])
    # Begin met 0 invoerregels; de gebruiker kan er zoveel toevoegen als gewenst
    stakeholder_entries = FieldList(FormField(StakeholderEntryForm), min_entries=0, max_entries=50)
    submit = SubmitField('Project indienen')

# Route voor het formulier
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            project_name = form.project_name.data
            goal_scope = form.goal_scope.data
            project_leader = form.project_leader.data

            # Bouw een dictionary met de ingevulde stakeholder-uren
            stakeholder_hours = {}
            for entry in form.stakeholder_entries.entries:
                stakeholder = entry.form.stakeholder.data
                hours = entry.form.hours.data
                if stakeholder and hours is not None:
                    stakeholder_hours[stakeholder] = hours

            # Zoek naar een bestaand project op basis van projectnaam
            project = Project.query.filter_by(project_name=project_name).first()
            if project:
                current_hours = json.loads(project.stakeholder_hours)
                current_hours.update(stakeholder_hours)
                project.stakeholder_hours = json.dumps(current_hours)
            else:
                project = Project(
                    project_name=project_name,
                    goal_scope=goal_scope,
                    project_leader=project_leader,
                    stakeholder_hours=json.dumps(stakeholder_hours)
                )
                db.session.add(project)

            db.session.commit()
            flash('Projectgegevens succesvol opgeslagen!', 'success')
            logger.info("Project '%s' opgeslagen met stakeholders: %s", project_name, stakeholder_hours)
        except Exception as e:
            logger.error("Fout bij het opslaan van projectgegevens: %s", str(e))
            traceback.print_exc()
            flash('Fout bij het opslaan: ' + str(e), 'error')
            db.session.rollback()
        return redirect(url_for('index'))
    # Geef ook de EMPLOYEES lijst mee zodat deze in de template gebruikt kan worden
    return render_template('index.html', form=form, employees=EMPLOYEES)

# Start de applicatie
if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=False, use_reloader=False)


