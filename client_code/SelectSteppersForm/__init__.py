from ._anvil_designer import SelectSteppersFormTemplate
from anvil import *
import anvil.server


class SelectSteppersForm(SelectSteppersFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.stepper_options = anvil.server.call('get_stepper_options', properties['config'])
    self.checkboxes = []
    
    for stepper in self.stepper_options:
      checkbox = CheckBox(checked=False, text=stepper)
      self.checkbox_panel.add_component(checkbox)
      self.checkboxes.append(checkbox)
      