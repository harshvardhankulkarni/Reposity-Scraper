import pandas
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, flash, send_from_directory, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
URL = 'https://github.com'


def repository_scraper(git_id: str):
    try:
        content = requests.get(f"{URL}/{git_id}/?tab=repositories").text
        soup = BeautifulSoup(content, 'html.parser')
        repo_count = int(soup.find(name='span', class_='Counter').getText())
        repositories = soup.select(selector='.wb-break-all a')
        repo_names = [tag.getText().strip() for tag in repositories]
        repo_links = [f"{URL}{tag.get('href')}" for tag in repositories]
        if len(repo_names) < repo_count:
            i = 2
            while len(repo_names) < repo_count:
                content = requests.get(f"{URL}/{git_id}/?page={i}&tab=repositories").text
                soup = BeautifulSoup(content, 'html.parser')
                repositories = soup.select(selector='.wb-break-all a')
                repo_names.extend([tag.getText().strip() for tag in repositories])
                repo_links.extend([f"{URL}{tag.get('href')}" for tag in repositories])
                i += 1
        return repo_names, repo_links
    except Exception:
        return None, None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        github_id = request.form.get('github-id')
        names, links = repository_scraper(github_id)
        if names is None and links is None:
            flash('User Not Found!')
        else:
            data_dict = {
                'Name': names,
                'Link': links,
            }
            data = pandas.DataFrame(data_dict)
            data.to_csv(f'Repositories/{github_id}.csv', index=False)
            flash(f'<a href="/downloads/{github_id}" class="font-bold">{github_id}</a> Download CSV File')
        return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/downloads/<name>')
def downloads(name):
    return send_from_directory('Repositories', f'{name}.csv')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
