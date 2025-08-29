from django.urls import path
from . import views

urlpatterns = [
    path('', views.webpage_content_view, name='home'),
    path('blog/public/', views.public_blog_list, name='public_blog_list'),
    path('blog/public/<slug:slug>/', views.public_blog_detail, name='public_blog_detail'),
    path('webpage/', views.webpage_content_view, name='webpage'),
    path('detect/', views.index, name='detect'),
    path('compare/', views.twofilecompare1, name='compare'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('add_document/', views.add_document, name='add_document'),
    path('dataset/manage/', views.manage_dataset, name='manage_dataset'),
    path('dataset/train/', views.train_dataset, name='train_dataset'),
    
    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/check-plagiarism/', views.check_blog_plagiarism, name='check_blog_plagiarism'),
    path('blog/my-posts/', views.blog_my_posts, name='blog_my_posts'),
    path('blog/compare/', views.blog_compare, name='blog_compare'),
    path('blog/admin/', views.blog_admin, name='blog_admin'),
    path('blog/admin/approve/<slug:slug>/', views.blog_approve, name='blog_approve'),
    path('blog/admin/reject/<slug:slug>/', views.blog_reject, name='blog_reject'),
    path('blog/admin/delete/<slug:slug>/', views.blog_delete, name='blog_delete'),
    path('blog/admin/categories/', views.blog_category_manage, name='blog_category_manage'),
    path('blog/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]