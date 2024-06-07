#views.py

from datetime import datetime
from flask import render_template, redirect, url_for, request, flash,Flask
from app import app, db
from flask_login import current_user, login_required
from . import app
from .models import db, User, Blogs, Newsletter
from flask_login import current_user, login_required



@app.route('/')
def main():
    blogs = Blogs.query.all()

   # Her blog için kullanıcı bilgilerini al
    for blog in blogs:
        # İlgili kullanıcıyı sorgula
        user = User.query.filter_by(id=blog.author_id).first()
        
        image_url = url_for('static', filename=f'assets/images/blog-photos/{blog.category}.jpg')
        blog.image_url = image_url
        # Kullanıcı bilgilerini blog nesnesine ekle
        if user:
            blog.author_username = user.username
            blog.author_photograph = user.photograph
    return render_template('main.html', blogs=blogs)

@app.route('/blog/<string:category_name>')
def category_blogs(category_name):
    # Belirli bir kategoriye sahip olan diğer blogları bul
    blogs = Blogs.query.filter_by(category=category_name).all()

    
     # Her blog için kullanıcı bilgilerini al
    for blog in blogs:
        # İlgili kullanıcıyı sorgula
        user = User.query.filter_by(id=blog.author_id).first()
        image_url = url_for('static', filename=f'assets/images/blog-photos/{blog.category}.jpg')
        blog.image_url = image_url
        
        # Kullanıcı bilgilerini blog nesnesine ekle
        if user:
            blog.author_username = user.username    
            blog.author_photograph = user.photograph
    return render_template('main.html', blogs=blogs)


@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    # Blogu veritabanından al
    blog = Blogs.query.get(blog_id)
    if blog:
        blog.views += 1         # Görüntülenme sayısını bir arttır
        db.session.commit()     # Değişiklikleri veritabanına kaydet
        image_url = url_for('static', filename=f'assets/images/blog-photos/{blog.category}.jpg')
        blog.image_url = image_url
        return render_template('blog_page.html', blog=blog)
    else:
        return redirect(url_for('main'))    # Blog bulunamazsa ana sayfaya yönlendir


@app.route('/myProfile')
@login_required
def my_profile():
    # Mevcut kullanıcının user_id'si ile eşleşen bütün blogları al
    user_blogs = Blogs.query.filter_by(author_id=current_user.id).all()
    for blog in user_blogs:
        blog.image_url = url_for('static', filename=f'assets/images/blog-photos/{blog.category}.jpg')
    return render_template('myProfile.html', user=current_user, user_blogs=user_blogs)


@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            current_user.save_profile_image(image)
            flash('Profil resmi başarıyla yüklendi.', 'success')
        else:
            flash('Bir resim seçmelisiniz.', 'danger')
    return redirect(url_for('my_profile'))


@app.route('/delete_profile_image', methods=['POST'])
def delete_profile_image():
    current_user.delete_profile_image()
    flash('Profil resmi başarıyla silindi.', 'success')
    return redirect(url_for('my_profile'))

@app.route('/edit_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    blog = Blogs.query.get_or_404(blog_id)

    # Sadece blog sahibinin düzenlemesine izin ver
    if blog.author_id != current_user.id:
        flash('Bu blog yazısını düzenleme yetkiniz yok.', 'danger')
        return redirect(url_for('main'))

    if request.method == 'POST':
        blog.title = request.form['title']
        blog.subtitle = request.form['subtitle']
        blog.category = request.form['category']
        blog.reading_time = request.form['reading_time']
        blog.content = request.form['content']
        
        db.session.commit()
        flash('Blog yazısı başarıyla güncellendi.', 'success')
        return redirect(url_for('my_profile'))
    
    return render_template('blog_edit.html', blog=blog)


@app.route('/delete_blog/<int:blog_id>', methods=['POST' , 'DELETE'])
@login_required
def delete_blog(blog_id):
    blog = Blogs.query.get_or_404(blog_id)

    # Sadece blogun sahibi tarafından silinebilir
    if blog.author_id != current_user.id:
        flash('Bu blog yazısını silme yetkiniz yok.', 'danger')
        return redirect(url_for('main'))

    try:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog başarıyla silindi.', 'success')
    except:
        db.session.rollback()
        flash('Blog silinirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
    finally:
        db.session.close()

    return redirect(url_for('my_profile'))


@app.route('/submit_blog', methods=['GET', 'POST'])
@login_required  # Sadece oturum açmış kullanıcılar bu görünüme erişebilir
def submit_blog():
    if request.method == 'POST':
        # Formdan gelen verileri al
        title = request.form['title']
        subtitle = request.form['subtitle']
        category = request.form['category']
        reading_time = request.form['reading_time']
        content = request.form['content']

        # Oturum açmış olan kullanıcının kimliğini al
        author_username = current_user.username

        # Kullanıcı adını kullanarak ilgili kullanıcının id'sini al
        user = User.query.filter_by(username=author_username).first()
        author_id = user.id

        # Yeni bir blog nesnesi oluştur ve publish_date ve views değerlerini ayarla
        new_blog = Blogs(title=title, subtitle=subtitle, category=category, reading_time=reading_time,
                         content=content, author_id=author_id, author_username=author_username,
                         publish_date=datetime.now(), views=0)

        # Veritabanına ekle ve değişiklikleri kaydet
        db.session.add(new_blog)
        db.session.commit()

        # Gönderim işlemi tamamlandıktan sonra ana sayfaya yönlendir
        return redirect(url_for('main'))

    # GET isteği geldiğinde blog gönderme formunu göster
    return render_template('/blog_submit.html')


@app.route('/subscribe_newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form['email']
    message = request.form['message']
    
    new_subscription = Newsletter(email=email, message=message)
    db.session.add(new_subscription)
    db.session.commit()
    
    return redirect(url_for('main'))  # Abonelik sonrası yönlendirilecek sayfa
