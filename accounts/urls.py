from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views.block_user import BlockUserViewSet
from accounts.views.login import LoginViewSet
from accounts.views.logout import LogoutViewSet
from accounts.views.me import MeViewSet
from accounts.views.otp_verify import OtpVerifyViewSet
from accounts.views.recovery import RecoveryViewSet
from accounts.views.register import RegisterViewSet
from accounts.views.reset_password import ResetPasswordViewSet

router = DefaultRouter()
router.register("register", RegisterViewSet, basename="auth-register")
router.register("login", LoginViewSet, basename="auth-login")
router.register("logout", LogoutViewSet, basename="auth-logout")
router.register("recovery", RecoveryViewSet, basename="auth-recovery")
router.register("otp-verify", OtpVerifyViewSet, basename="auth-otp-verify")
router.register("reset-password", ResetPasswordViewSet, basename="auth-reset-password")
router.register("block-user", BlockUserViewSet, basename="auth-block-user")
router.register("me", MeViewSet, basename="auth-me")

urlpatterns = [path("refresh/", TokenRefreshView.as_view(), name="token_refresh")]
urlpatterns += router.urls