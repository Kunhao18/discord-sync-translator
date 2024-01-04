import yaml
import discord
from discord import app_commands

from manager import TransChannelManager
from backend import DetectorBackend, TranslatorBackend

def role_check(role_id: int):
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.get_role(role_id) is not None
    return app_commands.check(predicate)


def admin_check():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.administrator
    return app_commands.check(predicate)


def get_lang_note_dict(lang_dict, need_detector=True):
    lang_dict_translator = {}
    lang_dict_detector = {}
    lang_dict_emoji = {}
    for language in lang_dict.keys():
        if need_detector:
            assert "detector_note" in lang_dict[language].keys(), f"Lack detector note for language {language}"
            lang_dict_detector[language] = lang_dict[language]["detector_note"]
        lang_dict_translator[language] = lang_dict[language]["translator_note"]
        lang_dict_emoji[language] = lang_dict[language]["emoji_note"]
    return lang_dict_detector, lang_dict_translator, lang_dict_emoji


# Instantiate Global
intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

with open('./config/general.yaml', 'r') as f_in:
    params = yaml.safe_load(f_in)

with open('./config/language.yaml', 'r') as f_in:
    language_config = yaml.safe_load(f_in)
lang_dict_detector, lang_dict_translator, lang_dict_emoji = get_lang_note_dict(language_config, params['need_detector'])

# global variables
bot_token = params['bot_token']
guild_id = params['guild_id']
webhook_name = params['webhook_name']

# instantiate objects
ch_manager = TransChannelManager(params['translate_data_path'])
translator_backend = TranslatorBackend(lang_dict_translator)
detector_backend = DetectorBackend(lang_dict_detector) if params['need_detector'] else None
