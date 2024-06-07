from flask_admin import AdminIndexView, expose

class MyAdminIndexView(AdminIndexView):
  @expose("/")
  def index(self):
    return self.render("admin/index.html")
  

    