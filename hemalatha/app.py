import os
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Non-GUI backend for Matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'parquet'}

# Users database (for demo purposes)
users_db = {}
with open('users.txt') as f:
    for line in f:
        username, password = line.strip().split(',')
        users_db[username] = password

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Home page (login page)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_db.get(username) == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')


# Dashboard page (file upload)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            session['file_path'] = file_path
            return redirect(url_for('overview'))

        flash('Invalid file type. Please upload a CSV, XLSX, or Parquet file.', 'danger')

    return render_template('dashboard.html')


# Overview page (preview dataset)
@app.route('/overview')
def overview():
    if 'file_path' not in session:
        return redirect(url_for('dashboard'))

    file_path = session['file_path']
    df = load_data(file_path)
    data_preview = df.head(10).to_html(classes="table table-striped table-hover", index=False)

    return render_template('overview.html', data_preview=data_preview)


# Visualization page (select variables and plot)
@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    if 'file_path' not in session:
        return redirect(url_for('dashboard'))

    file_path = session['file_path']
    df = load_data(file_path)
    columns = df.columns.tolist()

    if request.method == 'POST':
        variable1 = request.form['variable1']
        variable2 = request.form['variable2']
        plot_type = request.form['plot_type']
        # Generate the plot based on selected variables and plot type
        plot_path = generate_plot(df, variable1, variable2, plot_type)
        return render_template('visualize.html', columns=columns, plot_path=plot_path)

    return render_template('visualize.html', columns=columns)


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('file_path', None)
    return redirect(url_for('login'))


# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Read CSV file with low_memory=False to avoid DtypeWarning
def load_data(file_path):
    return pd.read_csv(file_path, low_memory=False)


# Plot generation logic
def generate_plot(df, variable1, variable2, plot_type):
    plt.figure(figsize=(8, 6))

    if plot_type == 'bar':
        sns.barplot(x=variable1, y=variable2, data=df)
        plt.title(f'Bar Plot: {variable1} vs {variable2}')

    elif plot_type == 'line':
        sns.lineplot(x=variable1, y=variable2, data=df)
        plt.title(f'Line Plot: {variable1} vs {variable2}')

    elif plot_type == 'scatter':
        sns.scatterplot(x=variable1, y=variable2, data=df)
        plt.title(f'Scatter Plot: {variable1} vs {variable2}')

    else:
        plt.text(0.5, 0.5, 'Invalid Plot Type Selected', ha='center', va='center', fontsize=20, color='red')

    # Save the plot
    plot_path = 'static/plot.png'
    plt.savefig(plot_path)
    plt.close()

    return plot_path


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8080')
