class DummyTranslator:
    def get(self, key, **kwargs):
        # Fallback dictionary for common keys
        strings = {
            'register.password': 'Password',
            'register.first_name': 'First Name',
            'register.last_name': 'Last Name',
            'register.browser_start': 'Starting Browser',
            'register.email_create_failed': 'Email creation failed',
            'register.email_setup_failed': 'Email setup failed',
            'register.register_start': 'Starting Registration',
            'register.total_usage': 'Total Usage',
            'register.get_token': 'Waiting for Session Token',
            'register.token_success': 'Token Acquired!',
            'register.update_cursor_auth_info': 'Injecting Token',
            'register.cursor_auth_info_updated': 'Token Injected',
            'register.reset_machine_id': 'Resetting Machine ID (Disabled in Auto, doing manually)',
            'register.account_info_saved': 'Account Saved',
            'register.cursor_registration_completed': 'Registration Completed!',
        }
        text = strings.get(key, key)
        for k, v in kwargs.items():
            text += f" [{k}: {v}]"
        return text

translator = DummyTranslator()
