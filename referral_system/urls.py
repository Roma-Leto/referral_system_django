from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users import views
from users.views import HomePageView, VerifyPhoneNumberView, UserProfileView
from users.views import UserProfileView, ActivateInviteCodeView

schema_view = get_schema_view(
    openapi.Info(
        title="Referral System API",
        default_version='v1',
        description="API простой реферальной системы",
        contact=openapi.Contact(email="imletoroma@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],  # Уровень доступа
)

urlpatterns = [
    # REST API
    path('phone/', views.PhoneNumberView.as_view(), name='phone_number'),
    path('verify/', views.VerificationCodeView.as_view(), name='verify_code'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/<str:username>/activate-invite-code/', views.ActivateInviteCodeView.as_view(),
         name='activate-invite-code'),

    # DOCS
    path('api-auth/', include('rest_framework.urls')),
    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # TEMPLATES
    path('', HomePageView.as_view(), name='home'),  # Главная страница
    path('ui/verify/<str:phone_number>/', VerifyPhoneNumberView.as_view(), name='verify'),
    # Страница ввода кода
    path('ui/profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    # Профиль пользователя
]
