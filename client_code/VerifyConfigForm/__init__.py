from ._anvil_designer import VerifyConfigFormTemplate
from anvil import *
import anvil.server


class VerifyConfigForm(VerifyConfigFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.first_lines = '\n'.join(properties['config'].splitlines()[:3])
    self.config_text_area.text = '\n'.join(properties['config'].splitlines()[3:])

  def verify_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    success, error = anvil.server.call('check_parsing', self.config_text_area.text)
    if success:
      self.error_label.text = "This configuration contains no errors."
      self.error_label.foreground = '#00aa00'
      self.submit_button.enabled = True
    else:
      self.submit_button.enabled = False
      self.error_label.text = error
      self.error_label.foreground = '#ff0000'

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.open_form('SelectSteppersForm', config=self.first_lines + '\n' + self.config_text_area.text)

    