from sqlalchemy import Column, Integer, String, DateTime
from base import Base
class Stats(Base): 
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_phlevel_reading = Column(Integer, nullable=False)
    max_phlevel_reading = Column(Integer, nullable=False)
    max_water_level = Column(Integer, nullable=True)
    max_chlorine_level = Column(Integer, nullable=True)
    num_chlorine_level = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)




    def __init__(self, num_phlevel_reading, max_phlevel_reading,max_water_level, max_chlorine_level, num_chlorine_level,last_updated):
        """ Initializes a processing statistics objet """
        self.num_phlevel_reading = num_phlevel_reading
        self.max_phlevel_reading = max_phlevel_reading
        self.max_water_level = max_water_level
        self.max_chlorine_level = max_chlorine_level
        self.num_chlorine_level = num_chlorine_level
        self.last_updated = last_updated
        

    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_phlevel_reading'] = self.num_phlevel_reading
        dict['max_phlevel_reading'] = self.max_phlevel_reading
        dict['max_water_level'] = self.max_water_level
        dict['max_chlorine_level'] = self.max_chlorine_level
        dict['num_chlorine_level'] = self.num_chlorine_level
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f") 
        return dict
    
        