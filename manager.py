import os
import json


class TransChannelManager:
    def __init__(self, config_path):
        self._channel_dict = {}
        self._group_dict = {}
        self._config_path = config_path
        self.load_config()

    @property
    def channel_dict(self):
        return self._channel_dict

    @property
    def group_dict(self):
        return self._group_dict

    def load_config(self):
        try:
            with open(self._config_path, "r") as f_in:
                config_data = json.load(f_in)
            self._channel_dict = config_data['channels']
            self._group_dict = config_data['groups']
        except Exception as e:
            print(f'Load Trans Config Failed: {e}')
            print('Remaking Config...')
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            self.save_config()

    def save_config(self):
        write_dict = {'channels': self._channel_dict,
                      'groups': self._group_dict}
        with open(self._config_path, "w") as f_out:
            json.dump(write_dict, f_out, indent=2)
    
    def bind_channel(self, channel_id, group_name, language):
        try:
            if channel_id in self._channel_dict.keys():
                return "**[FAIL]** Channel already bound."
            if group_name not in self._group_dict.keys():
                return "**[FAIL]** Group doesn't exist."
            if language in self._group_dict[group_name].keys():
                return "**[FAIL]** Group already has a channel of the selected language."
            self._channel_dict[channel_id] = group_name
            self._group_dict[group_name][language] = channel_id
            self.save_config()
            return "**[OK]** Channel bound."
        except Exception as e:
            return "**[FAIL]** Operating error."

    def unbind_channel(self, channel_id):
        try:
            group_name = self._channel_dict.pop(channel_id)
            for k, v in self._group_dict[group_name].items():
                if v == channel_id:
                    self._group_dict[group_name].pop(k)
                    break
            self.save_config()
            return "**[OK]** Channel unbound."
        except Exception as e:
            return "**[FAIL]** Operating error."

    def change_channel(self, channel_id, new_group, language):
        try:
            if channel_id not in self._channel_dict.keys():
                return "**[FAIL]** Channel isn't bound."
            if new_group not in self._group_dict.keys():
                return "**[FAIL]** Group doesn't exist."
            if language in self._group_dict[new_group].keys():
                return "**[FAIL]** Group already has a channel of the selected language."
            self.unbind_channel(channel_id)
            self._channel_dict[channel_id] = new_group
            self._group_dict[new_group][language] = channel_id
            self.save_config()
            return "**[OK]** Channel changed."
        except Exception as e:
            return "**[FAIL]** Operating error."

    def create_group(self, group_name):
        if group_name in self._group_dict.keys():
            return "**[FAIL]** New name already existed."
        else:
            try:
                self._group_dict[group_name] = {}
                self.save_config()
                return f"**[OK]** Group {group_name} created."
            except Exception as e:
                print(e)
                return "**[FAIL]** Operating error."

    def delete_group(self, group_name):
        if group_name not in self._group_dict.keys():
            return "**[FAIL]** Selected group doesn't exist."
        else:
            try:
                num_elem = 0
                tmp_dict = self._group_dict.pop(group_name)
                for k, v in tmp_dict.items():
                    num_elem += 1
                    self._channel_dict.pop(v)
                self.save_config()
                return f"**[OK]** Group {group_name} deleted. {num_elem} channels unbound."
            except Exception as e:
                return "**[FAIL]** Operating error."

    def rename_group(self, group_name, new_name):
        if group_name not in self._group_dict.keys():
            return "**[FAIL]** Selected group doesn't exist."
        elif new_name in self._group_dict.keys():
            return "**[FAIL]** New name already existed."
        else:
            try:
                self._group_dict[new_name] = {}
                tmp_dict = self._group_dict.pop(group_name)
                for k, v in tmp_dict.items():
                    self._channel_dict[v] = new_name
                    self._group_dict[new_name][k] = v
                self.save_config()
                return f"**[OK]** Group {group_name} has been changed to {new_name}."
            except Exception as e:
                return "**[FAIL]** Operating error."

    def check_group(self) -> (str, dict):
        if not self._group_dict:
            return "**[FAIL]** There is no group.", {}
        try:
            full_info = "**[OK]** Current group information:"
            return full_info, self._group_dict
        except Exception as e:
            return "**[FAIL]** Operating error.", {}
