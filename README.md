# Instructions for development
1. Clone the repository in any directory of your choosing.
```
git clone https://github.com/Anthuang/ublog.git
```
2. Install Google App Engine [here](https://cloud.google.com/appengine/docs/standard/python/download).
3. Open a terminal and go to the project folder containing the repo.
4. Type the following command in the terminal to run the project:
```
dev_appserver.py .
```
5. Open browser and go to localhost:8080 to view the site.

# Instructions for deploying
1. Open a terminal and go to the project folder containing the repo.
2. Type the following command in the terminal:
```
gcloud app deploy
```
3. To see the site, go to the url in the terminal or run the following command:
```
gcloud app browse
```
