import obspython as obs

class Main:
    name = 'OBSbounce'
    description = 'Make sources bounce around your screen'

    inputs = {
        'enabled': 'checkbox',
        'source': 'text',
        'outputWidth': 'int',
        'outputHeight': 'int',
        'vx': 'float',
        'vy': 'float'
    }

    lastInstNo = 0
    instances = {}

    def __init__(self, inputs):
        Main.lastInstNo += 1
        self.instNo = Main.lastInstNo
        Main.instances[self.instNo] = self
        self.data = inputs
        self.vxi = 1
        self.vyi = 1
        self.update('source')

    def destroy(self):
        del Main.instances[self.instNo]

    def update(self, input):
        if (input == 'source'):
            self.sceneitem = get_sceneitem_from_source_name_in_current_scene(self.data['source'])
            if self.sceneitem:
                self.source = obs.obs_sceneitem_get_source(self.sceneitem)
            else:
                self.source = None

    def tick(self, dt):
        move_source(self, dt)


def get_sceneitem_from_source_name_in_current_scene(name):
    result_sceneitem = None
    current_scene_as_source = obs.obs_frontend_get_current_scene()
    if current_scene_as_source:
        current_scene = obs.obs_scene_from_source(current_scene_as_source)
        result_sceneitem = obs.obs_scene_find_source_recursive(current_scene, name)
        obs.obs_source_release(current_scene_as_source)
    return result_sceneitem

def move_source(inst, dt):
    if not (inst.sceneitem and inst.data['enabled']):
        return

    pos = obs.vec2()
    scale = obs.vec2()
    obs.obs_sceneitem_get_pos(inst.sceneitem, pos)
    obs.obs_sceneitem_get_scale(inst.sceneitem, scale)
    width, height = obs.obs_source_get_width(inst.source), obs.obs_source_get_height(inst.source)

    if pos.x <= 0:
        inst.vxi = 1
    elif pos.x + width * scale.x >= inst.data['outputWidth']:
        inst.vxi = -1
    if pos.y <= 0:
        inst.vyi = 1
    elif pos.y + height * scale.y >= inst.data['outputHeight']:
        inst.vyi = -1

    pos.x += inst.data['vx'] * inst.vxi * dt
    pos.y += inst.data['vy'] * inst.vyi * dt

    obs.obs_sceneitem_set_pos(inst.sceneitem, pos)