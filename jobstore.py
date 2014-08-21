from flask import Flask, render_template,jsonify, request, Response
from flask.ext.sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['OPENSHIFT_POSTGRESQL_DB_URL']
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

class Job(db.Model):
	__tablename__ = 'jobs'
	id = db.Column(db.Integer(), primary_key=True)
	title = db.Column(db.String(64), index=True, nullable=False)
	description = db.Column(db.Text())
	posted_at = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
	company = db.Column(db.String(100), nullable=False)

	def __repr__(self):
		return 'Job %s' % self.title

	def to_json(self):
		job_json = {
			'id' : self.id,
			'title': self.title,
			'description' : self.description,
			'posted_at' : self.posted_at,
			'company':self.company
		}
		return job_json


	@staticmethod
	def from_json(job_json):
		title = job_json.get('title')
		description = job_json.get('description')
		return Job(title=title, description=description)


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/api/v1/jobs')
def all_jobs():
	jobs = Job.query.all()
	return jsonify({'jobs':[job.to_json() for job in jobs]})

@app.route('/api/v1/jobs', methods=['POST'])
def post_job():
	job = Job.from_json(request.json)
	db.session.add(job)
	db.session.commit()
	return jsonify(job.to_json()) , 201

if __name__ == '__main__':
	app.run(debug=True)