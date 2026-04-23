from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from flower_shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("consultation/", views.consultation, name="consultation"),
    path("card/<int:id>/", views.card, name="card"),
    path('quiz/', views.quiz, name='quiz'),
    path('quiz-step/', views.quiz_step, name='quiz_step'),
    path('result/', views.result, name='result'),
    path("order/<int:id>/", views.order, name="order"),
    path('payment/result/', views.payment_result, name='payment_result'),
    path('payment/webhook/', views.yookassa_webhook, name='yookassa_webhook'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
