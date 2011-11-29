#  Copyright 2008-2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import wx

from robotide.validators import (ScalarVariableNameValidator,
                                ListVariableNameValidator, TimeoutValidator,
                                NonEmptyValidator, ArgumentsValidator,
                                TestCaseNameValidator, UserKeywordNameValidator)
from robotide import utils
from robotide.context import Font
from robotide.ui.components import StaticText

from robotide.widgets import Dialog
from fieldeditors import ValueEditor, ListValueEditor, MultiLineEditor,\
    ContentAssistEditor, VariableNameEditor
from dialoghelps import get_help


def EditorDialog(obj):
    return globals()[obj.label.replace(' ', '') + 'Dialog']


class _Dialog(Dialog):
    _title = property(lambda self: utils.name_from_class(self, drop='Dialog'))

    def __init__(self, controller, item=None, plugin=None):
        # TODO: Get rid of item, everything should be in controller
        Dialog.__init__(self, self._title)
        self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
        self._controller = controller
        self.plugin = plugin
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._editors = self._get_editors(item)
        for editor in self._editors:
            self._sizer.Add(editor, editor.expand_factor, wx.EXPAND)
        self._add_comment_editor(item)
        self._create_help()
        self._create_line()
        self._create_buttons()
        self.SetSizer(self._sizer)
        self._sizer.Fit(self)
        self._editors[0].set_focus()

    def _add_comment_editor(self, item):
        self._comment_editor = ValueEditor(self, item.comment if item else '',
                                           'Comment')
        self._sizer.Add(self._comment_editor)

    def _create_line(self):
        line = wx.StaticLine(self, size=(20,-1), style=wx.LI_HORIZONTAL)
        self._sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

    def _create_help(self):
        text = StaticText(self, label=get_help(self._title))
        text.SetFont(Font().help)
        self._sizer.Add(text, flag=wx.ALL, border=2)

    def _create_buttons(self):
        buttons = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        self._sizer.Add(buttons, 0, wx.ALIGN_CENTER|wx.ALL, 5)

    def get_value(self):
        return [ e.get_value() for e in self._editors ]

    def get_comment(self):
        return self._comment_editor.get_value()


class ScalarVariableDialog(_Dialog):

    def _get_editors(self, var):
        name = var.name if var and var.name else '${}'
        value = var.value[0] if var else ''
        validator = ScalarVariableNameValidator(self._controller, name)
        return [VariableNameEditor(self, name, 'Name', validator),
                ValueEditor(self, value, 'Value')]

class ListVariableDialog(_Dialog):

    def _get_editors(self, var):
        name = var.name if var and var.name else '@{}'
        value = var.value if var and var.value else ''
        validator = ListVariableNameValidator(self._controller, name)
        return [VariableNameEditor(self, name, 'Name', validator),
                ListValueEditor(self, value, 'Value')]


class LibraryDialog(_Dialog):

    def _get_editors(self, item):
        name = item and item.name or ''
        args = item and utils.join_value(item.args) or ''
        alias = item.alias if item else ''
        return [ValueEditor(self, name, 'Name'),
                ValueEditor(self, args, 'Args'),
                ValueEditor(self, alias, 'Alias')]

class VariablesDialog(LibraryDialog):

    def _get_editors(self, item):
        path = item and item.name or ''
        args = item and utils.join_value(item.args) or ''
        return [ValueEditor(self, path, 'Path'),
               ValueEditor(self, args, 'Args')]

class ResourceDialog(_Dialog):

    def _get_editors(self, item):
        name = item and item.name or ''
        return [ValueEditor(self, name, 'Path')]


class DocumentationDialog(_Dialog):

    def _get_editors(self, doc):
        return [MultiLineEditor(self, doc)]

    def _add_comment_editor(self, item):
        pass

    def get_value(self):
        return _Dialog.get_value(self)

    def get_comment(self):
        return ''


class _SettingDialog(_Dialog):
    _validator = None

    def _get_editors(self, item):
        editor = ValueEditor(self, item.value)
        if self._validator:
            editor.set_validator(self._validator())
        return [editor]


class ForceTagsDialog(_SettingDialog):
    pass

class DefaultTagsDialog(_SettingDialog):
    pass

class TagsDialog(_SettingDialog):
    pass


class _FixtureDialog(_SettingDialog):

    def _get_editors(self, item):
        return [ContentAssistEditor(self, item.value)]

class SuiteSetupDialog(_FixtureDialog): pass

class SuiteTeardownDialog(_FixtureDialog): pass

class TestSetupDialog(_FixtureDialog): pass

class TestTeardownDialog(_FixtureDialog): pass

class SetupDialog(_FixtureDialog): pass

class TeardownDialog(_FixtureDialog): pass


class TemplateDialog(_FixtureDialog): pass

class TestTemplateDialog(_FixtureDialog): pass


class ArgumentsDialog(_SettingDialog):
    _validator = ArgumentsValidator

class ReturnValueDialog(_SettingDialog):
    pass

class TestTimeoutDialog(_SettingDialog):
    _validator = TimeoutValidator

class TimeoutDialog(TestTimeoutDialog):
    pass


class MetadataDialog(_Dialog):

    def _get_editors(self, item):
        name, value = item and (item.name, item.value) or ('', '')
        return [ValueEditor(self, name, 'Name'),
                ValueEditor(self, value, 'Value')]


class TestCaseNameDialog(_Dialog):
    _title = 'New Test Case'

    def _add_comment_editor(self, item):
        pass

    def _get_editors(self, test):
        value = test.name if test else ''
        return [ValueEditor(self, value, 'Name',
                            TestCaseNameValidator(self._controller))]

    def get_name(self):
        return _Dialog.get_value(self)[0]


class CopyUserKeywordDialog(_Dialog):
    _title = 'Copy User Keyword'

    def _add_comment_editor(self, item):
        pass

    def _get_editors(self, uk):
        value = uk.name if uk else ''
        return [ValueEditor(self, value, 'Name',
                            UserKeywordNameValidator(self._controller))]

    def get_name(self):
        return _Dialog.get_value(self)[0]


class UserKeywordNameDialog(_Dialog):
    _title = 'New User Keyword'

    def _add_comment_editor(self, item):
        pass

    def _get_editors(self, uk):
        value = uk.name if uk else ''
        return [ValueEditor(self, value, 'Name',
                            UserKeywordNameValidator(self._controller)),
                ValueEditor(self, '', 'Arguments', ArgumentsValidator())]

    def get_name(self):
        return _Dialog.get_value(self)[0]

    def get_args(self):
        return _Dialog.get_value(self)[1]