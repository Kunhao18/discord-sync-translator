import discord
from discord.ui import View

from utils import lang_dict_translator


class ChannelBindView(View):
    def __init__(self, channel, channel_id, group_name, ch_manager,
                 webhook_name="ShadowTrans", timeout=60):
        super().__init__(timeout=timeout)

        self._children_dict = {}
        self._save_children()

        self._webhook_name = webhook_name
        self._channel = channel
        self._channel_id = channel_id
        self._group_name = group_name
        self._ch_manager = ch_manager

    def _save_children(self):
        for child in self.children:
            self._children_dict[child.custom_id] = child
    
    @discord.ui.select(placeholder="Select a language.",
                       custom_id="lang_sel",
                       row=1,
                       options=[discord.SelectOption(label=lang, value=lang) for lang in lang_dict_translator.keys()])
    async def lang_select_callback(self, interaction, select):
        await interaction.response.defer()

    @discord.ui.button(label="BIND", style=discord.ButtonStyle.green, custom_id="bind_button", row=2)
    async def bind_button_callback(self, interaction, button):
        if not self._children_dict["lang_sel"].values:
            await interaction.response.defer()
        else:
            lang_value = self._children_dict["lang_sel"].values[0]
            await interaction.response.edit_message(content="Processing...", view=None, delete_after=3)

            bind_result = self._ch_manager.bind_channel(self._channel_id, self._group_name, lang_value)
            try:
                if bind_result.startswith("**[OK]**"):
                    has_hook = False
                    webhooks = await self._channel.webhooks()
                    for webhook in webhooks:
                        if webhook.name == self._webhook_name:
                            has_hook = True
                            break
                    if not has_hook:
                        await self._channel.create_webhook(name=self._webhook_name)
            except Exception as e:
                bind_result = "**[FAIL]** Webhook creation failed."
            await interaction.followup.send(bind_result, ephemeral=True)


class ChannelChangeView(View):
    def __init__(self, channel_id, new_group, ch_manager, timeout=60):
        super().__init__(timeout=timeout)
        self._children_dict = {}
        self._save_children()

        self._channel_id = channel_id
        self._new_group = new_group
        self._ch_manager = ch_manager

    def _save_children(self):
        for child in self.children:
            self._children_dict[child.custom_id] = child
    
    @discord.ui.select(placeholder="Select a language.",
                       custom_id="lang_sel",
                       row=1,
                       options=[discord.SelectOption(label=lang, value=lang) for lang in lang_dict_translator.keys()])
    async def lang_select_callback(self, interaction, select):
        await interaction.response.defer()

    @discord.ui.button(label="CHANGE", style=discord.ButtonStyle.green, custom_id="change_button", row=2)
    async def bind_button_callback(self, interaction, button):
        if not self._children_dict["lang_sel"].values:
            await interaction.response.defer()
        else:
            lang_value = self._children_dict["lang_sel"].values[0]
            await interaction.response.edit_message(content="Processing...", view=None, delete_after=3)

            change_result = self._ch_manager.change_channel(self._channel_id, self._new_group, lang_value)
            await interaction.followup.send(change_result, ephemeral=True)
