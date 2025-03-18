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
 
# Lijst met medewerkers voor de selectvelden
EMPLOYEES = [
    "Danny Herbig",
    "Edine Loosman",
    "Davey Monsuur",
    "Isa Dubbelman",
    "Rick Valentijn",
    "Eric Methorst",
    "Jan van der Doe",
    "Theun van der Veeken",
    "Rawane el Hafiane",
    "Nooren Vloeren",
    "Sjors Koning",
    "Ine van de Wiel-Brok",
    "Asma el Jari",
    "Brigitte Bartelen",
    "Bob Vriends",
    "Serpil Sekman",
    "Susanne Westerman",
    "Ad Ultima",
    "Denia Dircken",
    "Ron Wallegie",
    "Peter Schepers",
    "Priscilla Wesel",
    "Maarten Goosink",
    "Jelka Beliën",
    "Kent Hollander",
    "Bas Pool",
    "Melissa Verspeek",
    "Fabio Palinckx",
    "Mikki van Hek",
    "Brigitte Beekman",
    "Erik van den Boomen",
    "Joelle Lückerath",
    "Eva Kommers",
    "Tim van de Luijtgaarden",
    "Rick van Beek",
    "Marcelina Peksa",
    "Dylan Schneijderberg",
    "Robin Heeren",
    "Elise Pieterse",
    "Yaren Baysal",
    "Ilona de Vogel",
    "Keuken Inkoop",
    "Tijn Verbeek",
    "Scott Gerrese",
    "Rumeysa Yazici",
    "Danique de Boer",
    "Bart de Rammelaere",
    "Danny Pruysen",
    "Arian Nefs",
    "Kim Videler",
    "Quincy Lindeborg",
    "Wanshika Ramcharan",
    "Fouad Ali",
    "Bart van de Casteel",
    "Eren Can",
    "Tobias Bosch",
    "Karlijn Poos",
    "Hayat Boukhriss",
    "Dwight Cornel",
    "Rachelle Visser",
    "Jeroen Schagen",
    "Berdy Fokkema",
    "Theun van der Veeken",
    "Kim Herijgers",
    "Stephanie van Kaam",
    "Admin Auperle",
    "Wassim Bouazza",
    "Antoinette Weerdenburg",
    "Thijs Berg",
    "Jack Nooren",
    "Ismahan Ozkurt",
    "Mustafa Gumus",
    "Bryan Helms",
    "Yigit Kocaaga",
    "Sjoerd Verdonck",
    "Sedat Can",
    "Koen Franken",
    "Felizia Geurts",
    "Job Nieuwstraten",
    "Thob van Kaam",
    "Annemarie Lammertsma",
    "Joke Landtmeters",
    "Kyra Lima",
    "Joey Rovers",
    "Orkun Akdemir",
    "Maxaro Keukens",
    "Daphne Keeris",
    "Martin Ultee",
    "Martin Sweere",
    "Milan van Beurden",
    "Tugba Turan",
    "Marvin Hazeleger",
    "Dirk van den Broek",
    "Isetta Sekreve",
    "Aman Samoedj",
    "Virtual Entity",
    "Esra Schagen",
    "Tegel Inkoop",
    "Britt van Lieshout",
    "Luuk Staps",
    "Theresia de Reus - Van der Geer",
    "Joost Schoone",
    "Rico Sterrenberg",
    "Roos van't Veer",
    "Jimmy Havermans",
    "Trevor van Luijk",
    "Joey van Merode",
    "Lisa Boere",
    "Carolina Quelhas",
    "sa backup",
    "Jesse Biney",
    "Melisa Schagen",
    "Jorrit Nooren",
    "Quinn van Munster",
    "Sevval Kalkavan",
    "Dani Westen",
    "Ruben Huijskens",
    "Tirza Sturing",
    "Noa Ellerkamp",
    "Frank Boer",
    "frederic demeilliez",
    "Jorden Kranenburg",
    "Jörgen Zaadnoordijk",
    "Hasina Kamal",
    "Sofia Maiga",
    "Amel Loukili",
    "Armine van Veldhuizen",
    "Giovanny Berkers",
    "Christiaan Stemgèe",
    "Remon Awanis",
    "Efe Karakoç",
    "Ben Antiri",
    "Annemeyn Ernst",
    "Ruthjedi-Ann Offerman",
    "Lennard Bakhuys",
    "Dwight Cornel",
    "Julien Vianen",
    "Admin Veeken",
    "Simone Roig",
    "Sjoerd Thomas",
    "Beau Drijdijk",
    "Ingrid Broers",
    "Thomas de Bruin",
    "Hilde Hendriks",
    "Nienke Rutgers",
    "Daan Helmons",
    "Niels Verburgh",
    "Natascha Smet",
    "Sjoerd van Nijnatten",
    "Conny Hulsebosch",
    "Quinty Thakoersingh",
    "Jurriaan Bisschop",
    "Maxaro Transport",
    "adm mouwen",
    "Chynthia Janssen",
    "Mike van den Boom",
    "Dikra Kaddouri",
    "Mischa van der Luit",
    "Abdullah Abdla",
    "Elze Bijl",
    "Serpil Canta - Sekman",
    "Peggy Smit",
    "Marinda Verhage",
    "Sophie van Schilt",
    "Berry Melis",
    "Jessica Dorrestein",
    "Bas Fokkema",
    "Melvin Trilsbeek",
    "Sierra Cornelissen",
    "Björn Zaadnoordijk",
    "Joanna van Berkel - Skrzypek",
    "Priya Sunaina Matadien",
    "Beatrice Mahmoud",
    "Luko Nooren",
    "Admin Schoone",
    "Marloes Mallens",
    "Anouk Resoort",
    "Admin Havermans",
    "Gerarde de Jong",
    "Constantin Juravle",
    "Ray van Tuijl",
    "Lizelinde Verschuuren",
    "Patrick Auperlé",
    "Rob Kramers",
    "Bertram Joosen",
    "Zhand Bakir",
    "Jochen van den Bogart",
    "Weiyuan Liu",
    "Yara Kotta",
    "adm umaresan",
    "Manoj Kumaresan",
    "Adinda Knollenburg",
    "Emil Szczepaniak",
    "Anna Kovacs",
    "SA Avepoint",
    "Rachel van Bavel",
    "Anne Oor",
    "Scribe Integratie",
    "Nebay Gerezgiher",
    "Daan van Pelt",
    "Amber Groen",
    "Jiska Verwijmeren",
    "Info Bouwexpress",
    "Ruben Gil Beco",
    "Corne Nooren",
    "Jurgen van Zundert",
    "Mark Vermeulen",
    "Sjoerd de Grauw",
    "Edwin Damen",
    "May Hassan",
    "Ann De Bal",
    "Damiën Thakoersingh",
    "Nikki Schoonen",
    "Tristan Brand",
    "David van Laarhoven",
    "Maartje Breugelmans",
    "Stijn Meeuwisse",
    "Jimmy Havermans",
    "Container Import",
    "Semih Özkök",
    "Bas de Jong",
    "Rick van Beek",
    "Leanne Rijnen",
    "Teiko Haubrich",
    "John van der Jagt",
    "Shale Shams",
    "Max Renkels",
    "Tim Rauws",
    "Yousra El Mourabit",
    "Maeike Deijkers",
    "Cor Geuze",
    "Sean Radzio",
    "Thijs van Beek",
    "Koen Polus",
    "Lidwien van Aert",
    "Admin Antiri",
    "Sonia Sahim",
    "Giovanni Tadic",
    "Robin Jaspers",
    "Roumaissa Chouay",
    "Ticho Luijks",
    "Dionne Alberts",
    "Tim van Riel",
    "Maxaro Integration",
    "David Buelens",
    "Olivier van der Pol",
    "Emil Szczepaniak"
]
 
