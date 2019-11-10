import connexion

app = connexion.FlaskApp(__name__, specification_dir='conf/')
app.add_api('pypyr-scheduler.v1.yaml', validate_responses=True)
app.run(port=8080)
