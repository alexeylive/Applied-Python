class Action:
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, input):
        raise NotImplementedError("Необходимо переопределить метод")


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, input):
        return input[:self.pos] + str(self.text) + input[self.pos:]


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def apply(self, input):
        return input[:self.pos] + str(self.text) + input[self.pos + len(str(self.text)):]


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def apply(self, input):
        return input[:self.pos] + input[self.pos + self.length:]


class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._action_list = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def _changes(self,action):
        self._text = action.apply(self._text)
        self._version = action.to_version
        self._action_list.append(action)
        return self.version

    def insert(self, line, pos=None):
        if pos is None or (pos == 0 and len(self._text) == 0):
            pos = len(self._text)

        elif pos >= len(self._text) or pos < 0:
            raise ValueError

        action = InsertAction(pos, line, self._version, self._version + 1)
        return self._changes(action)

    def replace(self, line, pos=None):
        if pos is None:
            pos = len(self._text)

        elif pos < 0 or pos > len(self._text):
            raise ValueError

        action = ReplaceAction(pos, line, self._version, self._version + 1)
        return self._changes(action)

    def delete(self, pos, length):
        if pos + length > len(self._text) or pos < 0 or length < 0:
            raise ValueError

        action = DeleteAction(pos, length, self._version, self._version + 1)
        return self._changes(action)

    def action(self, action):
        if action.from_version > action.to_version or action.from_version != self._version or \
                action.from_version < 0 or action.from_version == action.to_version:
            raise ValueError

        return self._changes(action)

    def _optimize_before_insert(self,action1,action2):
        if isinstance(action1,InsertAction) and isinstance(action2,InsertAction) and \
                action1.pos == action2.pos:
            action1.text = action2.text + action1.text
            action1.to_version = action2.to_version

    def _optimize_after_insert(self,action1,action2):
        if isinstance(action1,InsertAction) and isinstance(action2,InsertAction) and \
                action2.pos == action1.pos + len(action1.text):
            action1.text = action1.text + action2.text
            action1.to_version = action2.to_version

    def _optimize_del(self,action1,action2):
        if isinstance(action1, DeleteAction) and isinstance(action2, DeleteAction) and \
                action2.pos == action1.pos:
            action1.length = action1.length + action2.length
            action1.to_version = action2.to_version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            to_version = self.version

        if from_version > to_version or from_version < 0 or to_version > self.version:
            raise ValueError

        if from_version == to_version:
            return []

        list = []
        vers = from_version
        for action in self._action_list:
            if action.from_version == vers:

                if len(list) != 0:
                    self._optimize_before_insert(list[len(list) - 1],action)
                    self._optimize_after_insert(list[len(list) - 1],action)
                    self._optimize_del(list[len(list) - 1],action)

                if len(list) == 0 or list[len(list) - 1].to_version != action.to_version:
                    list.append(action)

                vers = action.to_version

            if vers == to_version:
                break

        if vers != to_version:
            raise ValueError

        return list
