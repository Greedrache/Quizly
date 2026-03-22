<h1>Quizly Backend</h1>

<p>
Quizly is a backend service for a quiz platform. This Django-based project provides a REST API
to connect frontend and backend, handling all core functionalities such as user management,
quiz creation, and gameplay.
</p>

<h2>Features</h2>
<ul>
  <li>User registration and authentication</li>
  <li>YouTube video uploads</li>
  <li>Create, update, and delete quizzes</li>
  <li>Play and test quizzes</li>
</ul>

<h2>Tech Stack</h2>
<ul>
  <li>Python 3.14+</li>
  <li>Django 6.0.3</li>
  <li>Django REST Framework 3.16.1</li>
  <li>SQLite (development) / other databases as needed</li>
</ul>

<h2>Setup (Local Development)</h2>

<h3>1. Clone the repository</h3>
<pre><code>git clone https://github.com/Greedrache/Quizly .</code></pre>

<h3>2. Create a virtual environment</h3>
<pre><code>python -m venv venv</code></pre>

<h3>3. Activate the virtual environment</h3>
<p><strong>PowerShell:</strong></p>
<pre><code>venv\Scripts\Activate.ps1</code></pre>

<p><strong>CMD:</strong></p>
<pre><code>venv\Scripts\activate</code></pre>

<p><strong>Linux / macOS:</strong></p>
<pre><code>source venv/bin/activate</code></pre>

<h3>4. Install dependencies</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>4.1 Configure environment variables</h3>
<p>
Please go to the ,,.env,, file and write the following code inside:
</p>
<pre><code>GEMINI_API_KEY = "" # Please enter your Gemini API key here!</code></pre>



<h3>5. Create migrations</h3>
<pre><code>python manage.py makemigrations</code></pre>

<h3>6. Apply migrations</h3>
<pre><code>python manage.py migrate</code></pre>

<h3>7. Start the development server</h3>
<pre><code>python manage.py runserver</code></pre>

<p>
Server runs at:<br>
http://127.0.0.1:8000/
</p>

<h2>Optional</h2>

<p><strong>Create a superuser:</strong></p>
<pre><code>python manage.py createsuperuser</code></pre>

<p><strong>Deactivate the virtual environment:</strong></p>
<pre><code>deactivate</code></pre>

<h2>Troubleshooting</h2>
<ul>
  <li>
    If you encounter activation issues in PowerShell:<br>
    <code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code>
  </li>
  <li>
    If migrations are missing, run:<br>
    <code>python manage.py migrate</code>
  </li>
</ul>
