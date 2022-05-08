class Catalog:
  def __init__(self, id, name, base_path):
    self.id        = id
    self.name      = name
    self.base_path = base_path

  def __str__(self):
    return '%s (%s)' % (self.name, self.base_path)