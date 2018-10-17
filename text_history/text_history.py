class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._len = 0
        self._actions = []
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        raise AttributeError
    
    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        raise AttributeError

    def check_pos(self, pos, length=None):
        if pos is None:
            pos = self._len
        elif pos < 0 or self._len < pos:
            raise ValueError
        if length is not None and len(self._text[pos:pos+length]) < length:
            raise ValueError
        return pos
    
    def update(self, version=None):
        if version is None:
            self._version += 1
        else:
            self._version = version
        self._len = len(self._text)

    def check_action(self, action):
        if action.from_version != self._version and action.from_version == action.to_version:
            raise ValueError
    
    def make_action(self, method, pos, from_version, to_version=None, text=None, length=None):
        tree_action = {
            'Insert': InsertAction,
            'Replace': ReplaceAction,
            'Delete': DeleteAction
        }
        if to_version is None:
            to_version = from_version + 1
        if method == 'Delete':
            action = tree_action[method](pos, length, from_version, to_version)
        else:
            action = tree_action[method](pos, text, from_version, to_version)
        return action
    
    def check_version(self, from_version, to_version):
        if from_version and from_version >= to_version:
            return 0
        elif from_version < 0 or to_version > self._version:
            return 0
        return 1 

    def insert(self, text, pos=None, version=None):
        pos = self.check_pos(pos)
        action = self.make_action('Insert', pos, self._version, text=text, to_version=version)
        return self.action(action)
        
    def replace(self, text, pos=None, version=None):
        pos = self.check_pos(pos)
        action = self.make_action('Replace', pos, self._version, text=text, to_version=version)
        return self.action(action)
    
    def delete(self, pos, length, version=None):
        pos = self.check_pos(pos, length=length)
        action = self.make_action('Delete', pos, self._version, length=length, to_version=version)
        return self.action(action)

    def action(self, action:'Action'):
        self.check_action(action)
        self._text = action.apply(self.text)
        self._actions.append(action)
        self.update(action.to_version)
        return self._version
    
    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self._version
        if not self.check_version(from_version, to_version):
            raise ValueError
        return self._actions[from_version:to_version]


class Action:
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, text:str):
        pass


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, text):
        new_text = text[:self.pos] + self.text + text[self.pos:]
        return new_text


class ReplaceAction(InsertAction):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, text, from_version, to_version)

    def apply(self, text):
        place = self.pos + len(self.text)
        new_text = text[:self.pos] + self.text + text[place:]
        return new_text


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def apply(self, text):
        new_text = text[:self.pos] + text[self.pos + self.length:]
        return new_text
