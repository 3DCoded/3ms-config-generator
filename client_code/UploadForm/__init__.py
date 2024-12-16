from ._anvil_designer import UploadFormTemplate
from anvil import *
import anvil.server

class UploadForm(UploadFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.uploadMethod = 'url'

    # Any code you write here will run before the form opens.

  def file_radio_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.uploadMethod = 'file'
    self.url_radio.selected = False
    self.file_box.visible = True
    self.url_box.visible = False

  def url_radio_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    self.uploadMethod = 'url'
    self.file_radio.selected = False
    self.url_box.visible = True
    self.file_box.visible = False

  def upload_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.server.call("say_hello", 'bob')

  