# Definieer het database model
class Project(db.Model):
    __tablename__ = 'projects_staging'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    goal_scope = db.Column(db.Text, nullable=False)
    project_leader = db.Column(db.String(50), nullable=False)
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
    stakeholder_entries = FieldList(FormField(StakeholderEntryForm), min_entries=0, max_entries=50)
    submit = SubmitField('Project indienen')
 
# Route voor het formulier
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProjectForm()
    if form.validate_on_submit():
        # Controleer op dubbele stakeholders
        entered_stakeholders = [
            entry.form.stakeholder.data
            for entry in form.stakeholder_entries.entries
            if entry.form.stakeholder.data
        ]
        if len(entered_stakeholders) != len(set(entered_stakeholders)):
            flash("Fout: Dubbele stakeholders zijn niet toegestaan. Verwijder de duplicaten en probeer het opnieuw.", "error")
            # Render opnieuw met behoud van de ingevulde data
            return render_template('templates.html', form=form, employees=EMPLOYEES)
       
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
            return redirect(url_for('index'))
        except Exception as e:
            logger.error("Fout bij het opslaan van projectgegevens: %s", str(e))
            traceback.print_exc()
            flash('Fout bij het opslaan: ' + str(e), 'error')
            db.session.rollback()
            return render_template('index.html', form=form, employees=EMPLOYEES)
    return render_template('index.html', form=form, employees=EMPLOYEES)
 
# Start de applicatie
if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=False, use_reloader=False)