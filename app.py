from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import json
import urllib.parse
import logging
import traceback

# Configureer logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialiseer de Flask-app en stel de template-folder in
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5'  # Zorg voor een unieke sleutel

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

# Dictionary met projecten per programma
projecten = {
    "Digitale klantreis": [
        "Droombadkamerformulier",
        "Uitbreidingen Mabo / Mijn Maxaro",
        "Top 5 talen online",
        "Customer Journey Onderzoek",
        "Meubelconfigurator",
        "Badkamer Varianttool",
        "Keuzehulp complete ruimtes",
        "Zoekfunctie implementatie",
        "CDP onderzoek",
        "Inzet van AR/360",
        "Mirror website",
        "Exploded views",
        "Technische tekeningen",
        "Configurator CMS"
    ],
    "Klantsucces": [
        "D365 contact center (inventarisatie)",
        "Procesinventarisatie aftersales",
        "Geautomatiseerde mailing",
        "Introduceren wandpanelen",
        "Chatbot Max",
        "Luxe meubel serie"
    ],
    "Marketingtransformatie": [
        "Inrichting Google Analytics 4 (GA4)",
        "Automatisering complete ruimtes",
        "Rebranding website",
        "Bedrijfsvideo (opzet)",
        "Ombouw showroom HFD & RSD",
        "Nieuwe standaard doucherenders",
        "Strategie Social, SEO en SEA",
        "Branding Showroom UTR/RTD/MOR",
        "Productvideo's (onderzoek)",
        "Installatie video's (inventarisatie)",
        "Technische detailrenders",
        "Automatiseren detailrenders",
        "Onderzoek in-store tafel vloersamples"
    ],
    "Digitale transformatie": [
        "Dual Write",
        "Order API",
        "VST API",
        "Xelion API dashboard",
        "Intercompany Sync",
        "Auto release to warehouse",
        "OPS release Q1",
        "Location Management 2.0",
        "Manus 5.0",
        "SharePoint Basis + POC",
        "Microsoft Copilot (onderzoek)",
        "Artikelbeheer automatisering PvA"
    ],
    "Organisatie & Cultuur": [
        "O&O (inventarisatie)",
        "Projectmanagement 3.0 Monday",
        "Vernieuwde scaling-up structuur",
        "Telefonie KPI sales afgestemd",
        "Verzilvering opgeleverde projecten",
        "Contractbeheer Tool (inventarisatie)",
        "Uniformiteit opportunities (sales)"
    ]
}

# Maak een reverse mapping: project -> categorie (programmas)
project_to_category = {}
for category, projects in projecten.items():
    for project in projects:
        project_to_category[project] = category

# Lijst met medewerkers voor de selectvelden
EMPLOYEES = [
    "Danny Herbig", "Edine Loosman", "Davey Monsuur", "Isa Dubbelman", "Rick Valentijn"
    # Voeg hier je medewerkers toe...
]

# Definieer het database model
class Project(db.Model):
    __tablename__ = 'projects_staging'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    goal_scope = db.Column(db.Text, nullable=False)
    project_leader = db.Column(db.String(50), nullable=False)
    stakeholder_hours = db.Column(db.Text, nullable=False)
    programmas = db.Column(db.String(100), nullable=True)

# --- Definieer het hoofdformulier ---
class StakeholderEntryForm(FlaskForm):
    stakeholder = SelectField('Stakeholder', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired()])
    hours = FloatField('Aantal Uren', validators=[DataRequired()])

class ProjectForm(FlaskForm):
    project_name = SelectField('Project', choices=[], validators=[DataRequired()])
    goal_scope = TextAreaField('Doel en Scope (SMART)', validators=[DataRequired()])
    project_leader = SelectField('Projectleider', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired()])
    stakeholder_entries = FieldList(FormField(StakeholderEntryForm), min_entries=0, max_entries=50)
    
    # Voeg programmas als readonly veld toe
    programmas = StringField('Programma', render_kw={"readonly": True})  # readonly zodat het niet door de gebruiker bewerkt kan worden
    
    submit = SubmitField('Project indienen')


# Route voor het formulier
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProjectForm()

    # Dynamisch aanpassen van projecten op basis van geselecteerd project
    if form.project_name.data:
        selected_project = form.project_name.data
        programmas = project_to_category.get(selected_project, "")
    else:
        programmas = ""

    # Dynamisch vullen van de projecten afhankelijk van de projecten dictionary
    project_choices = [(project, project) for project in sum(projecten.values(), [])] # Alle projecten
    form.project_name.choices = project_choices

    if form.validate_on_submit():
        # Bepaal het gekoppelde programma op basis van het gekozen project
        selected_project = form.project_name.data
        associated_programmas = project_to_category.get(selected_project, "")
        # Voeg het bijbehorende programma toe aan het project
        programmas = associated_programmas

        try:
            project_name = selected_project
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
                project.programmas = programmas
            else:
                project = Project(
                    project_name=project_name,
                    goal_scope=goal_scope,
                    project_leader=project_leader,
                    stakeholder_hours=json.dumps(stakeholder_hours),
                    programmas=programmas
                )
                db.session.add(project)

            db.session.commit()
            flash('Projectgegevens succesvol opgeslagen!', 'success')
            logger.info("Project '%s' opgeslagen met stakeholders: %s en programmas: %s", project_name, stakeholder_hours, programmas)
            return redirect(url_for('index'))
        except Exception as e:
            logger.error("Fout bij het opslaan van projectgegevens: %s", str(e))
            traceback.print_exc()
            flash('Fout bij het opslaan: ' + str(e), 'error')
            db.session.rollback()
            return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)
    return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)

# Start de applicatie
if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=False, use_reloader=False)