from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge.db'
db = SQLAlchemy(app)

from datetime import datetime

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    answers = db.relationship('Answer', backref='question', lazy=True)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template('home.html', questions=questions)

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        question = Question(title=title, content=content)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('ask.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def view_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        content = request.form['content']
        answer = Answer(content=content, question_id=question.id)
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('view_question', question_id=question.id))
    return render_template('question.html', question=question)
@app.route('/question/<int:question_id>/rate_answer/<int:answer_id>/<int:delta>', methods=['POST'])
def rate_answer(question_id, answer_id, delta):
    answer = Answer.query.get_or_404(answer_id)
    answer.rating += delta
    db.session.commit()
    return redirect(url_for('view_question', question_id=question_id))

if __name__ == '__main__':
    app.run(debug=True)
