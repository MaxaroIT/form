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
EMPLOYEES = ['Admin Havermans',
 'Robin Jaspers',
 'Britt van Lieshout',
 'Nikki Schoonen',
 'Dirk van den Broek',
 'Dwight Cornel',
 'Joke Landtmeters',
 'Yigit Kocaaga',
 'Bart van de Casteel',
 'Carolina Quelhas',
 'May Hassan',
 'Anna Kovacs',
 'Adinda Knollenburg',
 'Tobias Bosch',
 'Isa Dubbelman',
 'Milan van Beurden',
 'Denia Dircken',
 'Tim van de Luijtgaarden',
 'Gerarde de Jong',
 'Wanshika Ramcharan',
 'Emil Szczepaniak',
 'Rachel van Bavel',
 'Robin Heeren',
 'Koen Franken',
 'Susanne Westerman',
 'Bertram Joosen',
 'Davey Monsuur',
 'Erik van den Boomen',
 'Elise Pieterse',
 'Priscilla Wesel',
 'Maartje Breugelmans',
 'Fabio Palinckx',
 'Mischa van der Luit',
 'Beatrice Mahmoud',
 'Anne Oor',
 'Brigitte Beekman',
 'Antoinette Weerdenburg',
 'Sevval Kalkavan',
 'Edwin Damen',
 'Scott Gerrese',
 'Sierra Cornelissen',
 'Marloes Mallens',
 'Daan van Pelt',
 'Amel Loukili',
 'Thob van Kaam',
 'Priya Sunaina Matadien',
 'Sonia Sahim',
 'Maarten Goosink',
 'Jack Nooren',
 'Natascha Smet',
 'Weiyuan Liu',
 'Martin Sweere',
 'Tugba Turan',
 'Sean Radzio',
 'Stephanie van Kaam',
 'Remon Awanis',
 'Jessica Dorrestein',
 'Martin Ultee',
 'Ben Antiri',
 'Amber Groen',
 'Julien Vianen',
 'Tristan Brand',
 'Lidwien van Aert',
 'Eric Methorst',
 'Yaren Baysal',
 'Rico Sterrenberg',
 'Jimmy Havermans',
 'Marcelina Peksa',
 'Björn Zaadnoordijk',
 'Admin Schoone',
 'Patrick Auperlé',
 'Koen Polus',
 'Bas Fokkema',
 'adm mouwen',
 'Giovanny Berkers',
 'Brigitte Bartelen',
 'Annemarie Lammertsma',
 'Jurgen van Zundert',
 'David Buelens',
 'Marvin Hazeleger',
 'Abdullah Abdla',
 'Rob Kramers',
 'Tim Rauws',
 'Sjoerd van Nijnatten',
 'Mikki van Hek',
 'Tegel Inkoop',
 'Jorden Kranenburg',
 'Armine van Veldhuizen',
 "Roos van't Veer",
 'Luuk Staps',
 'Peter Schepers',
 'Sophie van Schilt',
 'Zhand Bakir',
 'Yousra El Mourabit',
 'Rachelle Visser',
 'Chynthia Janssen',
 'Yara Kotta',
 'Rawane el Hafiane',
 'Leanne Rijnen',
 'Eren Can',
 'Sofia Maiga',
 'Felizia Geurts',
 'Theresia de Reus - Van der Geer',
 'Maxaro Keukens',
 'Maxaro Transport',
 'Bart de Rammelaere',
 'Ruthjedi-Ann Offerman',
 'Bas Pool',
 'Lizelinde Verschuuren',
 'Sjoerd Thomas',
 'Ray van Tuijl',
 'Ruben Huijskens',
 'Ticho Luijks',
 'Job Nieuwstraten',
 'Lisa Boere',
 'Lennard Bakhuys',
 'Damiën Thakoersingh',
 'Christiaan Stemgèe',
 'Peggy Smit',
 'Luko Nooren',
 'Virtual Entity',
 'Danique de Boer',
 'Kim Videler',
 'Danny Herbig',
 'Joelle Lückerath',
 'Rick Valentijn',
 'Jelka Beliën',
 'Berdy Fokkema',
 'Sjoerd Verdonck',
 'Joanna van Berkel - Skrzypek',
 'Stijn Meeuwisse',
 'Manoj Kumaresan',
 'Edine Loosman',
 'Annemeyn Ernst',
 'Marinda Verhage',
 'Nebay Gerezgiher',
 'Anouk Resoort',
 'Jan van der Doe',
 'Fouad Ali',
 'Jiska Verwijmeren',
 'Cor Geuze',
 'Rick van Beek',
 'Teiko Haubrich',
 'Bob Vriends',
 'Olivier van der Pol',
 'Joost Schoone',
 'Rumeysa Yazici',
 'Noa Ellerkamp',
 'Melisa Schagen',
 'Bryan Helms',
 'Esra Schagen',
 'Mike van den Boom',
 'Nooren Vloeren',
 'Roumaissa Chouay',
 'Aman Samoedj',
 'Hayat Boukhriss',
 'Ine van de Wiel-Brok',
 'Serpil Canta - Sekman',
 'Sedat Can',
 'Conny Hulsebosch',
 'Semih Özkök',
 'Ilona de Vogel',
 'Asma el Jari',
 'Giovanni Tadic',
 'Jeroen Schagen',
 'Danny Pruysen',
 'Karlijn Poos',
 'Daphne Keeris',
 'Melissa Verspeek',
 'Dani Westen',
 'Kyra Lima',
 'Bas de Jong',
 'Tirza Sturing',
 'Quinty Thakoersingh',
 'Keuken Inkoop',
 'Trevor van Luijk',
 'Joey Rovers',
 'Theun van der Veeken',
 'Berry Melis',
 'Quinn van Munster',
 'Ismahan Ozkurt',
 'Simone Roig',
 'Nienke Rutgers',
 'Hasina Kamal',
 'Thijs Berg',
 'Beau Drijdijk',
 'Quincy Lindeborg',
 'Ad Ultima',
 'Maeike Deijkers',
 'John van der Jagt',
 'Dikra Kaddouri',
 'Tim van Riel',
 'Max Renkels',
 'Efe Karakoç',
 'Corne Nooren',
 'Isetta Sekreve',
 'Jurriaan Bisschop',
 'Joey van Merode',
 'Jorrit Nooren',
 'Sjoerd de Grauw',
 'Niels Verburgh',
 'Melvin Trilsbeek',
 'Sjors Koning',
 'Tijn Verbeek',
 'Ingrid Broers',
 'Jochen van den Bogart',
 'Dionne Alberts',
 'Mustafa Gumus',
 'Elze Bijl',
 'Kent Hollander',
 'Frank Boer',
 'Hilde Hendriks',
 'Thijs van Beek',
 'Dylan Schneijderberg',
 'Thomas de Bruin',
 'Kim Herijgers',
 'Orkun Akdemir',
 'Shale Shams',
 'Wassim Bouazza',
 'Ann De Bal',
 'Constantin Juravle',
 'Eva Kommers',
 'Ruben Gil Beco',
 'Arian Nefs',
 'Admin Veeken',
 'Jesse Biney',
 'David van Laarhoven',
 'Daan Helmons',
 'Jörgen Zaadnoordijk',
 'Admin Antiri',
 'Mark Vermeulen',
 'Serpil Sekman']

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