#!/usr/bin/env python3
from bottle import route, run, request, HTTPError
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()

class Albums(Base):
    """Описывает структуру таблицы album для хранения записей"""
    __tablename__ = "album"
    id = sa.Column(sa.INTEGER, primary_key = True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)

def connect_db():
    engine = sa.create_engine(DB_PATH)
    session = sessionmaker(engine)
    return session()


@route("/albums")
def albums():
    """ Возвращает количество и список альбомов выбранной группы"""
    artist_name = request.query.artist
    session = connect_db()
    albums_list = session.query(Albums).filter(Albums.artist == artist_name).all()
    album_string = ""
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist_name)
        result = HTTPError(404, message)
    else:
        album_names = [album.album for album in albums_list]
        for item in album_names:
            album_string += "<li>" + item + "</li>"
            result = "<H1>Список альбомов</H1> <h2>{}</h2>\n".format(artist_name)
            result += "\n" + "<ul>" + album_string + "</ul>" + "Всего альбомов " + str(len(album_names))
    return result


@route("/")
def index_page():
    """Возвращает на стартовую страницу список групп из базы данных"""
    session = connect_db()
    albums_list = session.query(Albums).all()
    artist_names = ""
    artist_list = set([album.artist for album in albums_list])
    for item in artist_list:
        artist_names += "<li><a href = "+ '"' +"/albums?artist=" + item + '"''>' + item + "</a></li>"
        result = "<H1>Список групп</H1>"
        result += "\n" + "<ul>" + artist_names + "</ul>" + '<form action="/add"><button>Добавить запись</button></form>'
    return result


@route("/add")
def post_form():
    #"""Возвращает html формы запроса для добавления нового альбома"""
    return """
    <form action = "/albums" method = "post">
    Artist: <input name = "artist" type = "text" required/>
    Album: <input name = "album" type = "text" required/>
    Year: <input name = "year" type = "number" required/>
    Genre: <input name = "genre" type = "text" required/>
    <input value = "Send" type = "submit" />
    </form>
    """


@route("/albums", method = "POST")
def save_to_db():
    """ Проверяет существование альбома группы в базе.
    Создает объект класса и сохраняет в базе.
    """
    artist = request.forms.artist
    album = request.forms.album
    year = request.forms.year
    genre = request.forms.genre
    session = connect_db()
    albums_list = session.query(Albums).filter(
                Albums.album == album).filter(
                Albums.artist == artist).all()
   
    if albums_list:
        message = "У группы уже есть альбом с таким названием"
        result = HTTPError(409, message)
        return result
    elif artist == "" or album == "" or year == "" or genre == "":
        message = "Заполнены не все поля формы"
        result = HTTPError(409, message)
        return result
    elif year.isdigit() is False:
        message = "Указанный год не является числом"
        result = HTTPError(409, message)
        return result
    else:
        new_album = Albums(
        artist = artist,
        album = album,
        year = year,
        genre = genre
        )
        
        session.add(new_album)
        session.commit()
        return "<h2>Сохранено</h2>"
    
        


def main():
    http_server()

def http_server(): 
    print("Сервер запущен")
    run(host = "localhost", port = 8080, debug=True)
    

if __name__ == "__main__":
    main()