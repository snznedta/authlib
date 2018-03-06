from authlib.specs.rfc6749 import InvalidRequestError
from authlib.specs.rfc6749.util import scope_to_list


class OpenIDMixin(object):
    RESPONSE_TYPES = []

    @classmethod
    def check_authorization_endpoint(cls, request):
        if is_openid_request(request, cls.RESPONSE_TYPES):
            # http://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
            request._data_keys.update({
                'response_mode', 'nonce', 'display', 'prompt', 'max_age',
                'ui_locales', 'id_token_hint', 'login_hint', 'acr_values'
            })
            return True

    def validate_authorization_redirect_uri(self, client):
        if not self.redirect_uri:
            raise InvalidRequestError(
                'Missing "redirect_uri" in request.',
            )

        if not client.check_redirect_uri(self.redirect_uri):
            raise InvalidRequestError(
                'Invalid "redirect_uri" in request.',
                state=self.request.state,
            )

    def validate_nonce(self, required=False):
        nonce = self.request.nonce
        if not nonce:
            if required:
                raise InvalidRequestError(
                    'Missing "nonce" in request.'
                )
            return True
        if not hasattr(self.server, 'exists_nonce'):
            raise RuntimeError(
                'The "AuthorizationServer" MUST define '
                'an "exists_nonce" method.'
            )
        if self.server.exists_nonce(nonce, self.request):
            raise InvalidRequestError('Replay attack')


def is_openid_request(request, response_types):
    if request.response_type not in response_types:
        return False
    return 'openid' in scope_to_list(request.scope)
