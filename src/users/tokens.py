from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.is_active) + str(user.pk) + str(timestamp)


activation_token_generator = AccountActivationTokenGenerator()
