from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView
from tsg.settings import DEBUG


def callback_url() -> str:
    if DEBUG:
        return "http://localhost:8080/login"
    return "https://www.thesharegame.com/login"


class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = callback_url()
    client_class = OAuth2Client
