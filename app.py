from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File paths
internship_data_path = r"C:\Users\Admin\Desktop\internship_data.csv"
student_data_path = r"C:\Users\Admin\Desktop\Student_data.csv"

# Read internship data with encoding
internship_df = pd.read_csv(internship_data_path, encoding='ISO-8859-1')

# Store student data
def save_student_data(data):
    student_df = pd.DataFrame(data, index=[0])
    student_df.to_csv(student_data_path, mode='a', header=False, index=False)

# Home page
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            'Name': request.form['name'],
            'Institution': request.form['institution'],
            'Category': request.form['category'],
            'Email': request.form['email'],
            'Contact Info': request.form['contact'],
            'Gender': request.form['gender'],
            'Area of Interest': request.form['interest'],
            'Nationality': request.form['nationality'],
            'Physically Handicapped': request.form['handicapped'],
            'Academic Qualifications': request.form['qualifications'],
            'Preferred Locations': request.form['locations'],
            'Skills': request.form['skills'],
            'Languages Known': request.form['languages']
        }
        save_student_data(user_data)
        return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == 'password123':
            session['username'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        skills = request.form['skills']
        location = request.form['location']

        # Recommendation logic using CountVectorizer and cosine_similarity
        internship_df['combined'] = internship_df['Skills Required'] + ' ' + internship_df['Location']
        cv = CountVectorizer()
        count_matrix = cv.fit_transform(internship_df['combined'])
        user_query = skills + ' ' + location
        user_vector = cv.transform([user_query])
        cosine_sim = cosine_similarity(user_vector, count_matrix)
        similar_indices = cosine_sim[0].argsort()[-5:][::-1]  # Top 5 recommendations

        recommendations = internship_df.iloc[similar_indices].to_dict('records')
        return render_template('recommendations.html', internships=recommendations)
    
    return render_template('dashboard.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
