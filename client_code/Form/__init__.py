from ._anvil_designer import FormTemplate
from anvil import *
import anvil.server

class Form(FormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.downloadMethod = 'url'
    self.url_radio.selected = True

    # Any code you write here will run before the form opens.

  def file_radio_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.downloadMethod = 'file'
    self.url_radio.selected = False

  def url_radio_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.downloadMethod = 'url'
    self.file_radio.selected = False
