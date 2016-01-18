
class Nota:  
    def __init__(self, x, y, time, sprite, screen_width, screen_height, notetype):
      self.x = (x-256)*2.5
      self.y = y
      self.time = time
      self.sprite = sprite
      self.removed = False
      self.screen_width = screen_width
      self.screen_height = screen_height
      self.notetype = notetype
            
    # Essa funcao atualiza a pos da nota
    def update(self, songTime):  
      if self.notetype == 2:
		  self.sprite.rotateIncZ(0.4)
      self.y = ((self.time-songTime)-(self.screen_height/2))*1.3 + 326
      self.sprite.position(self.x, self.y, 5.0);

    # Essa funcao desenha as paradas
    def draw(self):
      if((self.time-songTime) > -(self.screen_height/2)):
        self.sprite.draw()
        
    def get_removed(self):
      return self.removed
      
    def set_removed(self):
      self.removed = True
      
    def outofscreen(self):
      if self.y < -self.screen_height/2:
        return True
      else:
        return False
