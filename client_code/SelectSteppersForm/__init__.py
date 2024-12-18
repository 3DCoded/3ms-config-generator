from ._anvil_designer import SelectSteppersFormTemplate
from anvil import *
import anvil.server


class SelectSteppersForm(SelectSteppersFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.config = properties['config']
    self.stepper_options = anvil.server.call('get_stepper_options', self.config)
    self.checkboxes = []
    
    for stepper in self.stepper_options:
      checkbox = CheckBox(checked=False, text=stepper)
      self.checkbox_panel.add_component(checkbox)
      self.checkboxes.append(checkbox)

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    steppers = {}
    for checkbox in self.checkboxes:
      if checkbox.checked:
        steppers[checkbox.text] = self.stepper_options[checkbox.text]
    anvil.open_form('SelectTMCForm', config=self.config, steppers=steppers)
      