from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import json
import urllib.parse
import logging
import traceback
import pandas as pd
import numpy as np

# Lees de data
data = pd.read_csv('data/Portfolio 2025(Portfolio 2025).csv', sep=";", skiprows=4)
data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
data.iloc[:, 0] = data.iloc[:, 0].ffill()
data = data[data["Programma's"] == 'Q2']
data = data[['Digitale klantreis', 'Klantsucces', 'Marketingtransformatie', 'Digitale transformatie']]
df_dict = data.to_dict(orient="list")
df_dict_clean = {key: [value for value in values if not (isinstance(value, float) and np.isnan(value))] for key, values in df_dict.items()}

# Configureer logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialiseer Flask-app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5'

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
    logger.info("Database URI geconfigureerd")
except Exception as e:
    logger.error("Fout bij configureren database URI: %s", str(e))
    raise

# Initialiseer database
db = SQLAlchemy(app)

# Projecten en mapping
projecten = df_dict_clean
project_to_category = {project: category for category, projects in projecten.items() for project in projects}

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

# Database model
class Project(db.Model):
    __tablename__ = 'projects_staging'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    goal_scope = db.Column(db.Text, nullable=False)
    project_leader = db.Column(db.String(50), nullable=False)
    stakeholder_hours = db.Column(db.Text, nullable=False)
    programmas = db.Column(db.String(100), nullable=True)

# Formulieren
class StakeholderEntryForm(FlaskForm):
    stakeholder = SelectField('Stakeholder', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired(message="Selecteer een stakeholder")])
    hours = FloatField('Aantal Uren', validators=[DataRequired(message="Vul het aantal uren in")])
    # Schakel CSRF uit voor dit subformulier
    class Meta:
        csrf = False

class ProjectForm(FlaskForm):
    project_name = SelectField('Project', choices=[], validators=[DataRequired(message="Selecteer een project")])
    goal_scope = TextAreaField('Projectdoelstelling + PBI', validators=[DataRequired(message="Vul de doelstelling in")])
    project_leader = SelectField('Projectleider', choices=[(emp, emp) for emp in EMPLOYEES], validators=[DataRequired(message="Selecteer een projectleider")])
    stakeholder_entries = FieldList(FormField(StakeholderEntryForm), min_entries=1, validators=[DataRequired(message="Voeg minimaal één stakeholder toe")])
    programmas = StringField('Programma', render_kw={"readonly": True})
    submit = SubmitField('Project indienen')

# Route
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ProjectForm()
    project_choices = [(project, project) for project in sum(projecten.values(), [])]
    form.project_name.choices = project_choices

    # Stel programma in op basis van geselecteerd project
    if form.project_name.data:
        selected_project = form.project_name.data
        form.programmas.data = project_to_category.get(selected_project, "")
    else:
        form.programmas.data = ""

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                # Haal gegevens op
                project_name = form.project_name.data
                goal_scope = form.goal_scope.data
                project_leader = form.project_leader.data
                programmas = project_to_category.get(project_name, "")

                # Controleer stakeholder-uren en zoek naar duplicaten
                stakeholder_hours = {}
                stakeholders_seen = set()  # Houd bij welke stakeholders al zijn ingevoerd
                for entry in form.stakeholder_entries.entries:
                    stakeholder = entry.form.stakeholder.data
                    hours = entry.form.hours.data
                    if stakeholder and hours is not None:
                        # Controleer op duplicaten
                        if stakeholder in stakeholders_seen:
                            flash(f"Dubbele stakeholder '{stakeholder}' gedetecteerd. Pas het formulier aan om duplicaten te vermijden.", "error")
                            return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)
                        stakeholders_seen.add(stakeholder)
                        stakeholder_hours[stakeholder] = hours
                    else:
                        flash("Alle stakeholder-velden moeten volledig ingevuld zijn.", "error")
                        return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)

                # Controleer of er minimaal één stakeholder is
                if len(stakeholders_seen) != len(form.stakeholder_entries.entries):
                    flash("Voeg minimaal één stakeholder met uren toe en zorg ervoor dat er geen duplicaten zijn.", "error")
                    return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)

                # Database logica
                project = Project.query.filter_by(project_name=project_name).first()
                if project:
                    current_hours = json.loads(project.stakeholder_hours)
                    current_hours.update(stakeholder_hours)
                    project.stakeholder_hours = json.dumps(current_hours)
                    project.goal_scope = goal_scope
                    project.project_leader = project_leader
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
                logger.info("Project '%s' opgeslagen met stakeholders: %s", project_name, stakeholder_hours)
                return redirect(url_for('index'))

            except Exception as e:
                logger.error("Fout bij opslaan: %s", str(e))
                flash(f"Fout bij het opslaan: {str(e)}", "error")
                db.session.rollback()
        else:
            # Geef specifieke foutmeldingen weer
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Fout in {field}: {error}", "error")
            logger.warning("Formulier validatie mislukt: %s", form.errors)

    return render_template('index.html', form=form, employees=EMPLOYEES, project_mapping=project_to_category)

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=False, use_reloader=False)