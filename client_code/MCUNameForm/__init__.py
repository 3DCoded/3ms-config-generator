from ._anvil_designer import MCUNameFormTemplate
from anvil import *
import anvil.server
from anvil.js.window import navigator

class MCUNameForm(MCUNameFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.config = properties['config']
    self.steppers = properties['steppers']

  def generate_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    mcu_name = self.mcu_name_box.text.strip()
    cfg = anvil.server.call('generate_hardware_config', self.config, self.steppers, mcu_name)
    self.mmu_hardware_box.text = cfg
    self.mmu_hardware_box.visible = True
    try:
      navigator.clipboard.writeText(cfg)
      anvil.alert("mmu_hardware.cfg copied to clipboard.")
    except:
      pass