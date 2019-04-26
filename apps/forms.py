# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from wtforms import Form


class BaseForm(Form):
    def get_error(self):
        message = None
        print(self.errors)
        if self.errors == {}:
            pass
        else:
            message = self.errors.popitem()[1][0]
        return message

    def validate(self):
        return super(BaseForm, self).validate()