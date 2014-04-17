import lib.vmflib.types as types

from lib.vmflib.vmf import Entity

RGB = types.RGB
vector = types.Vector

# An implementation of the lightinfo entity for vmflib

class Dota_lightinfo_entity(Entity):
    def __init__(self):
        Entity.__init__(self, "ent_dota_lightinfo")
        
        self.auto_properties = ['classname', 'origin', 'targetname',
                                
                                # All the values found in the dota2.fgd file at https://github.com/dota2modders/dota2fgd/blob/master/dota2.fgd
                                'color_day', 'color_dusk', 'color_night', 'color_dawn', 
                                'ambient_color_day', 'ambient_color_dusk', 'ambient_color_night', 'ambient_color_dawn', 
                                'ambient_scale_day', 'ambient_scale_dusk', 'ambient_scale_night', 'ambient_scale_dawn', 
                                
                                'shadow_color_day', 'shadow_color_dusk', 'shadow_color_night', 'shadow_color_dawn', 
                                'shadow_scale_day', 'shadow_scale_dusk', 'shadow_scale_night', 'shadow_scale_dawn', 
                                'shadow_ground_scale_day', 'shadow_ground_scale_dusk', 'shadow_ground_scale_night', 'shadow_ground_scale_dawn', 
                                
                                'specular_color_day', 'specular_color_dusk', 'specular_color_night', 'specular_color_dawn', 
                                'light_direction_day', 'light_direction_dusk', 'light_direction_night', 'light_direction_dawn', 
                                'ambient_direction_day', 'ambient_direction_dusk', 'ambient_direction_night', 'ambient_direction_dawn', 
                                
                                'fog_color_day', 'fog_color_dusk', 'fog_color_night', 'fog_color_dawn', 
                                'fog_start_day', 'fog_start_dusk', 'fog_start_night', 'fog_start_dawn', 
                                'fog_end_day', 'fog_end_dusk', 'fog_end_night', 'fog_end_dawn'
                                
                                'inner_radius', 'outer_radius']
        
        self.classname = class_name
        self.origin = None
        self.targetname = None
        
        self.color_day = RGB(0,0,0)
        self.color_dusk = RGB(0,0,0)
        self.color_night = RGB(0,0,0)
        self.color_dawn = RGB(0,0,0)
        
        self.ambient_color_day = RGB(0,0,0)
        self.ambient_color_dusk = RGB(0,0,0)
        self.ambient_color_night = RGB(0,0,0)
        self.ambient_color_dawn = RGB(0,0,0)
        
        self.ambient_scale_day = 0.0
        self.ambient_scale_dusk = 0.0
        self.ambient_scale_night = 0.0
        self.ambient_scale_dawn = 0.0
        
        self.shadow_color_day = RGB(0,0,0)
        self.shadow_color_dusk = RGB(0,0,0)
        self.shadow_color_night = RGB(0,0,0)
        self.shadow_color_dawn = RGB(0,0,0)
        
        self.shadow_scale_day = 0.0
        self.shadow_scale_dusk = 0.0
        self.shadow_scale_night = 0.0
        self.shadow_scale_dawn = 0.0
        
        self.shadow_ground_scale_day = 0.0
        self.shadow_ground_scale_dusk = 0.0
        self.shadow_ground_scale_night = 0.0
        self.shadow_ground_scale_dawn = 0.0
        
        self.specular_color_day = RGB(0,0,0)
        self.specular_color_dusk = RGB(0,0,0)
        self.specular_color_night = RGB(0,0,0)
        self.specular_color_dawn = RGB(0,0,0)
        
        self.light_direction_day = Vector(0,0,0)
        self.light_direction_dusk = Vector(0,0,0)
        self.light_direction_night = Vector(0,0,0)
        self.light_direction_dawn = Vector(0,0,0)
        
        self.ambient_direction_day = Vector(0,0,0)
        self.ambient_direction_dusk = Vector(0,0,0)
        self.ambient_direction_night = Vector(0,0,0)
        self.ambient_direction_dawn = Vector(0,0,0)
        
        self.fog_color_day = RGB(0,0,0)
        self.fog_color_dusk = RGB(0,0,0)
        self.fog_color_night = RGB(0,0,0)
        self.fog_color_dawn = RGB(0,0,0)
        
        self.fog_start_day = 0.0
        self.fog_start_dusk = 0.0
        self.fog_start_night = 0.0
        self.fog_start_dawn = 0.0
        
        self.fog_end_day = 0.0
        self.fog_end_dusk = 0.0
        self.fog_end_night = 0.0
        self.fog_end_dawn = 0.0
        
        self.inner_radius = 0.0
        self.outer_radius = 0.0
        

        p = self.properties
        p['id'] = Entity.entitycount
        Entity.entitycount += 1            # Increment entity counter