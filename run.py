from flask import Flask, render_template, request, redirect, url_for
from MyModules.MyMariaDB import MyDBController
from pprint import pprint

from Recommender import SGRecommender

application = Flask(__name__)

data_ = {}
dbcon = MyDBController('127.0.0.1', 'guest', '0000', 'steam_db')
game_titles = dbcon.getTitles()

@application.route("/")
def root():  
    return render_template("primary.html", titles = game_titles)

@application.route("/recommend", methods=['GET', 'POST'])
def func_get():
    if(request.method == 'GET'):
        user_input = request.args.get('game_list')
        user_input = user_input.split('#')
        if(len(user_input) == 1):
            return redirect(url_for('root'))
        for i in user_input[1:]:
            if(i not in game_titles):
                return redirect(url_for("/"))
        info = [dbcon.getGameIdByTitle(i) for i in user_input[1:]]
        rec = SGRecommender()
        cf_list, cbf_list = rec.recommend(info)
        
        data_['mode'] = 0
        data_['input'] = info
        data_['cf'] = [dbcon.getGameInfo(i) for i in cf_list]
        data_['cbf'] = [dbcon.getGameInfo(i) for i in cbf_list]

        return render_template('index.html', d = data_)
    elif(request.method == 'POST'):
        mode = int(request.form['demo-priority'])  
        info = data_['input']

        rec = SGRecommender()
        cf_list, cbf_list = rec.recommend(info, mode)

        data_['mode'] = mode
        data_['cf'] = [dbcon.getGameInfo(i) for i in cf_list]
        data_['cbf'] = [dbcon.getGameInfo(i) for i in cbf_list]

        return render_template('index.html', d = data_)

if __name__ == "__main__":
    application.run(threaded = True)

