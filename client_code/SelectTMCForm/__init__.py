from ._anvil_designer import SelectTMCFormTemplate
from anvil import *
import anvil.server


class SelectTMCForm(SelectTMCFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.config = properties['config']
    self.steppers = properties['steppers']

    self.tmc_options = anvil.server.call('get_tmc_options', self.config, self.steppers)

    for stepper, opts in self.tmc_options.items():
      if stepper not in self.steppers:
        continue
      panel = LinearPanel()
      self.linear_panel.add_component(panel)
      label = Label(text=f'Stepper "{stepper}"')
      label.bold = True
      panel.add_component(label)
      for key, value in opts.items():
        if 'tmc' in key:
          radio = RadioButton(selected=False, group_name=stepper, text=key)
          panel.add_component(radio)

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    selected_options = {}
    panels = self.linear_panel.get_components()
    for panel in panels:
      components = panel.get_components()
      stepper = components[0].text
      for component in components:
        if type(component) == RadioButton:
          if component.selected:
            selected_options[stepper] = component.text[9:-1]

    # Move to next form
