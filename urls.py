from django.urls import path
from .views import user_views, feedback_views, analysis_views

urlpatterns = [
    # USER API'S
    path('user_register/', user_views.user_register, name='user_register'),
    path('user_login/', user_views.user_login, name='user_login'),
    path('user_details/', user_views.get_user_details, name='user_detail'),

    # FEEDBACK API'S
    path('add_feedback/', feedback_views.add_feedback_view, name='add_feedback'),
    path('toggle_publish_feedback/', feedback_views.toggle_publish_feedback_view, name='toggle_publish_feedback'),
    path('get_feedbacks/', feedback_views.get_all_feedbacks_view, name='get_all_feedbacks'),
    path('get_user_feedbacks/', feedback_views.get_feedbacks_view, name='get_feedbacks'),

    # ANALYSIS API'S
    path('analyze_resume/', analysis_views.analyze_resume, name='analyze_resume'),
]

