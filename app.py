import github.GithubException
from werkzeug.exceptions import HTTPException
from typing import Dict
from github import Github
from flask import Flask, jsonify, abort

APP_URL = 'https://github-api-mskrzypczak.herokuapp.com/'

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
g = Github()


class UserDataRetriever(object):
    @property
    def username(self):
        return self.__username

    @property
    def user(self):
        return self.__user

    @property
    def repositories(self):
        return self.__repositories

    @property
    def stars_sum(self):
        return sum(self.__repositories.values())

    @username.setter
    def username(self, value):
        self.__username = value

    @user.setter
    def user(self, value):
        self.__user = value

    @repositories.setter
    def repositories(self, value):
        self.__repositories = value

    @stars_sum.setter
    def stars_sum(self, value):
        self.__stars_sum = value

    def __init__(self, username: str):
        self.username = username
        self.stars_sum: int = 0
        self.repositories: Dict[str, int] = {}

        try:
            self.user = g.get_user(username)
        except github.GithubException:
            self.user = None

        self.__fetch_repositories()

    def __fetch_repositories(self):
        if self.user:
            self.repositories = {repo.name: repo.stargazers_count for repo in self.user.get_repos()}

    def to_json(self):
        return jsonify({
            "username": self.username,
            "stars_sum": self.stars_sum,
            "repositories": self.repositories
        })


@app.route('/user-summary/<string:username>', methods=['GET'])
def get(username):
    user_data = UserDataRetriever(username)
    if user_data.user is None:
        abort(404, description=f"User {username} does not exist")
    return user_data.to_json(), 200


@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": f"To get the information about any GitHub user simply add his username after '{APP_URL}user-summary/'",
        "example": f"{APP_URL}user-summary/MikeCreator-put"}), 200


@app.errorhandler(HTTPException)
def handle_exception(e):
    response = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    return response, e.code


if __name__ == '__main__':
    app.run()
