from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import current_app
from flask_login import UserMixin
from werkzeug.utils import secure_filename
import os

class User(UserMixin, db.Model):
    table_args = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    fav_blogs = db.relationship('Blogs', secondary='user_fav_blogs', backref='favorited_by')
    photograph = db.Column(db.String(255))  # Dosya yolu için String tipinde bir sütun

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save_profile_image(self, image):
        # Resim adını güvenli hale getir
        filename = secure_filename(image.filename)
        
        # Dosya uzantısını kontrol et ve jpg veya jpeg ise devam et, değilse hata ver
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            raise ValueError("Yalnızca JPG veya JPEG dosyaları kabul edilmektedir.")

        # Kullanıcının dosya yolunu oluştur
        user_image_folder = os.path.join(current_app.root_path, 'static', 'assets', 'images', 'user-images')
        os.makedirs(user_image_folder, exist_ok=True)

        # Yeni dosya adını oluştur
        new_filename = self.username + '.jpg'
        file_path = os.path.join(user_image_folder, new_filename)

        # Resmi kaydet
        image.save(file_path)

        # Dosya yolunu veritabanına kaydet
        self.photograph = os.path.join('/static', 'assets', 'images', 'user-images', new_filename)
        db.session.commit()  # Veritabanındaki değişiklikleri kaydet

    def delete_profile_image(self):
        # Profil resmini silmek için
        user_image_folder = os.path.join(current_app.root_path, 'static', 'assets', 'images', 'user-images')
        image_path = os.path.join(user_image_folder, f'{self.username}.jpg')
        if os.path.exists(image_path):
            os.remove(image_path)
        self.photograph = None
        db.session.commit()  # Veritabanındaki değişiklikleri kaydet


# Ara tablo tanımı
user_fav_blogs = db.Table('user_fav_blogs',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id'))
)

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Kullanıcının ID'sini referans alır
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    reading_time = db.Column(db.Integer, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)
    views = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(2000), nullable=False)

    @property
    def author_username(self):
        return self.author.username if self.author else None

    @property
    def author_photograph(self):
        return self._author_photograph

    @author_photograph.setter
    def author_photograph(self, value):
        self._author_photograph = value

    @author_username.setter
    def author_username(self, username):
        self.author = User.query.filter_by(username=username).first()

    def __repr__(self):
        return '<Blog {}>'.format(self.title)
    

class Newsletter(db.Model):
    __tablename__ = 'Newsletter'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Newsletter {self.username}>'
